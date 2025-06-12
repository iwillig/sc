# Shortcut CLI Implementation Plan

## Overview
This plan outlines the implementation of core Shortcut objects and commands for the CLI tool, following the design specified in CLI_DESIGN_PLAN.md.

## Current Status
✅ **Completed:**
- Basic CLI structure with Click
- Configuration system (simple YAML-based)
- Team/Group commands (list, view, members, stories)
- Iteration commands (list, current, next, view, stories, stats)
- Search command (global search)
- Centralized API client management

## Implementation Phases

### Phase 1: Core Story Management (Priority: HIGH)
The Story resource is the most critical component of Shortcut.

#### 1.1 Story CRUD Operations
**File:** `sc/commands/story.py`

```python
# Commands to implement:
sc story create         # Interactive story creation
sc story search         # Search stories using the search API
sc story view <id>      # View story details  
sc story edit <id>      # Edit story (interactive)
sc story delete <id>    # Delete a story
```

**Key Features:**
- Interactive prompts for creation/editing
- Smart defaults (current iteration, detected project)
- Rich formatting for story details
- Support for description in markdown
- Search command with powerful query syntax (e.g., "owner:me state:in-progress")

#### 1.2 Story Workflow Commands
```python
# Workflow management:
sc story move <id> <state>      # Move to any workflow state
sc story start <id>             # Shortcut to "In Progress"
sc story finish <id>            # Shortcut to "Done"
sc story block <id> [reason]    # Mark as blocked
sc story unblock <id>           # Remove block
```

#### 1.3 Story Assignment Commands  
```python
# Assignment operations:
sc story assign <id> <member>   # Assign to member
sc story group <id> <group>     # Assign to group/team
sc story epic <id> <epic>       # Add to epic
sc story iteration <id> <iter>  # Add to iteration
```

#### 1.4 Story Metadata Commands
```python
# Metadata management:
sc story comment <id>           # Add a comment
sc story estimate <id> <pts>    # Set story points
sc story label <id> <labels...> # Add/remove labels
sc story task <id>              # Manage tasks within story
```

### Phase 2: Epic Management (Priority: HIGH)
Epics group related stories together.

**File:** `sc/commands/epic.py`

```python
# Commands to implement:
sc epic create          # Create new epic
sc epic list            # List all epics
sc epic view <id>       # View epic details with progress
sc epic edit <id>       # Edit epic details
sc epic stories <id>    # List stories in epic
sc epic add <id> <story_ids...>     # Add stories to epic
sc epic remove <id> <story_ids...>  # Remove stories from epic
sc epic complete <id>   # Mark epic as complete
sc epic stats <id>      # Show epic statistics
```

### Phase 3: Project Management (Priority: HIGH)  
Projects organize work at the highest level.

**File:** `sc/commands/project.py`

```python
# Commands to implement:
sc project list         # List all projects
sc project view <id>    # View project details
sc project create       # Create new project (admin)
sc project stories <id> # List project stories
sc project stats <id>   # Show project statistics
sc project teams <id>   # List teams in project
```

### Phase 4: Authentication Commands (Priority: MEDIUM)
Improve authentication experience.

**File:** `sc/commands/auth.py`

```python
# Commands to implement:
sc auth login           # Interactive login with API token
sc auth logout          # Remove stored credentials  
sc auth status          # Show current authentication status
sc auth token           # Display current token (for scripts)
```

**Features:**
- Validate token on login
- Show user info on status
- Support for environment variables and config file

### Phase 5: Workflow Commands (Priority: MEDIUM)
Understanding workflow states is crucial for story management.

**File:** `sc/commands/workflow.py`

```python
# Commands to implement:
sc workflow list        # List all workflows
sc workflow view <id>   # View workflow states
sc workflow states <id> # List states with descriptions
sc workflow default     # Show default workflow
```

### Phase 6: Enhanced Features (Priority: LOW)

#### 6.1 Member Commands
**File:** `sc/commands/member.py`
```python
sc member list          # List all members
sc member view <id>     # View member details
sc member stories <id>  # List member's stories
```

#### 6.2 Label Commands  
**File:** `sc/commands/label.py`
```python
sc label list           # List all labels
sc label create         # Create new label
sc label stories <name> # List stories with label
```

## Implementation Strategy

### 1. Common Patterns
Create reusable utilities for common patterns:

**File:** `sc/utils/common.py`
- ID resolution (support both numeric and full IDs)
- State name to ID mapping
- Member name to ID resolution  
- Interactive selection prompts
- Pagination handling

### 2. Output Formatting
Standardize output across commands:

**File:** `sc/formatters/base.py`
- Table formatter (using Rich)
- JSON formatter
- CSV formatter
- Field selection support

### 3. Error Handling
Consistent error handling:
- API errors with helpful messages
- Network timeouts
- Invalid IDs/references
- Permission errors

### 4. Testing Strategy
- Unit tests for each command module
- Integration tests with mock API
- CLI end-to-end tests

## Priority Order

1. **Story Commands** (most used feature)
   - Basic CRUD first
   - Then workflow commands
   - Then assignment/metadata

2. **Epic Commands** (organizational)
   - List and view first
   - Then create/edit
   - Then story management

3. **Project Commands** (context)
   - List and view only initially
   - Stats can come later

4. **Auth Commands** (better UX)
   - Login/logout first
   - Status later

5. **Workflow Commands** (supporting)
   - Needed for story state management
   - Read-only initially

## Success Metrics

1. **Coverage**: Implement 80% of planned commands
2. **Performance**: All commands complete in <2 seconds  
3. **Usability**: Minimal required flags for common operations
4. **Reliability**: Graceful handling of all error cases
5. **Consistency**: Uniform command structure and output

## Next Steps

1. Start with Story CRUD commands (create, list, view)
2. Add interactive prompts using questionary
3. Implement state management (workflow commands)
4. Add filtering and search capabilities
5. Build out Epic management
6. Complete Project commands
7. Polish with auth commands