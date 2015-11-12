import pytest

from .. import Shuttle
from ..cache import Cache, PackageNotCompatibleException
from ..package_stub import PackageStub


def test_update(tmp_path):
    s = Shuttle('test', '1.0.0')
    cache = Cache(tmp_path, s=s)
    package = PackageStub({'name': 'abc', 'version': '1.0.0'}, s=s)

    meta = {
        'archive': ['archive.gz', None],
        'package': package.to_dict()
    }

    assert len(cache.list()) == 0

    cache.update(meta, None)

    assert len(cache.list()) == 1
    assert cache.list()[0].ident == package.ident

    assert cache.get('abc >=1.0.1') is None
    assert cache.get('abc').ident == package.ident
    assert cache.get('abc ==1.0.0').ident == package.ident
    assert cache.get('abc >0.0.1').ident == package.ident

    assert cache.get('xyz') is None


def test_update_compatible(tmp_path):
    s = Shuttle('test', '1.0.0')
    cache = Cache(tmp_path, s=s)
    package = PackageStub({
        'name': 'abc',
        'version': '1.0.0',
        'compatibility': {
            'test': '>=0.9.0'
        }
    }, s=s)

    meta = {
        'archive': ['archive.gz', None],
        'package': package.to_dict()
    }

    assert len(cache.list()) == 0

    cache.update(meta, None)

    assert len(cache.list()) == 1

    assert cache.get('abc >=1.0.1') is None
    assert cache.get('abc').ident == package.ident
    assert cache.get('abc ==1.0.0').ident == package.ident
    assert cache.get('abc >0.0.1').ident == package.ident

    assert cache.get('xyz') is None


def test_update_incompatible(tmp_path):
    s = Shuttle('test', '1.0.0')
    cache = Cache(tmp_path, s=s)
    package = PackageStub({
        'name': 'abc',
        'version': '1.0.0',
        'compatibility': {
            'test': '>=2.0.0'
        }
    }, s=s)

    meta = {
        'archive': ['archive.gz', None],
        'package': package.to_dict()
    }

    assert len(cache.list()) == 0

    cache.update(meta, None)

    assert len(cache.list()) == 0

    with pytest.raises(PackageNotCompatibleException):
        cache.get('abc')
        cache.get('abc >=0.0.0')

    assert cache.get('xyz') is None


def test_update_multiple_compatible(tmp_path):
    s = Shuttle('test', '5.0.0')
    cache = Cache(tmp_path, s=s)

    for i in range(1, 11):
        package = PackageStub({
            'name': 'abc',
            'version': '%d.0.0' % i,  # from 1.0.0 to 10.0.0
            'compatibility': {
                'test': '>=%d.0.0' % i  # from 1.0.0 to 10.0.0
            }
        }, s=s)

        meta = {
            'archive': ['archive.gz', None],
            'package': package.to_dict()
        }

        cache.update(meta, None)

    assert len(cache.list()) == 5
    assert cache.get('abc').version == '5.0.0'

    assert cache.get('xyz') is None


def test_update_multiple_incompatible(tmp_path):
    s = Shuttle('test', '0.0.0')
    cache = Cache(tmp_path, s=s)

    for i in range(1, 11):
        package = PackageStub({
            'name': 'abc',
            'version': '%d.0.0' % i,  # from 1.0.0 to 10.0.0
            'compatibility': {
                'test': '>=%d.0.0' % i  # from 1.0.0 to 10.0.0
            }
        }, s=s)

        meta = {
            'archive': ['archive.gz', None],
            'package': package.to_dict()
        }

        cache.update(meta, None)

    assert len(cache.list()) == 0

    with pytest.raises(PackageNotCompatibleException):
        cache.get('abc')
        cache.get('abc >=0.0.0')

    assert cache.get('xyz') is None