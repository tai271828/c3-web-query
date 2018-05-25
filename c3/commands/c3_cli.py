import os
import click
import logging
import c3.config as c3config
import c3.api.api as c3api
from c3.api.api_utils import APIQuery
from c3.commands.pool import commands as group_batch
from c3.commands.single import commands as group_single


logger = logging.getLogger('c3_web_query')


@click.group()
@click.option('--c3username',
              default=lambda: os.environ.get('C3USERNAME', ''),
              help='Your C3 username')
@click.option('--c3apikey',
              default=lambda: os.environ.get('C3APIKEY', ''),
              help='Your C3 API KEY')
@click.option('--verbose', default=0,
              help='Verbose level, the lower the fewer message output.')
@click.option('--conf',
              help='Configuration file.')
def main(c3username, c3apikey, verbose, conf):
    # TODO: how do i pass these global conf var
    # configuration singlet initialization
    configuration = c3config.Configuration.get_instance()
    configuration.read_configuration(conf)
    # default value from the configuration file
    # fallback order: env var > customized conf > default.ini
    if c3username:
        configuration.config['C3']['UserName'] = c3username
    else:
        c3username = configuration.config['C3']['UserName']

    if c3apikey:
        configuration.config['C3']['APIKey'] = c3apikey
    else:
        c3apikey = configuration.config['C3']['APIKey']

    c3url = configuration.config['C3']['URI']
    api = APIQuery(c3url)

    request_params = {"username": c3username,
                      "api_key": c3apikey}

    api_instance = c3api.API.get_instance()
    api_instance.set_api_params(api, request_params)

    try:
        verbose = configuration.config['GENERAL']['Verbose']
    except KeyError:
        logger.warning('Fallback to default verbose value.')

    logging.info('Configuration:')
    logging.info('User specified conf file: %s' % conf)
    logging.info('C3 username: %s' % c3username)
    logging.info('C3 API KEY: %s' % c3apikey)
    logging.info('Output verbose level: %s' % verbose)


main.add_command(group_batch.create)
main.add_command(group_batch.create_prototype)
main.add_command(group_single.query)
