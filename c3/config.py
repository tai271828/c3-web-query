"""
Global config singlet.
"""
import pkg_resources
import logging
import c3.maptable
from configparser import ConfigParser

logger = logging.getLogger('c3_web_query')

resource_package = __name__
resource_path = '/'.join(('data', 'default.ini'))

template = pkg_resources.resource_stream(resource_package, resource_path)


class Configuration(object):
    __instance = None

    def __init__(self):
        self.config = None

    @classmethod
    def get_instance(cls):
        if not cls.__instance:
            cls.__instance = Configuration()
        return cls.__instance

    def read_configuration(self, conf_file=None):
        """
        Read the initialization configuration file.

        The function will try to read the user specified configuration file
        first, and fall back expected values to default.ini if they are not
        found.

        All the read values will be then overridden by the special
        environmental variables if this function is invoked by c3_cli:main.

        :param conf_file: user specified configuration file.
        :return: configuration object
        """
        config = ConfigParser()
        config_default = ConfigParser()
        config_default.read(template.name)

        if conf_file:
            logger.debug('Reading conf...')
            logger.debug('Found %s' % conf_file)
            config.read(conf_file)

        try:
            if conf_file and config['C3']['UserName']:
                logger.debug('Override C3USERNAME by the given conf file.')
                logger.debug('It is %s ' % config['C3']['UserName'])
        except KeyError:
            # fallback value
            config['C3']['UserName'] = config_default['C3']['UserName']
            logger.debug('No given C3 Username. Use default.ini ')

        try:
            if conf_file and config['C3']['APIKey']:
                logger.debug('Override C3APIKEY by the given conf file.')
        except KeyError:
            # fallback value
            config['C3']['APIKey'] = config_default['C3']['APIKey']
            logger.debug('No given C3 API key. Use default.ini')

        try:
            if conf_file and config['GENERAL']['verbose']:
                logger.debug('Override verbose by the given conf file.')
        except KeyError:
            # fallback value
            config['GENERAL']['verbose'] = config_default['GENERAL']['verbose']
            logger.debug('No given verbose. Use default.ini')

        try:
            if conf_file and config['SHRINK']['all']:
                logger.debug('Override shrink flag by the given conf file')
        except KeyError:
            # fallback value
            config['SHRINK']['all'] = config_default['SHRINK']['all']
            logger.debug('No given shrink flag. Use default.ini')

        self.config = config


def set_logger_verbose_level(verbose_level, logger):
    vl = c3.maptable.loglevel[verbose_level]
    logger.setLevel(vl)
