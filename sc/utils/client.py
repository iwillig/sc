"""Utility for getting the Shortcut API client."""

import click
from useshortcut.client import APIClient
from rich.console import Console
from sc.config import get_config

console = Console()


def get_client() -> APIClient:
    """Get Shortcut client with API token from config or environment."""
    config = get_config()
    token = config.get_api_token()
    
    if not token:
        console.print("[red]Error: No API token found.[/red]")
        console.print("Set SHORTCUT_API_TOKEN environment variable or save token in ~/.config/shortcut/config.yml")
        raise click.Abort()
    
    return APIClient(api_token=token)