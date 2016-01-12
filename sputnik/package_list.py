import os
import logging
import shutil

import semver

from . import util
from . import default
from .package_string import PackageString
from .package_stub import PackageStub


class CompatiblePackageNotFoundException(Exception): pass
class PackageNotFoundException(Exception): pass
class InvalidDataPathException(Exception): pass


class PackageList(object):

    package_class = PackageStub

    def __init__(self, app_name, app_version, path, **kwargs):
        super(PackageList, self).__init__()

        self.logger = logging.getLogger(__name__)

        self.app_name = app_name
        self.app_version = app_version

        self.path = path
        self.data_path = kwargs.get('data_path') or path

        if not self.data_path:
            raise InvalidDataPathException(self.data_path)

        self.load()

    def packages(self):
        if not os.path.exists(self.path):
            os.mkdir(self.path)

        for path in os.listdir(self.path):
            if path.endswith('.tmp'):
                continue

            meta_path = os.path.join(self.path, path, default.META_FILENAME)
            if not os.path.isfile(meta_path):
                continue

            yield self.__class__.package_class(path=os.path.join(self.path, path))

    def load(self):
        self._packages = {}
        for package in self.packages():
            self._packages[package.ident] = package

    def get(self, package_string):
        candidates = []
        query = PackageString(package_string)

        for package in self._packages.values():
            ps = PackageString(package=package)
            if query.match(ps):
                candidates.append(ps)

        if not candidates:
            raise PackageNotFoundException(package_string)

        candidates.sort(key=lambda c: (self.is_compatible(c.package), c))
        package = candidates[-1].package

        if not self.is_compatible(package):
            raise CompatiblePackageNotFoundException(
                'running %s %s but requires %s' %
                (self.app_name, self.app_version, package.compatibility))

        return package

    def list(self, package_string=None, check_compatibility=True):
        def c(value):
            if check_compatibility:
                return value
            return True

        if not package_string:
            return [p for p in self._packages.values() if c(self.is_compatible(p))]

        candidates = []
        query = PackageString(package_string)

        for package in self._packages.values():
            ps = PackageString(package=package)
            if query.match(ps) and c(self.is_compatible(ps.package)):
                candidates.append(ps.package)

        return candidates

    def list_all(self, package_string=None):
        return self.list(package_string, check_compatibility=False)

    def purge(self):
        self.logger.info('purging %s', self.__class__.__name__)
        for package in self.list():
            self.remove(package)

    def is_compatible(self, package):
        if self.app_name and package.compatibility:
            compatible_version = package.compatibility.get(self.app_name)
            if not compatible_version:
                return False

            if self.app_version:
                return semver.match(self.app_version, compatible_version)

            return False
        return True

    def remove(self, package):
        if not os.path.isdir(package.path):
            raise Exception("not installed")

        # cleanup remove
        if os.path.exists(package.path):
            self.logger.info('pending remove %s', package.path)
            tmp = package.path + '.tmp'
            shutil.move(package.path, tmp)
            self.logger.info('remove %s', package.path)
            shutil.rmtree(tmp)

        self.load()
