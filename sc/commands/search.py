import click
import os
from useshortcut.client import APIClient
from useshortcut.models import SearchInputs
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
def search():
    """Search across Shortcut resources."""
    pass


@search.command(name='all')
@click.argument('query')
@click.option('--limit', '-l', default=10, help='Limit results per type')
def search_all(query, limit):
    """Global search across all resources."""
    client = get_client()
    
    console.print(f"\n[bold]Searching for: '{query}'[/bold]\n")
    
    # Search stories
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
    
    # Search epics
    try:
        # Note: search_epics doesn't exist in the API, using general search instead
        search_params = SearchInputs(query=f"{query} type:epic", page_size=limit)
        search_results = client.search(search_params)
        epics = [r for r in (search_results.data if hasattr(search_results, 'data') else search_results) if hasattr(r, 'epic_id')]
        epics = epics[:limit]
        if epics:
            console.print("[bold blue]Epics:[/bold blue]")
            table = Table()
            table.add_column("ID", style="cyan")
            table.add_column("Name", style="green")
            table.add_column("State")
            table.add_column("Stories")
            
            for epic in epics:
                table.add_row(
                    str(epic.id),
                    epic.name[:60] + "..." if len(epic.name) > 60 else epic.name,
                    epic.state,
                    str(len(epic.story_ids))
                )
            
            console.print(table)
            console.print()
    except Exception as e:
        console.print(f"[red]Error searching epics: {e}[/red]")
    
    # Search iterations
    try:
        iterations = client.list_iterations()
        matching_iterations = [i for i in iterations if query.lower() in i.name.lower()][:limit]
        
        if matching_iterations:
            console.print("[bold yellow]Iterations:[/bold yellow]")
            table = Table()
            table.add_column("ID", style="cyan")
            table.add_column("Name", style="green")
            table.add_column("Status")
            table.add_column("Stories")
            
            for i in matching_iterations:
                table.add_row(
                    str(i.id),
                    i.name,
                    i.status,
                    str(len(i.story_ids))
                )
            
            console.print(table)
            console.print()
    except Exception as e:
        console.print(f"[red]Error searching iterations: {e}[/red]")


@search.command()
@click.argument('query')
@click.option('--limit', '-l', default=20, help='Limit number of results')
@click.option('--type', '-t', help='Filter by story type (feature, bug, chore)')
@click.option('--state', '-s', help='Filter by workflow state')
def stories(query, limit, type, state):
    """Search for stories."""
    client = get_client()
    
    # Build query with filters
    full_query = query
    if type:
        full_query += f" type:{type}"
    if state:
        full_query += f" state:{state}"
    
    console.print(f"\n[bold]Searching stories for: '{full_query}'[/bold]\n")
    
    try:
        search_params = SearchInputs(query=full_query, page_size=limit)
        try:
            search_results = client.search_stories(search_params)
            stories = search_results.data if hasattr(search_results, 'data') else search_results
            stories = stories[:limit] if isinstance(stories, list) else []
        except TypeError as e:
            # Fallback: use raw API if model parsing fails
            import requests
            headers = {'Shortcut-Token': client.api_token}
            response = requests.get(f"{client.base_url}/search/stories", headers=headers, params={'query': full_query, 'page_size': limit})
            if response.status_code == 200:
                data = response.json()
                stories = data.get('data', [])
                # Convert raw dicts to objects with necessary attributes
                from types import SimpleNamespace
                stories = [SimpleNamespace(**s) for s in stories[:limit]]
            else:
                raise
        
        if not stories:
            console.print("[yellow]No stories found[/yellow]")
            return
        
        table = Table()
        table.add_column("ID", style="cyan")
        table.add_column("Name", style="green")
        table.add_column("Type")
        table.add_column("State")
        table.add_column("Estimate")
        table.add_column("Owner")
        
        workflows = client.list_workflows()
        
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
            for workflow in workflows:
                for state in workflow.states:
                    if state.id == story.workflow_state_id:
                        state_name = state.name
                        break
            
            table.add_row(
                str(story.id),
                story.name[:50] + "..." if len(story.name) > 50 else story.name,
                story.story_type,
                state_name,
                str(story.estimate) if story.estimate else "-",
                owner_name
            )
        
        console.print(table)
        console.print(f"\n[dim]Found {len(stories)} stories[/dim]")
        
    except Exception as e:
        console.print(f"[red]Error searching stories: {e}[/red]")


@search.command()
@click.argument('query')
@click.option('--limit', '-l', default=20, help='Limit number of results')
@click.option('--state', '-s', help='Filter by epic state')
def epics(query, limit, state):
    """Search for epics."""
    client = get_client()
    
    # Build query with filters
    full_query = query
    if state:
        full_query += f" state:{state}"
    
    console.print(f"\n[bold]Searching epics for: '{full_query}'[/bold]\n")
    
    try:
        # Note: search_epics doesn't exist in the API, using general search instead
        search_params = SearchInputs(query=f"{full_query} type:epic", page_size=limit)
        search_results = client.search(search_params)
        # Filter for epic results
        all_results = search_results.data if hasattr(search_results, 'data') else search_results
        epics = []
        if isinstance(all_results, list):
            for result in all_results:
                if hasattr(result, 'entity_type') and result.entity_type == 'epic':
                    epics.append(result)
        epics = epics[:limit]
        
        if not epics:
            console.print("[yellow]No epics found[/yellow]")
            return
        
        table = Table()
        table.add_column("ID", style="cyan")
        table.add_column("Name", style="green")
        table.add_column("State")
        table.add_column("Stories")
        table.add_column("Completed")
        table.add_column("Started")
        
        for epic in epics:
            table.add_row(
                str(epic.id),
                epic.name[:50] + "..." if len(epic.name) > 50 else epic.name,
                epic.state,
                str(len(epic.story_ids)),
                str(epic.stats.num_stories_done) if epic.stats else "-",
                epic.started_at[:10] if epic.started_at else "-"
            )
        
        console.print(table)
        console.print(f"\n[dim]Found {len(epics)} epics[/dim]")
        
    except Exception as e:
        console.print(f"[red]Error searching epics: {e}[/red]")