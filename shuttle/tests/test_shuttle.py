import os
import sys
from .. import Shuttle


def test_build_install_remove(sample_package_path, tmp_path):
    s = Shuttle('test', '1.0')
    command = s.make_command(data_path=tmp_path)

    archive = command.build(sample_package_path)
    assert os.path.isfile(archive.path)

    packages = command.list()
    assert len(packages) == 0

    package = command.install(archive.path)
    assert os.path.isdir(package.path)

    packages = command.list(package.package_name())
    assert packages[0].package_name() == package.package_name()

    command.remove(package.package_name())
    assert not os.path.isdir(package.path)

    packages = command.list()
    assert len(packages) == 0
