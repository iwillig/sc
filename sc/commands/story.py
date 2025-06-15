"""Story management commands for Shortcut CLI."""

import click
import questionary
import requests
from types import SimpleNamespace
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.markdown import Markdown
from useshortcut.models import SearchInputs, CreateStoryParams, UpdateStoryInput
from sc.utils import get_client
from sc.utils.common import get_workflow_state_map, get_state_id_by_name

console = Console()


@click.group()
def story():
    """Manage stories in Shortcut."""
    pass

@story.command()
@click.argument('story_id')
def view(story_id):
    """View detailed information about a story."""
    client = get_client()
    story = client.get_story(story_id)

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
        f"[bold]Created:[/bold] {story.created_at}",
        f"[bold]Updated:[/bold] {story.updated_at}",
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

    # Story name
    name = questionary.text("Story title:").ask()
    if not name:
        console.print("[red]Story creation cancelled[/red]")
        return

    # Get default workflow state (first state of first workflow)
    default_state_id = workflows[0].states[0].id if workflows and workflows[0].states else None
    if not default_state_id:
        console.print("[red]Error: No workflow states found[/red]")
        return

    # Create the story with basic fields
    story_data = CreateStoryParams(
        name=name,
        workflow_state_id=default_state_id,
    )

    new_story = client.create_story(story_data)

    console.print(f"\n[green]✓ Created story #{new_story.id}[/green]")
    console.print(f"[dim]View in browser: {new_story.app_url}[/dim]")
