import click
from rich.console import Console
from rich.table import Table
from sc.utils import get_client

from useshortcut.models import SearchInputs
console = Console()


@click.group()
def team():
    """Manage teams in Shortcut."""
    pass


@team.command()
def list():
    """List all teams."""
    client = get_client()
    groups = client.list_groups()
    
    table = Table(title="Teams")
    table.add_column("ID", style="cyan", no_wrap=True)
    table.add_column("Name", style="green")
    table.add_column("Description")
    table.add_column("Members", justify="right")
    
    for g in groups:
        table.add_row(
            str(g.id),
            g.name,
            g.description or "",
            str(len(g.member_ids))
        )
    
    console.print(table)


@team.command()
@click.argument('group_id')
def view(group_id):
    """View details of a specific team."""
    client = get_client()
    g = client.get_group(group_id)
    console.print(f"\n[bold]Team: {g.name}[/bold]")
    console.print(f"ID: [cyan]{g.id}[/cyan]")
    console.print(f"Description: {g.description or 'No description'}")
    console.print(f"Members: {len(g.member_ids)}")
    console.print(f"Color: {g.color}")
    console.print(f"Archived: {g.archived}")
    console.print(f"Entity Type: {g.entity_type}")


@team.command()
@click.argument('team_id')
def members(team_id):
    """List members of a team."""
    client = get_client()
    g = client.get_group(team_id)
    api_members = client.list_members()
    console.print(f"\n[bold]Members of {g.name}:[/bold]")
    
    table = Table()
    table.add_column("ID", style="cyan")
    table.add_column("Name", style="green")
    table.add_column("Email")
    table.add_column("Role")
    
    team_members = [m for m in api_members if m.id in g.member_ids]
    
    for member in team_members:
        table.add_row(
            member.id,
            member.profile.name,
            member.profile.email_address,
            member.role
        )
    
    console.print(table)


@team.command()
@click.argument('team_id')
@click.option('--limit', '-l', default=20, help='Limit number of stories')
@click.option('--state', '-s', help='Filter by workflow state')
def stories(team_id, limit, state):
    """List stories assigned to a team."""
    client = get_client()
    g = client.get_group(team_id)
    query = f"group:{team_id}"

    if state:
        query += f" state:{state}"

    search_params = SearchInputs(query=query, page_size=limit)
    search_results = client.search_stories(search_params)
    stories = search_results.data
    console.print(f"\n[bold]Stories for {g.name}:[/bold]")
    
    table = Table()
    table.add_column("ID", style="cyan")
    table.add_column("Name", style="green")
    table.add_column("Type")
    table.add_column("State")
    table.add_column("Estimate")
    table.add_column("Owner")
    
    for story in stories:
        owner_ids = story.owner_ids
        owner_name = "Unassigned"
        if owner_ids:
            try:
                owner = client.get_member(owner_ids[0])
                owner_name = owner.profile.name
            except:
                owner_name = owner_ids[0]
        
        # Get workflow state name
        state_name = "Unknown"
        try:
            workflows = client.list_workflows()
            for workflow in workflows:
                for state in workflow.states:
                    if state.id == story.workflow_state_id:
                        state_name = state.name
                        break
        except:
            state_name = str(story.workflow_state_id)
        
        table.add_row(
            str(story.id),
            story.name[:50] + "..." if len(story.name) > 50 else story.name,
            story.story_type,
            state_name,
            str(story.estimate) if story.estimate else "-",
            owner_name
        )
    
    console.print(table)