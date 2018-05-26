"""
Test configuration parser

Usage: project_root> pytest

"""
import c3.config
import pkg_resources

resource_package = __name__
resource_path = '/'.join(('../c3/data', 'default.ini'))

template = pkg_resources.resource_stream(resource_package, resource_path)


def read_default():
    config_singlet = c3.config.Configuration()
    config_singlet.read_configuration(template.name)
    return config_singlet


def test_read_default():
    config_singlet = read_default()

    assert config_singlet.config['C3']['UserName'] == 'ubuntu'
