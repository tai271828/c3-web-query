import os
import click
from c3.commands.pool import commands as group_batch
from c3.commands.single import commands as group_single


@click.group()
@click.option('--c3username',
              default=lambda: os.environ.get('C3USERNAME', ''),
              help='Your C3 username')
@click.option('--c3apikey',
              default=lambda: os.environ.get('C3APIKEY', ''),
              help='Your C3 API KEY')
@click.option('--verbose', default=1,
              help='Verbose level, the lower the fewer message output.')
@click.option('--level', default=1,
              help='Review level, the lower number means lower pass threshold.')
def main(c3username, c3apikey, verbose, level):
    pass


main.add_command(group_batch.batch)
main.add_command(group_single.single)