# Contributing to AI Virtual Assistant

Thank you for your interest in contributing to this project! This document provides guidelines and instructions for contributing.

## Getting Started

1. Fork the repository
2. Clone your fork: `git clone <your-fork-url>`
3. Create a branch: `git checkout -b feature/your-feature-name`
4. Make your changes
5. Test your changes
6. Commit your changes: `git commit -m "Add: your feature description"`
7. Push to your fork: `git push origin feature/your-feature-name`
8. Open a Pull Request

## Code Style

- Follow PEP 8 style guide for Python code
- Use type hints where appropriate
- Add docstrings to functions and classes
- Keep functions focused and modular

## Adding New Tools

When adding a new tool:

1. Create a new file in `src/tools/` inheriting from `BaseTool`
2. Implement required methods:
   - `get_function_declarations()`: Define available functions
   - `execute()`: Implement function logic
3. Register the tool in `src/tools/__init__.py`
4. Add tests if possible
5. Update documentation

## Testing

Before submitting a PR:

- Test your changes thoroughly
- Ensure no linter errors
- Test with different audio configurations
- Verify function calling works correctly

## Commit Messages

Use clear, descriptive commit messages:
- `Add: feature description`
- `Fix: bug description`
- `Update: change description`
- `Refactor: refactoring description`

## Questions?

Feel free to open an issue for questions or discussions about contributions.

