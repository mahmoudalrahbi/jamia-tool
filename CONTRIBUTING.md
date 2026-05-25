# Contributing to Jamia Tool

Thank you for your interest in contributing!

## Getting Started

1. Fork the repository
2. Clone your fork: `git clone https://github.com/YOUR_USERNAME/jamia-tool.git`
3. Create a feature branch: `git checkout -b feat/your-feature-name`
4. Set up the project following the [README](README.md)

## Development Workflow

1. Make your changes on your feature branch
2. Write or update tests in the `tests/` directory
3. Run the test suite: `python -m pytest tests/`
4. Commit with a clear message (see below)
5. Push your branch and open a Pull Request against `main`

**Direct pushes to `main` are not allowed.** All changes must go through a Pull Request and receive approval before merging.

## Commit Message Format

Use short, descriptive present-tense messages:

```
Add duplicate payment guard
Fix member name stripping at sheet read
Update summary command output format
```

## Pull Request Guidelines

- Keep PRs focused — one feature or fix per PR
- Reference any related issue in the PR description (e.g., `Closes #12`)
- Ensure all tests pass before requesting review
- Update the README if your change affects usage or setup

## Reporting Issues

Use the GitHub Issues tab. Fill in the provided template completely — include steps to reproduce, expected behavior, and actual behavior.

## Code Style

- Follow PEP 8
- No unnecessary comments — let well-named code speak for itself
- Keep functions small and focused

## Questions

Open a GitHub Discussion or an Issue tagged `question`.
