import click


@click.command()
@click.argument('algorithm')
@click.option('--certificate',
              type=click.Choice(['14.04.5', '16.04']),
              default='16.04',
              help='Filters to match certify status')
def create(algorithm, certificate):
    """
    Create a test pool by given categories.
    """
    click.echo('Creating a pool...')
    click.echo('Algorithm to pick up systems: %s' % algorithm)
    click.echo('Filter - Certify status : %s' % certificate)

