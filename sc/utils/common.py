"""Common utilities for Shortcut CLI commands."""

from typing import Optional, Dict, List
from rich.console import Console

console = Console()


def get_workflow_state_map(client) -> Dict[int, str]:
    """Get a mapping of workflow state IDs to names."""
    state_map = {}
    workflows = client.list_workflows()
    for workflow in workflows:
        for state in workflow.states:
            state_map[state.id] = state.name
    return state_map


def get_state_id_by_name(client, state_name: str) -> Optional[int]:
    """Find workflow state ID by name (case insensitive)."""
    state_name_lower = state_name.lower()
    workflows = client.list_workflows()
    for workflow in workflows:
        for state in workflow.states:
            if state.name.lower() == state_name_lower:
                return state.id
    return None


def get_member_id_by_name(client, member_name: str) -> Optional[str]:
    """Find member ID by name or email (partial match)."""
    if member_name == "@me":
        # TODO: Get current user ID from API
        return None
    
    member_name_lower = member_name.lower()
    members = client.list_members()
    for member in members:
        if (member_name_lower in member.profile.name.lower() or 
            member_name_lower in member.profile.email_address.lower()):
            return member.id
    return None


def format_story_id(story_id: str) -> str:
    """Format story ID for display."""
    return f"#{story_id}"


def truncate_text(text: str, max_length: int = 60) -> str:
    """Truncate text with ellipsis if too long."""
    if len(text) > max_length:
        return text[:max_length - 3] + "..."
    return text