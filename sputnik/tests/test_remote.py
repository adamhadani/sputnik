import os

import pytest


repository_url = os.environ.get('REPOSITORY_URL', 'https://index-staging.spacy.io')


@pytest.mark.remote
def test_upload_package(command, sample_package_path, tmp_path):
    archive = command.build(sample_package_path)
    assert os.path.isfile(archive.path)

    res = command.upload(archive.path, data_path=tmp_path, repository_url=repository_url)
    assert res


@pytest.mark.remote
def test_upload_package2(command, sample_package_path2, tmp_path):
    archive = command.build(sample_package_path2)
    assert os.path.isfile(archive.path)

    res = command.upload(archive.path, data_path=tmp_path, repository_url=repository_url)
    assert res


@pytest.mark.remote
def test_install_package(command, tmp_path):
    packages = command.list(data_path=tmp_path)
    assert len(packages) == 0

    package = command.install('test', data_path=tmp_path, repository_url=repository_url)
    assert os.path.isdir(package.path)

    packages = command.list(data_path=tmp_path)
    assert len(packages) == 1
    assert packages[0].ident == package.ident


@pytest.mark.remote
def test_upgrade_package(command, tmp_path):
    packages = command.list(data_path=tmp_path)
    assert len(packages) == 0

    package1 = command.install('test ==1.0.0', data_path=tmp_path, repository_url=repository_url)
    assert os.path.isdir(package1.path)

    packages = command.list(data_path=tmp_path)
    assert len(packages) == 1
    assert packages[0].ident == package1.ident

    package2 = command.install('test ==2.0.0', data_path=tmp_path, repository_url=repository_url)
    assert os.path.isdir(package2.path)

    packages = command.list(data_path=tmp_path)
    assert len(packages) == 1
    assert packages[0].ident == package2.ident


@pytest.mark.remote
def test_search_packages(command, tmp_path):
    assert command.search(data_path=tmp_path, repository_url=repository_url)
