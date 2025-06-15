import click
from useshortcut.models import SearchInputs
from rich.console import Console
from rich.table import Table
from sc.utils import get_client

console = Console()

@click.group()
def search():
    """Search across Shortcut resources."""
    pass

@search.command(name='stories')
@click.argument('query')
@click.option('--limit', '-l', default=10, help='Limit results per type')
def search_all(query, limit):
    """Global search across all resources."""
    client = get_client()
    
    console.print(f"\n[bold]Searching for: '{query}'[/bold]\n")
    
    # Search stories
    try:
        search_params = SearchInputs(query=query, page_size=limit)
        search_results = client.search_stories(search_params)
        stories = search_results.data if hasattr(search_results, 'data') else search_results
        stories = stories[:limit] if isinstance(stories, list) else []

        if stories:
            console.print("[bold green]Stories:[/bold green]")
            table = Table()
            table.add_column("ID", style="cyan")
            table.add_column("Name", style="green")
            table.add_column("Type")
            table.add_column("State")
            
            workflows = client.list_workflows()
            
            for story in stories:
                # Get workflow state name
                state_name = "Unknown"
                for workflow in workflows:
                    for state in workflow.states:
                        if state.id == story.workflow_state_id:
                            state_name = state.name
                            break
                
                table.add_row(
                    str(story.id),
                    story.name[:60] + "..." if len(story.name) > 60 else story.name,
                    story.story_type,
                    state_name
                )
            
            console.print(table)
            console.print()
    except Exception as e:
        console.print(f"[red]Error searching stories: {e}[/red]")