import click

@click.group()
@click.version_option()
def cli():
    """SC - Command line tool."""
    pass

@cli.command()
@click.argument('name')
@click.option('--greeting', '-g', default='Hello', help='Greeting to use')
def greet(name, greeting):
    """Greet someone."""
    click.echo(f'{greeting}, {name}!')

if __name__ == '__main__':
    cli()