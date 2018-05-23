import os
import click
import logging
import c3.config as config
from c3.commands.pool import commands as group_batch
from c3.commands.single import commands as group_single
from c3.commands.cid import commands as group_cid


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
    configuration = config.Configuration.get_instance()
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

    try:
        verbose = configuration.config['GENERAL']['Verbose']
    except KeyError:
        logger.warning('Fallback to default verbose value.')

    print('Configuration:')
    print('\tUser specified conf file: %s' % conf)
    print('\tC3 username: %s' % c3username)
    print('\tC3 API KEY: %s' % c3apikey)
    print('\tOutput verbose level: %s' % verbose)


main.add_command(group_batch.create)
main.add_command(group_single.query)
main.add_command(group_cid.show_cid)
