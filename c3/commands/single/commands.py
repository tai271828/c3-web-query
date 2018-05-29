import click


@click.command()
@click.argument('basic')
@click.argument('extra')
@click.option('--cid', help='Target CID to query')
def query_prototype(basic, extra, cid):
    """
    Query or push single CID number.

    TODO: This is an prototype and has not implemented anything useful.
    """
    click.echo('SINGLE mode for %s' % cid)
    click.echo('Query for CID in mode: %s' % basic)
    click.echo('Query for CID with extra: %s' % extra)
