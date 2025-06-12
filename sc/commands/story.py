"""Story management commands for Shortcut CLI."""

import click
import questionary
import requests
from datetime import datetime
from types import SimpleNamespace
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.markdown import Markdown
from useshortcut.models import SearchInputs, StoryInput, UpdateStoryInput
from sc.utils import get_client
from sc.utils.common import get_workflow_state_map, get_state_id_by_name

console = Console()


@click.group()
def story():
    """Manage stories in Shortcut."""
    pass


@story.command()
@click.argument('query', required=False, default='')
@click.option('--limit', '-l', default=25, help='Maximum number of results')
@click.option('--project', '-p', help='Filter by project')
@click.option('--owner', '-o', help='Filter by owner (use @me for self)')
@click.option('--state', '-s', help='Filter by workflow state')
@click.option('--type', '-t', help='Filter by story type (feature, bug, chore)')
@click.option('--label', help='Filter by label')
@click.option('--epic', '-e', help='Filter by epic')
@click.option('--iteration', '-i', help='Filter by iteration (use "current" for current iteration)')
@click.option('--team', help='Filter by team/group')
def search(query, limit, project, owner, state, type, label, epic, iteration, team):
    """Search for stories using Shortcut's search syntax.
    
    Examples:
        sc story search "authentication"
        sc story search --owner @me --state "In Progress"
        sc story search --type bug --label urgent
        sc story search "label:security state:todo"
    """
    client = get_client()
    
    # Build search query from options
    query_parts = []
    if query:
        query_parts.append(query)
    if project:
        query_parts.append(f'project:"{project}"')
    if owner:
        query_parts.append(f'owner:{owner}')
    if state:
        query_parts.append(f'state:"{state}"')
    if type:
        query_parts.append(f'type:{type}')
    if label:
        query_parts.append(f'label:"{label}"')
    if epic:
        query_parts.append(f'epic:"{epic}"')
    if iteration:
        query_parts.append(f'iteration:{iteration}')
    if team:
        query_parts.append(f'group:"{team}"')
    
    final_query = ' '.join(query_parts) if query_parts else '*'
    
    try:
        search_params = SearchInputs(query=final_query, page_size=limit)
        
        # Try the search
        try:
            search_results = client.search_stories(search_params)
            stories = search_results.data if hasattr(search_results, 'data') else search_results
            stories = stories[:limit] if isinstance(stories, list) else []
        except:
            # Fallback to raw API
            headers = {'Shortcut-Token': client.api_token}
            response = requests.get(
                f"{client.base_url}/search/stories",
                headers=headers,
                params={'query': final_query, 'page_size': limit}
            )
            if response.status_code == 200:
                data = response.json()
                stories = data.get('data', [])
                stories = [SimpleNamespace(**s) for s in stories[:limit]]
            else:
                raise Exception(f"Search failed: {response.status_code}")
                
    except Exception as e:
        console.print(f"[red]Error searching stories: {str(e)}[/red]")
        return
    
    if not stories:
        console.print(f"No stories found matching: {final_query}")
        return
    
    # Display results in a table
    table = Table(title=f"Stories matching: {final_query}")
    table.add_column("ID", style="cyan", no_wrap=True)
    table.add_column("Name", style="green")
    table.add_column("Type", style="yellow")
    table.add_column("State")
    table.add_column("Owner")
    table.add_column("Estimate")
    
    # Get workflows for state name mapping
    state_map = get_workflow_state_map(client)
    
    for story in stories:
        # Get owner name
        owner_name = "Unassigned"
        if hasattr(story, 'owner_ids') and story.owner_ids:
            owner = client.get_member(story.owner_ids[0])
            owner_name = owner.profile.name
        
        # Get state name
        state_name = state_map.get(story.workflow_state_id, str(story.workflow_state_id))
        
        # Truncate long names
        name = story.name[:60] + "..." if len(story.name) > 60 else story.name
        
        table.add_row(
            str(story.id),
            name,
            story.story_type,
            state_name,
            owner_name,
            str(story.estimate) if hasattr(story, 'estimate') and story.estimate else "-"
        )
    
    console.print(table)


@story.command()
@click.argument('story_id')
def view(story_id):
    """View detailed information about a story."""
    client = get_client()
    
    try:
        story = client.get_story(story_id)
    except Exception as e:
        console.print(f"[red]Error: Could not find story with ID '{story_id}'[/red]")
        console.print(f"[dim]Details: {str(e)}[/dim]")
        return
    
    # Get related data
    state_map = get_workflow_state_map(client)
    state_name = state_map.get(story.workflow_state_id, str(story.workflow_state_id))
    
    # Format owners
    owners = []
    if story.owner_ids:
        for owner_id in story.owner_ids:
            owner = client.get_member(owner_id)
            owners.append(owner.profile.name)
    
    # Basic info panel
    info_lines = [
        f"[bold]ID:[/bold] {story.id}",
        f"[bold]Type:[/bold] {story.story_type}",
        f"[bold]State:[/bold] {state_name}",
        f"[bold]Owners:[/bold] {', '.join(owners) if owners else 'Unassigned'}",
        f"[bold]Estimate:[/bold] {story.estimate if story.estimate else 'Unestimated'}",
        f"[bold]Created:[/bold] {story.created_at[:10]}",
        f"[bold]Updated:[/bold] {story.updated_at[:10]}",
    ]
    
    if story.started_at:
        info_lines.append(f"[bold]Started:[/bold] {story.started_at[:10]}")
    if story.completed_at:
        info_lines.append(f"[bold]Completed:[/bold] {story.completed_at[:10]}")
    
    if story.blocked:
        info_lines.append(f"[bold red]BLOCKED[/bold red]")
    
    if story.labels:
        label_names = [label.name for label in story.labels]
        info_lines.append(f"[bold]Labels:[/bold] {', '.join(label_names)}")
    
    console.print(Panel(story.name, title=f"Story #{story.id}", style="cyan"))
    console.print("\n".join(info_lines))
    
    # Description
    if story.description:
        console.print("\n[bold]Description:[/bold]")
        console.print(Panel(Markdown(story.description)))
    
    # Tasks
    if story.tasks:
        console.print("\n[bold]Tasks:[/bold]")
        for task in story.tasks:
            status = "✓" if task.complete else "○"
            console.print(f"  {status} {task.description}")
    
    # Comments count
    if hasattr(story, 'comments') and story.comments:
        console.print(f"\n[dim]Comments: {len(story.comments)}[/dim]")
    
    # Links
    console.print(f"\n[dim]View in browser: {story.app_url}[/dim]")


@story.command()
def create():
    """Create a new story (interactive)."""
    client = get_client()
    
    # Get available options
    workflows = client.list_workflows()
    members = client.list_members()
    epics = client.list_epics()
    iterations = client.list_iterations()
    groups = client.list_groups()
    
    # Story name
    name = questionary.text("Story title:").ask()
    if not name:
        console.print("[red]Story creation cancelled[/red]")
        return
    
    # Story type
    story_type = questionary.select(
        "Story type:",
        choices=["feature", "bug", "chore"]
    ).ask()
    

    # Description
    description = questionary.text(
        "Description (optional, press Enter to skip):",
        multiline=True
    ).ask()
    
    # Estimate
    estimate_str = questionary.text("Estimate in points (optional):").ask()
    estimate = int(estimate_str) if estimate_str and estimate_str.isdigit() else None
    
    # Owner assignment
    owner_choices = [{"name": "Unassigned", "value": None}]
    owner_choices.extend([
        {"name": f"{m.profile.name} ({m.profile.email_address})", "value": m.id}
        for m in members if not m.disabled
    ])
    owner_id = questionary.select("Assign to:", choices=owner_choices).ask()
    
    # Epic assignment (optional)
    epic_choices = [{"name": "No epic", "value": None}]
    epic_choices.extend([
        {"name": e.name, "value": e.id}
        for e in epics if not e.archived and e.project_ids and project_id in e.project_ids
    ])
    epic_id = questionary.select("Add to epic:", choices=epic_choices).ask()
    
    # Iteration assignment (optional)
    active_iterations = [i for i in iterations if i.status in ["unstarted", "started"]]
    iteration_choices = [{"name": "No iteration", "value": None}]
    iteration_choices.extend([
        {"name": f"{i.name} ({i.status})", "value": i.id}
        for i in active_iterations
    ])
    iteration_id = questionary.select("Add to iteration:", choices=iteration_choices).ask()
    
    # Team/Group assignment (optional)
    group_choices = [{"name": "No team", "value": None}]
    group_choices.extend([
        {"name": g.name, "value": g.id}
        for g in groups if not g.archived
    ])
    group_id = questionary.select("Assign to team:", choices=group_choices).ask()
    
    # Get default workflow state (first state of first workflow)
    default_state_id = workflows[0].states[0].id if workflows and workflows[0].states else None
    if not default_state_id:
        console.print("[red]Error: No workflow states found[/red]")
        return
    
    # Create the story with basic fields
    story_data = StoryInput(
        name=name,
        story_type=story_type,
        description=description or None,
        workflow_state_id=default_state_id,
        epic_id=epic_id
    )
    
    story = client.create_story(story_data)

    console.print(f"\n[green]✓ Created story #{story.id}[/green]")
    console.print(f"[dim]View in browser: {story.app_url}[/dim]")


@story.command()
@click.argument('story_id')
def edit(story_id):
    """Edit an existing story (interactive)."""
    console.print(f"[yellow]Story editing not yet implemented for story {story_id}[/yellow]")
    console.print("This will open an interactive prompt for editing stories.")


@story.command()
@click.argument('story_id')
@click.confirmation_option(prompt='Are you sure you want to delete this story?')
def delete(story_id):
    """Delete a story."""
    client = get_client()
    
    try:
        client.delete_story(story_id)
        console.print(f"[green]✓ Deleted story {story_id}[/green]")
    except Exception as e:
        console.print(f"[red]Error deleting story: {str(e)}[/red]")


# Workflow commands
@story.command()
@click.argument('story_id')
@click.argument('state')
def move(story_id, state):
    """Move a story to a different workflow state."""
    client = get_client()
    
    # Get the state ID from name
    state_id = get_state_id_by_name(client, state)
    if not state_id:
        console.print(f"[red]Error: Could not find workflow state '{state}'[/red]")
        return
    
    # Update the story
    update = UpdateStoryInput(workflow_state_id=state_id)
    story = client.update_story(story_id, update)
    
    console.print(f"[green]✓ Moved story {story_id} to '{state}'[/green]")


@story.command()
@click.argument('story_id')
def start(story_id):
    """Move a story to 'In Progress' state."""
    client = get_client()
    
    # Find "In Progress" state
    state_id = get_state_id_by_name(client, "In Progress")
    if not state_id:
        console.print(f"[red]Error: Could not find 'In Progress' workflow state[/red]")
        return
    
    # Update the story
    from useshortcut.models import UpdateStory
    update = UpdateStory(workflow_state_id=state_id)
    story = client.update_story(story_id, update)
    
    console.print(f"[green]✓ Started story {story_id}[/green]")


@story.command()
@click.argument('story_id')
def finish(story_id):
    """Move a story to 'Done' state."""
    client = get_client()
    
    # Find "Done" state
    state_id = get_state_id_by_name(client, "Done")
    if not state_id:
        console.print(f"[red]Error: Could not find 'Done' workflow state[/red]")
        return
    
    # Update the story
    from useshortcut.models import UpdateStory
    update = UpdateStory(workflow_state_id=state_id)
    story = client.update_story(story_id, update)
    
    console.print(f"[green]✓ Finished story {story_id}[/green]")


@story.command()
@click.argument('story_id')
@click.option('--reason', '-r', help='Reason for blocking')
def block(story_id, reason):
    """Mark a story as blocked."""
    console.print(f"[yellow]Blocking story {story_id} not yet implemented[/yellow]")


@story.command()
@click.argument('story_id')
def unblock(story_id):
    """Remove block from a story."""
    console.print(f"[yellow]Unblocking story {story_id} not yet implemented[/yellow]")


# Assignment commands
@story.command()
@click.argument('story_id')
@click.argument('member')
def assign(story_id, member):
    """Assign a story to a team member."""
    console.print(f"[yellow]Assigning story {story_id} to {member} not yet implemented[/yellow]")


@story.command()
@click.argument('story_id')
@click.argument('team')
def team(story_id, team):
    """Assign a story to a team/group."""
    console.print(f"[yellow]Assigning story {story_id} to team {team} not yet implemented[/yellow]")


@story.command()
@click.argument('story_id')
@click.argument('epic_id')
def epic(story_id, epic_id):
    """Add a story to an epic."""
    console.print(f"[yellow]Adding story {story_id} to epic {epic_id} not yet implemented[/yellow]")


@story.command()
@click.argument('story_id')
@click.argument('iteration_id')
def iteration(story_id, iteration_id):
    """Add a story to an iteration."""
    console.print(f"[yellow]Adding story {story_id} to iteration {iteration_id} not yet implemented[/yellow]")