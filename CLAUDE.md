# Project-specific instructions for Shortcut CLI

## Error Handling
- Do NOT use try/except statements in the code - let errors propagate to the top level of the program
- Errors should be handled at the CLI command level only when necessary for user-friendly messages
- Let the API client raise exceptions naturally

## Code Style
- Keep functions simple and focused
- Use type hints where appropriate
- Import from utils modules for common operations
- Follow existing patterns in the codebase
- ALL Python import statements must be at the top level of the module - no imports inside functions