# Story Create Command Demo

This demonstrates what the interactive story creation flow looks like:

```
$ sc story create

Story title: Implement user authentication API endpoints

? Story type: (Use arrow keys)
  ❯ feature
    bug
    chore
[Selected: feature]

? Project: (Use arrow keys)
  ❯ API Backend
    Frontend Web
    Mobile App
    Infrastructure
[Selected: API Backend]

? Description (optional, press Enter to skip):
Add REST API endpoints for user authentication including:
- POST /auth/login - User login with email/password
- POST /auth/logout - Logout and invalidate session
- POST /auth/refresh - Refresh access token
- GET /auth/me - Get current user info

Should use JWT tokens with refresh token rotation.

? Estimate in points (optional): 5

? Assign to: (Use arrow keys)
  ❯ Unassigned
    Sarah Chen (sarah.chen@company.com)
    Alex Johnson (alex.johnson@company.com)
    Maria Garcia (maria.garcia@company.com)
    James Wilson (james.wilson@company.com)
[Selected: Sarah Chen]

? Add to epic: (Use arrow keys)
  ❯ No epic
    Authentication & Authorization
    User Management
    API v2 Migration
[Selected: Authentication & Authorization]

? Add to iteration: (Use arrow keys)
  ❯ No iteration
    Sprint 24 (started)
    Sprint 25 (unstarted)
[Selected: Sprint 24]

? Assign to team: (Use arrow keys)
  ❯ No team
    Backend
    Frontend
    Mobile
    DevOps
[Selected: Backend]

✓ Created story #12345
View in browser: https://app.shortcut.com/workspace/story/12345
```

## What happens behind the scenes:

1. **Story title**: User enters a descriptive title
2. **Story type**: Select from feature/bug/chore
3. **Project**: Shows only non-archived projects
4. **Description**: Optional multiline markdown description
5. **Estimate**: Optional story points (numeric)
6. **Owner**: Shows all active members with name and email
7. **Epic**: Shows only epics that belong to the selected project
8. **Iteration**: Shows only active iterations (unstarted/started)
9. **Team**: Shows all non-archived teams/groups

The command then creates the story using the Shortcut API and returns the story ID and web URL for easy access.