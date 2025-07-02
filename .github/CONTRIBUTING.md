# Contributing to whenami

Thank you for your interest in contributing to whenami!

## Development Setup

1. Clone the repository
2. Create a virtual environment: `python -m venv .venv`
3. Activate it: `source .venv/bin/activate` (Linux/Mac) or `.venv\Scripts\activate` (Windows)
4. Install in development mode: `pip install -e ".[dev]"`

## Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src/whenami --cov-report=term-missing

# Run specific test file
pytest tests/test_event_names.py -v
```

## GitHub Actions

This repository uses GitHub Actions for CI/CD:

### CI Pipeline (`.github/workflows/ci.yml`)
- **Triggers**: Push to main/master/develop, PRs
- **Tests**: Python 3.9, 3.10, 3.11, 3.12
- **Features**:
  - Installs dependencies
  - Runs linting (ruff) if available
  - Runs type checking (mypy) if available
  - Executes pytest with coverage
  - Uploads coverage to Codecov
  - Builds and validates package

### Publishing Pipeline (`.github/workflows/publish.yml`)
- **Triggers**: GitHub releases, manual workflow dispatch
- **Features**:
  - Builds package with proper validation
  - Publishes to PyPI using trusted publishing
  - Option to publish to Test PyPI for testing
  - Uses GitHub environments for security

### Security Pipeline (`.github/workflows/security.yml`)
- **Triggers**: Weekly schedule, PRs, manual dispatch
- **Features**:
  - Runs `safety` for vulnerability checks
  - Runs `bandit` for security linting
  - Dependency review for PRs

## Publishing Releases

1. Update version in `pyproject.toml`
2. Create a Git tag: `git tag v0.1.1`
3. Push tag: `git push origin v0.1.1`
4. Create a GitHub release from the tag
5. The publish workflow will automatically deploy to PyPI

## Environment Setup for PyPI Publishing

To use the publishing workflow, set up these GitHub repository secrets:

### For PyPI Trusted Publishing (Recommended)
1. Go to PyPI → Account Settings → Publishing
2. Add a "pending publisher" for your repository
3. Configure the GitHub environment named `pypi` in your repository settings

### For Test PyPI
1. Configure the GitHub environment named `test-pypi`
2. Use the workflow dispatch option with "Publish to Test PyPI" checked

## Code Style

- Follow PEP 8
- Use type hints where possible
- Write docstrings for public functions
- Add tests for new features
- Update README.md with new functionality

## Pull Request Process

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature`
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Update documentation as needed
7. Submit a pull request

The CI pipeline will automatically run tests and checks on your PR.