# Contributing to PixelGroomer

*[Deutsche Version](CONTRIBUTING.de.md)*

Thank you for considering contributing to PixelGroomer!

## Getting Started

1. Fork the repository
2. Clone your fork locally
3. Run the setup script:
   ```bash
   ./setup.sh
   ```
4. Create a feature branch:
   ```bash
   git checkout -b feature/your-feature-name
   ```

## Development Guidelines

### Languages

This project uses only two languages:

- **Bash** - For scripts and orchestration
- **Python** - For complex logic (EXIF, YAML, JSON)

Do not introduce other languages (Node.js, Ruby, Go, etc.).

### Bash Requirements

- Scripts must be compatible with Bash 3.2 (macOS default)
- All scripts must pass ShellCheck validation
- Python must always run inside the project's virtual environment

### Testing

All new features and bug fixes require tests:

```bash
make test          # Run all tests
make test-fast     # Skip slow tests
```

Tests must pass before submitting a pull request.

### Documentation

This project maintains bilingual documentation (English and German):

- Create both `*.en.md` and `*.de.md` versions
- Keep content synchronized between versions

### Commit Messages

Use action-prefixed commit messages:

```
created: add new feature
enhanced: improve existing functionality
fixed: correct a bug
refactored: restructure without behavior change
updated: dependency or config changes
removed: delete files or features
```

## Pull Request Process

1. Ensure all tests pass (`make test`)
2. Update documentation if needed (both EN and DE)
3. Follow the commit message format
4. Submit your pull request with a clear description

## Questions?

Open an issue if you have questions or need help getting started.
