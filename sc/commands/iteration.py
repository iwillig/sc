import click
from datetime import datetime
from rich.console import Console
from rich.table import Table
from sc.utils import get_client

console = Console()




@click.group()
def iteration():
    """Manage iterations in Shortcut."""
    pass


@iteration.command()
@click.option('--include-archived', is_flag=True, help='Include archived iterations')
def list(include_archived):
    """List all iterations."""
    client = get_client()
    try:
        iterations = client.list_iterations()
    except Exception as e:
        console.print(f"[red]Error listing iterations: {str(e)}[/red]")
        return
    
    # Note: API doesn't provide archived flag for iterations
    # Filter by status instead - 'done' iterations are effectively archived
    if not include_archived:
        iterations = [i for i in iterations if i.status != 'done']
    
    # Sort by start date
    iterations.sort(key=lambda x: x.start_date if x.start_date else datetime.min.isoformat())
    
    table = Table(title="Iterations")
    table.add_column("ID", style="cyan")
    table.add_column("Name", style="green")
    table.add_column("Status")
    table.add_column("Start Date")
    table.add_column("End Date")
    table.add_column("Stories")
    
    for i in iterations:
        status_color = {
            "unstarted": "yellow",
            "started": "green",
            "done": "blue"
        }.get(i.status, "white")
        
        table.add_row(
            str(i.id),
            i.name,
            f"[{status_color}]{i.status}[/{status_color}]",
            i.start_date[:10] if i.start_date else "-",
            i.end_date[:10] if i.end_date else "-",
            str(i.stats['num_stories_done'] + i.stats['num_stories_started'] + i.stats['num_stories_unstarted']) if i.stats else "0"
        )
    
    console.print(table)


@iteration.command()
def current():
    """Show the current active iteration."""
    client = get_client()
    iterations = client.list_iterations()
    
    current_iter = None
    for i in iterations:
        if i.status == "started":
            current_iter = i
            break
    
    if not current_iter:
        console.print("[yellow]No current iteration found[/yellow]")
        return
    
    console.print(f"\n[bold]Current Iteration: {current_iter.name}[/bold]")
    console.print(f"ID: [cyan]{current_iter.id}[/cyan]")
    console.print(f"Status: [green]{current_iter.status}[/green]")
    console.print(f"Start Date: {current_iter.start_date[:10] if current_iter.start_date else 'Not set'}")
    console.print(f"End Date: {current_iter.end_date[:10] if current_iter.end_date else 'Not set'}")
    console.print(f"Stories: {len(current_iter.story_ids)}")
    if current_iter.description:
        console.print(f"Description: {current_iter.description}")


@iteration.command()
def next():
    """Show the next planned iteration."""
    client = get_client()
    iterations = client.list_iterations()
    
    # Find unstarted iterations and sort by start date
    future_iterations = [i for i in iterations if i.status == "unstarted" and i.start_date]
    if not future_iterations:
        console.print("[yellow]No future iterations found[/yellow]")
        return
    
    future_iterations.sort(key=lambda x: x.start_date)
    next_iter = future_iterations[0]
    
    console.print(f"\n[bold]Next Iteration: {next_iter.name}[/bold]")
    console.print(f"ID: [cyan]{next_iter.id}[/cyan]")
    console.print(f"Status: [yellow]{next_iter.status}[/yellow]")
    console.print(f"Start Date: {next_iter.start_date[:10] if next_iter.start_date else 'Not set'}")
    console.print(f"End Date: {next_iter.end_date[:10] if next_iter.end_date else 'Not set'}")
    console.print(f"Stories: {len(next_iter.story_ids)}")
    if next_iter.description:
        console.print(f"Description: {next_iter.description}")


@iteration.command()
@click.argument('iteration_id', type=int)
def view(iteration_id):
    """View details of a specific iteration."""
    client = get_client()
    try:
        i = client.get_iteration(iteration_id)
    except Exception as e:
        console.print(f"[red]Error: Could not find iteration with ID '{iteration_id}'[/red]")
        console.print(f"[dim]Details: {str(e)}[/dim]")
        return
    
    status_color = {
        "unstarted": "yellow",
        "started": "green",
        "done": "blue"
    }.get(i.status, "white")
    
    console.print(f"\n[bold]Iteration: {i.name}[/bold]")
    console.print(f"ID: [cyan]{i.id}[/cyan]")
    console.print(f"Status: [{status_color}]{i.status}[/{status_color}]")
    console.print(f"Start Date: {i.start_date[:10] if i.start_date else 'Not set'}")
    console.print(f"End Date: {i.end_date[:10] if i.end_date else 'Not set'}")
    console.print(f"Stories: {i.stats['num_stories_done'] + i.stats['num_stories_started'] + i.stats['num_stories_unstarted'] if i.stats else 0}")
    console.print(f"Entity Type: {i.entity_type}")
    if i.description:
        console.print(f"Description: {i.description}")


@iteration.command()
@click.argument('iteration_id', type=int)
@click.option('--limit', '-l', default=20, help='Limit number of stories')
def stories(iteration_id, limit):
    """List stories in an iteration."""
    client = get_client()
    try:
        i = client.get_iteration(iteration_id)
    except Exception as e:
        console.print(f"[red]Error: Could not find iteration with ID '{iteration_id}'[/red]")
        console.print(f"[dim]Details: {str(e)}[/dim]")
        return
    
    # Search for stories in this iteration
    from useshortcut.models import SearchInputs
    search_params = SearchInputs(query=f"iteration:{iteration_id}", page_size=limit)
    try:
        search_results = client.search_stories(search_params)
        stories = search_results.data if hasattr(search_results, 'data') else search_results
        stories = stories[:limit] if isinstance(stories, list) else []
    except Exception as e:
        console.print(f"[red]Error searching stories: {str(e)}[/red]")
        return
    
    console.print(f"\n[bold]Stories in {i.name}:[/bold]")
    
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


@iteration.command()
@click.argument('iteration_id', type=int)
def stats(iteration_id):
    """Show statistics for an iteration."""
    client = get_client()
    try:
        i = client.get_iteration(iteration_id)
    except Exception as e:
        console.print(f"[red]Error: Could not find iteration with ID '{iteration_id}'[/red]")
        console.print(f"[dim]Details: {str(e)}[/dim]")
        return
    
    # Search for all stories in this iteration
    from useshortcut.models import SearchInputs
    search_params = SearchInputs(query=f"iteration:{iteration_id}", page_size=100)
    try:
        search_results = client.search_stories(search_params)
        stories = search_results.data if hasattr(search_results, 'data') else search_results
        stories = stories if isinstance(stories, list) else []
    except Exception as e:
        console.print(f"[red]Error searching stories: {str(e)}[/red]")
        return
    
    # Get done states
    workflows = client.list_workflows()
    done_state_ids = []
    for workflow in workflows:
        for state in workflow.states:
            if state.type == "done":
                done_state_ids.append(state.id)
    
    completed_stories = [s for s in stories if s.workflow_state_id in done_state_ids]
    total_points = sum(s.estimate or 0 for s in stories)
    completed_points = sum(s.estimate or 0 for s in completed_stories)
    
    console.print(f"\n[bold]Statistics for {i.name}:[/bold]")
    console.print(f"Status: {i.status}")
    console.print(f"Total Stories: {len(stories)}")
    console.print(f"Completed Stories: {len(completed_stories)}")
    console.print(f"Completion Rate: {len(completed_stories)/len(stories)*100:.1f}%" if stories else "N/A")
    console.print(f"Total Points: {total_points}")
    console.print(f"Completed Points: {completed_points}")
    console.print(f"Points Completion Rate: {completed_points/total_points*100:.1f}%" if total_points > 0 else "N/A")
    
    # Story type breakdown
    story_types = {}
    for story in stories:
        story_types[story.story_type] = story_types.get(story.story_type, 0) + 1
    
    console.print("\n[bold]Story Type Breakdown:[/bold]")
    for story_type, count in story_types.items():
        console.print(f"  {story_type}: {count}")
    
    # State breakdown
    state_counts = {}
    for story in stories:
        state_name = "Unknown"
        for workflow in workflows:
            for state in workflow.states:
                if state.id == story.workflow_state_id:
                    state_name = state.name
                    break
        state_counts[state_name] = state_counts.get(state_name, 0) + 1
    
    console.print("\n[bold]State Breakdown:[/bold]")
    for state, count in state_counts.items():
        console.print(f"  {state}: {count}")