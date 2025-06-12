# Shortcut CLI Design Plan

## Overview

A command-line interface for Shortcut that follows GitHub CLI's design patterns while adapting to Shortcut's project management workflow.

## Command Structure

```
sc <resource> <action> [flags] [arguments]
```

## Core Resources and Commands

### 1. Authentication (`sc auth`)
```bash
sc auth login          # Interactive login with API token
sc auth logout         # Remove stored credentials
sc auth status         # Show current authentication status
sc auth token          # Display current token (for scripts)
```

### 2. Stories (`sc story`)
```bash
# CRUD Operations
sc story create        # Interactive story creation
sc story list          # List stories (context-aware)
sc story view <id>     # View story details
sc story edit <id>     # Edit story interactively
sc story delete <id>   # Delete a story

# Workflow Actions
sc story move <id> <state>      # Move to workflow state
sc story start <id>             # Move to "In Progress"
sc story finish <id>            # Move to "Done"
sc story block <id>             # Mark as blocked
sc story unblock <id>           # Remove block

# Assignment Actions
sc story assign <id> <member>   # Assign to member
sc story group <id> <group>     # Assign to group/team
sc story epic <id> <epic>       # Add to epic
sc story iteration <id> <iter>  # Add to iteration

# Other Actions
sc story comment <id>           # Add a comment
sc story estimate <id> <pts>    # Set story points
sc story label <id> <labels...> # Add labels
sc story task <id>              # Manage tasks
```

### 3. Epics (`sc epic`)
```bash
sc epic create         # Create new epic
sc epic list           # List epics
sc epic view <id>      # View epic details
sc epic edit <id>      # Edit epic
sc epic stories <id>   # List stories in epic
sc epic add <id> <story...>     # Add stories to epic
sc epic remove <id> <story...>  # Remove stories from epic
sc epic complete <id>  # Mark epic as complete
```

### 4. Projects (`sc project`)
```bash
sc project list        # List all projects
sc project view <id>   # View project details
sc project create      # Create new project
sc project stories <id> # List project stories
sc project stats <id>  # Show project statistics
```

### 5. Groups/Teams (`sc group`)
```bash
sc group list          # List all groups/teams
sc group view <id>     # View group details
sc group members <id>  # List group members
sc group stories <id>  # List group stories
```

### 6. Iterations (`sc iteration`)
```bash
sc iteration list      # List iterations
sc iteration current   # Show current iteration
sc iteration next      # Show next iteration
sc iteration view <id> # View iteration details
sc iteration stories <id> # List iteration stories
sc iteration stats <id> # Show iteration statistics
```

### 7. Search (`sc search`)
```bash
sc search <query>      # Global search
sc search stories <query> # Search stories
sc search epics <query>   # Search epics
```

### 8. Workflow (`sc workflow`)
```bash
sc workflow list       # List all workflows
sc workflow view <id>  # View workflow states
sc workflow states <id> # List workflow states
```

## Configuration (`sc config`)
```bash
sc config set <key> <value>  # Set configuration
sc config get <key>          # Get configuration value
sc config list               # List all settings

# Key configurations:
# - default.project
# - default.group
# - default.workflow
# - output.format (table|json|csv)
# - editor (for interactive edits)
```

## Aliases (`sc alias`)
```bash
sc alias set <name> <command>  # Create alias
sc alias list                  # List aliases
sc alias delete <name>         # Remove alias

# Example aliases:
sc alias set mine "story list --owner=@me"
sc alias set blocked "story list --blocked=true"
sc alias set current "iteration current"
```

## Global Flags

```bash
--help, -h           # Help for any command
--project, -p        # Override project context
--group, -g          # Override group context
--format, -f         # Output format (table|json|csv)
--fields             # Select output fields
--limit, -l          # Limit results
--web, -w            # Open in web browser
--no-interactive     # Disable interactive prompts
```

## Context Awareness

### Auto-Detection
1. Check git remote for Shortcut project mapping
2. Check `.shortcut/config.yml` in project root
3. Check global config (`~/.config/shortcut/`)
4. Prompt if context needed

### Context Override
```bash
sc story list                    # Uses detected context
sc story list --project=API      # Override project
sc story list --group=Backend    # Override group
```

## Interactive Features

### Story Creation Flow
```bash
$ sc story create
? Story title: Implement user authentication
? Story type: (Use arrow keys)
  ❯ feature
    bug
    chore
? Project: API (auto-detected)
? Description: <opens editor>
? Estimate: 3
? Assign to: @me
? Add to epic: Authentication Epic
? Add labels: security, backend

✓ Created story #1234 in API project
```

### Smart Defaults
- Auto-detect project from git
- Default to current iteration
- Suggest recent epics/labels
- Remember user preferences

## Output Formats

### Table (Default)
```bash
$ sc story list --limit=3
ID    Title                      Type     State        Owner
----  -------------------------  -------  -----------  --------
1234  Implement authentication   feature  In Progress  @ivan
1235  Fix login bug             bug      Todo         @sarah
1236  Update documentation      chore    Done         @alex
```

### JSON
```bash
$ sc story view 1234 --format=json
{
  "id": 1234,
  "name": "Implement authentication",
  "type": "feature",
  ...
}
```

### CSV
```bash
$ sc story list --format=csv > stories.csv
```

## Filtering and Queries

```bash
# Story filters
sc story list --state="In Progress"
sc story list --type=bug
sc story list --owner=@me
sc story list --group=Backend
sc story list --epic="Authentication"
sc story list --iteration=current
sc story list --label=urgent
sc story list --blocked=true

# Combining filters
sc story list --type=bug --state="In Progress" --owner=@me

# Search queries
sc search "authentication AND type:feature"
sc search "label:urgent state:todo"
```

## Bulk Operations

```bash
# Bulk update
sc story bulk move --state="In Progress" 1234 1235 1236
sc story bulk assign --owner=@sarah 1234 1235
sc story bulk label --add=urgent 1234 1235

# Using filters
sc story bulk move --state="Done" --filter="label:resolved"
```

## Integration Features

### Git Integration
```bash
# Auto-create story from git branch
sc story create --from-branch

# Link story to PR
sc story link 1234 --pr=123

# Create branch from story
sc story branch 1234
```

### Editor Integration
```bash
# Open story in editor
sc story edit 1234 --editor

# Bulk edit in editor
sc story list --edit
```

## Implementation Phases

### Phase 1: Foundation
- [x] Basic CLI structure (Click)
- [ ] Authentication (auth commands)
- [ ] Configuration system
- [ ] API client wrapper
- [ ] Output formatting

### Phase 2: Core Resources
- [ ] Story CRUD operations
- [ ] Basic filtering
- [ ] Project/Group context
- [ ] Table output

### Phase 3: Workflow
- [ ] Story workflow commands
- [ ] Epic management
- [ ] Iteration support
- [ ] Search functionality

### Phase 4: Enhanced Features
- [ ] Bulk operations
- [ ] Interactive prompts
- [ ] Git integration
- [ ] Aliases system

### Phase 5: Polish
- [ ] Auto-completion
- [ ] Performance optimization
- [ ] Extended output formats
- [ ] Plugin system

## Technical Architecture

### Directory Structure
```
sc/
├── cli.py              # Main CLI entry
├── commands/           # Command modules
│   ├── auth.py
│   ├── story.py
│   ├── epic.py
│   ├── project.py
│   └── ...
├── api/                # API client
│   ├── client.py
│   ├── resources/
│   └── exceptions.py
├── config/             # Configuration
│   ├── manager.py
│   └── schema.py
├── context/            # Context detection
│   ├── git.py
│   └── project.py
├── formatters/         # Output formatting
│   ├── table.py
│   ├── json.py
│   └── csv.py
└── utils/              # Utilities
    ├── interactive.py
    └── validators.py
```

### Key Libraries
- `click` - CLI framework
- `requests` - API calls
- `rich` - Enhanced terminal output
- `pyyaml` - Configuration files
- `python-dotenv` - Environment variables
- `questionary` - Interactive prompts

### Configuration Storage
```yaml
# ~/.config/shortcut/config.yml
auth:
  token: <encrypted>
  
defaults:
  project: API
  group: Backend
  workflow: Engineering
  
output:
  format: table
  fields: [id, name, type, state, owner]
  
aliases:
  mine: story list --owner=@me
  blocked: story list --blocked=true
```

## Success Metrics

1. **Performance**: Commands complete in <2 seconds
2. **Usability**: Minimal flags needed for common tasks
3. **Completeness**: Cover 80% of web UI functionality
4. **Reliability**: Graceful error handling
5. **Adoption**: Clear documentation and examples