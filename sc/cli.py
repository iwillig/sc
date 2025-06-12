import click
from sc.commands.teams import team
from sc.commands.iteration import iteration
from sc.commands.search import search
from sc.commands.story import story

@click.group()
@click.version_option()
def cli():
    """SC - Shortcut Command Line Interface.

    A command-line tool for interacting with Shortcut project management.

    Authentication:
    - Set SHORTCUT_API_TOKEN environment variable, or
    - Save your token in ~/.config/shortcut/config.yml
    """
    pass

# Add command groups
cli.add_command(team)
cli.add_command(iteration)
cli.add_command(search)
cli.add_command(story)

if __name__ == '__main__':
    cli()
