# Shortcut Data Model Summary

## Overview

Shortcut (formerly Clubhouse) is a project management platform with a hierarchical data model designed for agile software development teams.

## Core Resources

### 1. Stories
The fundamental unit of work in Shortcut.

**Key Properties:**
- `id`: Unique identifier
- `name`: Story title
- `description`: Detailed description
- `story_type`: feature | bug | chore
- `workflow_state_id`: Current state in workflow
- `project_id`: Required - belongs to one project
- `epic_id`: Optional - parent epic
- `group_id`: Optional - assigned team
- `iteration_id`: Optional - sprint assignment
- `estimate`: Story points
- `owner_ids`: Array of assigned members
- `follower_ids`: Array of following members
- `labels`: Array of tags
- `tasks`: Checklist items
- `blocked`: Boolean flag

### 2. Groups (Teams)
Organizational units representing teams. Note: The API uses "groups" but these represent teams.

**Key Properties:**
- `id`: UUID format
- `name`: Team name
- `mention_name`: @mention handle
- `member_ids`: Array of team members
- `default_workflow_id`: Default workflow for stories
- `workflow_ids`: Available workflows
- Statistics: `num_stories`, `num_stories_started`, `num_stories_backlog`

### 3. Projects
Containers for organizing stories - can represent products, components, or initiatives.

**Key Properties:**
- `id`: Unique identifier
- `name`: Project name
- `abbreviation`: 3-character code
- `team_id`: Associated team
- `workflow_id`: Project workflow
- `iteration_length`: Sprint duration in weeks
- `color`: Visual identifier
- `stats`: Project metrics

### 4. Epics
Large features or initiatives that span multiple stories.

**Key Properties:**
- `id`: Unique identifier
- `name`: Epic title
- `description`: Epic details
- `epic_state_id`: Workflow state
- `group_ids`: Can span multiple teams
- `objective_ids`: Related objectives
- `planned_start_date`: Start timeline
- `deadline`: Target completion
- `completed`: Boolean status

### 5. Iterations (Sprints)
Time-boxed work periods for agile planning.

**Key Properties:**
- `id`: Unique identifier
- `name`: Iteration name
- `start_date`: Beginning date
- `end_date`: Ending date
- `status`: Current status
- Stories association

### 6. Workflows
Define the process states for stories and epics.

**Key Properties:**
- `id`: Unique identifier
- `name`: Workflow name
- `states`: Array of workflow states
- `default_state_id`: Initial state

**Common States:**
- Unstarted / To Do
- In Progress / Started
- Done / Completed
- Custom states per workflow

### 7. Members
Users in the Shortcut workspace.

**Key Properties:**
- `id`: UUID format
- `name`: Display name
- `mention_name`: @mention handle
- `email`: Email address
- `role`: admin | member | observer
- `group_ids`: Team memberships

## Relationships

```
┌─────────────┐
│   Members   │
└──────┬──────┘
       │ belong to
       ▼
┌─────────────┐     owns      ┌─────────────┐
│   Groups    │◄──────────────│   Stories   │
└─────────────┘               └──────┬──────┘
       │                             │
       │ can own                     │ belong to
       ▼                             ▼
┌─────────────┐     contains  ┌─────────────┐
│    Epics    │◄──────────────│  Projects   │
└─────────────┘               └─────────────┘
                                     │
                                     │ uses
                                     ▼
                              ┌─────────────┐
                              │  Workflows  │
                              └─────────────┘
```

## Key Design Principles

### 1. Project-Centric
- Every story must belong to exactly one project
- Projects define the primary organizational structure

### 2. Flexible Team Assignment
- Stories can be assigned to groups (teams) or left unassigned
- Epics can span multiple groups for cross-team initiatives

### 3. Workflow-Driven
- Stories progress through defined workflow states
- Different groups can have different workflows
- Epics have their own workflow states

### 4. Rich Collaboration
- Comments on stories and epics
- Followers for notifications
- @mentions for team members

### 5. Hierarchical Organization
```
Workspace
  └── Groups (Teams)
       └── Members
  └── Projects
       └── Stories
            └── Tasks
  └── Epics
       └── Stories
  └── Iterations
       └── Stories
```

## API Authentication

- **Method**: API Token
- **Header**: `Shortcut-Token: your-api-token`
- **Base URL**: `https://api.app.shortcut.com/api/v3/`

## Common Operations

### Story Management
- Create story (requires project_id)
- Move between workflow states
- Assign to groups, epics, iterations
- Add comments and tasks
- Update estimates and labels

### Team Coordination
- List group members and stories
- Track team velocity and backlog
- Manage group workflows

### Project Organization
- Create projects with workflows
- Track project statistics
- Manage project iterations

### Epic Planning
- Create multi-team epics
- Track epic progress
- Link stories to epics
- Set epic timelines

## CLI Design Implications

Based on this model, a Shortcut CLI should support:

1. **Context Awareness**
   - Default to current project/group from git or config
   - Allow overrides with flags

2. **Resource Commands**
   ```
   sc story create/list/view/update
   sc epic create/list/view/update
   sc group list/view
   sc project list/view/create
   sc iteration current/list
   ```

3. **Workflow Actions**
   ```
   sc story move <state>
   sc story assign <group>
   sc story estimate <points>
   ```

4. **Bulk Operations**
   ```
   sc story bulk update
   sc story bulk move
   ```

5. **Search and Filter**
   ```
   sc story search <query>
   sc story list --group=<name> --iteration=current
   ```