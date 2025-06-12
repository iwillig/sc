import click
import os
from useshortcut.client import APIClient
from rich.console import Console
from rich.table import Table

console = Console()


def get_client():
    """Get Shortcut client with API token from environment."""
    token = os.environ.get('SHORTCUT_API_TOKEN')
    if not token:
        console.print("[red]Error: SHORTCUT_API_TOKEN environment variable not set[/red]")
        raise click.Abort()
    return APIClient(api_token=token)


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
    try:
        g = client.get_group(group_id)
    except Exception as e:
        console.print(f"[red]Error: Could not find team with ID '{group_id}'[/red]")
        console.print(f"[dim]Details: {str(e)}[/dim]")
        return
    
    console.print(f"\n[bold]Team: {g.name}[/bold]")
    console.print(f"ID: [cyan]{g.id}[/cyan]")
    console.print(f"Description: {g.description or 'No description'}")
    console.print(f"Members: {len(g.member_ids)}")
    console.print(f"Color: {g.color}")
    console.print(f"Archived: {g.archived}")
    console.print(f"Entity Type: {g.entity_type}")


@team.command()
@click.argument('group_id')
def members(group_id):
    """List members of a team."""
    client = get_client()
    try:
        g = client.get_group(group_id)
        members = client.list_members()
    except Exception as e:
        console.print(f"[red]Error: Could not find team with ID '{group_id}'[/red]")
        console.print(f"[dim]Details: {str(e)}[/dim]")
        return
    
    console.print(f"\n[bold]Members of {g.name}:[/bold]")
    
    table = Table()
    table.add_column("ID", style="cyan")
    table.add_column("Name", style="green")
    table.add_column("Email")
    table.add_column("Role")
    
    group_members = [m for m in members if m.id in g.member_ids]
    
    for member in group_members:
        table.add_row(
            member.id,
            member.profile.name,
            member.profile.email_address,
            member.role
        )
    
    console.print(table)


@team.command()
@click.argument('group_id')
@click.option('--limit', '-l', default=20, help='Limit number of stories')
@click.option('--state', '-s', help='Filter by workflow state')
def stories(group_id, limit, state):
    """List stories assigned to a team."""
    client = get_client()
    try:
        g = client.get_group(group_id)
    except Exception as e:
        console.print(f"[red]Error: Could not find team with ID '{group_id}'[/red]")
        console.print(f"[dim]Details: {str(e)}[/dim]")
        return
    
    from useshortcut.models import SearchInputs
    
    query = f"group:{group_id}"
    if state:
        query += f" state:{state}"
    
    try:
        search_params = SearchInputs(query=query, page_size=limit)
        try:
            search_results = client.search_stories(search_params)
            stories = search_results.data if hasattr(search_results, 'data') else search_results
            stories = stories[:limit] if isinstance(stories, list) else []
        except TypeError as e:
            # Fallback: use raw API if model parsing fails
            import requests
            headers = {'Shortcut-Token': client.api_token}
            response = requests.get(f"{client.base_url}/search/stories", headers=headers, params={'query': query, 'page_size': limit})
            if response.status_code == 200:
                data = response.json()
                stories = data.get('data', [])
                # Convert raw dicts to objects with necessary attributes
                from types import SimpleNamespace
                stories = [SimpleNamespace(**s) for s in stories[:limit]]
            else:
                raise
    except Exception as e:
        console.print(f"[red]Error searching stories: {str(e)}[/red]")
        return
    
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