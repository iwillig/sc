import click
from sc.commands.teams import team
from sc.commands.iteration import iteration
from sc.commands.search import search

@click.group()
@click.version_option()
def cli():
    """SC - Shortcut Command Line Interface.

    A command-line tool for interacting with Shortcut project management.

    Set your SHORTCUT_API_TOKEN environment variable before using.
    """
    pass

# Add command groups
cli.add_command(team)
cli.add_command(iteration)
cli.add_command(search)

if __name__ == '__main__':
    cli()
