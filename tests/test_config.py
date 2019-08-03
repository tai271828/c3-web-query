"""
Test configuration parser

Usage: project_root> pytest

"""
import pytest


@pytest.fixture
def config_singlet():
    """
    Read the default.ini and return config singlet.

    :return: configuration singlet instance.
    """
    import pkg_resources
    import c3.config

    resource_package = __name__
    resource_path = '/'.join(('../c3/data', 'default.ini'))

    template = pkg_resources.resource_stream(resource_package, resource_path)

    config_singlet = c3.config.Configuration()
    config_singlet.read_configuration(template.name)
    return config_singlet


def test_read_default_username(config_singlet):
    assert config_singlet.config['C3']['UserName'] == 'ubuntu'

def test_read_default_apikey(config_singlet):
    assert config_singlet.config['C3']['APIKey'] == 'ubuntu'

def test_read_default_batch_query_mode(config_singlet):
    assert config_singlet.config['C3']['BatchQueryMode'] == '0'

def test_read_default_uri(config_singlet):
    answer_uri = 'https://certification.canonical.com'
    assert config_singlet.config['C3']['URI'] == answer_uri

def test_read_default_verbose(config_singlet):
    answer = 'info'
    assert config_singlet.config['GENERAL']['verbose'] == answer

def test_read_default_cache(config_singlet):
    answer = 'true'
    assert config_singlet.config['GENERAL']['cache'] == answer
