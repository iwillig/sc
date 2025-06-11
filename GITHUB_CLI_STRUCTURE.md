# GitHub CLI Structure Documentation

## Command Hierarchy

The GitHub CLI (`gh`) follows a consistent command structure:

```
gh <resource> <action> [flags] [arguments]
```

## Core Resources and Actions

### 1. Authentication (`gh auth`)
```
gh auth login      # Interactive login
gh auth logout     # Logout from GitHub
gh auth status     # View authentication status
gh auth refresh    # Refresh authentication credentials
gh auth token      # Print the auth token
```

### 2. Repository (`gh repo`)
```
gh repo create     # Create a new repository
gh repo clone      # Clone a repository
gh repo fork       # Fork a repository
gh repo view       # View repository details
gh repo list       # List repositories
gh repo edit       # Edit repository settings
gh repo delete     # Delete a repository
gh repo sync       # Sync a forked repository
```

### 3. Pull Requests (`gh pr`)
```
gh pr create       # Create a pull request
gh pr list         # List pull requests
gh pr view         # View a pull request
gh pr checkout     # Check out a pull request
gh pr status       # Show status of pull requests
gh pr review       # Add a review to a pull request
gh pr merge        # Merge a pull request
gh pr close        # Close a pull request
gh pr reopen       # Reopen a pull request
gh pr diff         # View changes in a pull request
```

### 4. Issues (`gh issue`)
```
gh issue create    # Create an issue
gh issue list      # List issues
gh issue view      # View an issue
gh issue status    # Show status of issues
gh issue close     # Close an issue
gh issue reopen    # Reopen an issue
gh issue comment   # Add a comment to an issue
gh issue edit      # Edit an issue
```

### 5. Workflows (`gh workflow`)
```
gh workflow list   # List workflows
gh workflow view   # View workflow details
gh workflow run    # Run a workflow
gh workflow enable # Enable a workflow
gh workflow disable # Disable a workflow
```

### 6. Releases (`gh release`)
```
gh release create  # Create a release
gh release list    # List releases
gh release view    # View a release
gh release download # Download release assets
gh release delete  # Delete a release
```

## Command Patterns

### Common Flags
- `--help` - Show help for any command
- `--repo` - Specify repository (owner/repo format)
- `--json` - Output in JSON format
- `--web` - Open in web browser
- `--limit` - Limit number of results

### Interactive vs Non-Interactive
- Interactive mode: Prompts for missing information
- Non-interactive: All parameters via flags (for scripting)

### Context Awareness
- Automatically detects current repository
- Falls back to prompts if context missing
- Can override with `--repo` flag

## Design Principles

### 1. Resource-Oriented
Commands organized around GitHub resources (repos, PRs, issues, etc.)

### 2. Action-Based Subcommands
Each resource has standard CRUD operations plus resource-specific actions

### 3. Consistent Patterns
- `list` - Show multiple items
- `view` - Show single item details
- `create` - Create new item
- `edit` - Modify existing item
- `delete` - Remove item

### 4. Progressive Disclosure
- Simple commands for common tasks
- Advanced flags for power users
- `--help` available at every level

### 5. Output Flexibility
- Human-readable by default
- Machine-readable with `--json`
- Web fallback with `--web`

## Extension System

```
gh extension install   # Install an extension
gh extension list      # List installed extensions
gh extension remove    # Remove an extension
gh extension upgrade   # Upgrade extensions
```

## Configuration

```
gh config get         # Get a configuration value
gh config set         # Set a configuration value
gh config list        # List configuration settings
```

## Aliases

```
gh alias set          # Create command shortcut
gh alias list         # List aliases
gh alias delete       # Remove an alias
```

## Example Workflows

### Create and Merge a PR
```bash
gh repo fork owner/repo
gh repo clone owner/repo
cd repo
git checkout -b feature
# make changes
git push origin feature
gh pr create
gh pr merge
```

### Manage Issues
```bash
gh issue create --title "Bug report" --body "Description"
gh issue list --label "bug"
gh issue close 123
```

### Work with Releases
```bash
gh release create v1.0.0 --title "Version 1.0.0" --notes "Release notes"
gh release download v1.0.0
```

## Key Takeaways for Shortcut CLI

1. **Organize by Resource**: Stories, Epics, Projects, Iterations
2. **Standard Actions**: create, list, view, update, delete
3. **Context Detection**: Current project/workspace from git or config
4. **Output Options**: Table (default), JSON, CSV
5. **Interactive Helpers**: Prompts for missing required fields
6. **Scripting Support**: All actions possible via flags
7. **Extensibility**: Plugin system for custom commands