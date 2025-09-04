# Contributing to Qreu

Thank you for considering contributing to Qreu! This document provides guidelines for contributing to this email wrapper library.

## Python Version Compatibility

**Important:** Qreu maintains compatibility with Python 2.7 and Python 3.5-3.12. All contributions must work across this range.

### Compatibility Guidelines

- **No f-strings** - Use `.format()` or `%` formatting for Python 2.7 compatibility
- **Import compatibility** - Use `from __future__ import` statements when needed
- **Use `six` library** - For Python 2/3 compatibility utilities
- **Type hints** - Use comment-style type hints for Python 2.7: `# type: str`
- **String handling** - Be mindful of bytes vs unicode differences

Example of compatible code:

```python
# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

import six

def format_email(name, domain):
    # type: (str, str) -> str
    """Format an email address."""
    return "{0}@{1}".format(name, domain)

if six.PY2:
    from StringIO import StringIO
else:
    from io import StringIO
```

## Development Setup

1. Fork the repository
2. Clone your fork:
   ```bash
   git clone https://github.com/your-username/qreu.git
   cd qreu
   ```

3. Install development dependencies:
   ```bash
   pip install -r requirements-dev.txt
   pip install -e .
   ```

4. Run tests to ensure everything works:
   ```bash
   mamba
   ```

## Testing

- All changes must include tests
- Tests must pass on Python 2.7 and Python 3.5-3.12
- Use `mamba` for running tests
- Maintain or improve test coverage

### Running Tests

```bash
# Run all tests
mamba

# Run with coverage (if available)
mamba --enable-coverage
```

## Code Style

- Use 4 spaces for indentation
- Follow PEP 8 where possible, with Python 2.7 constraints
- Include docstrings for public functions and classes
- Use meaningful variable names
- Add comments for complex logic

## Pull Request Process

1. Create a feature branch from master
2. Make your changes
3. Add tests for new functionality
4. Ensure all tests pass on both Python 2.7 and 3.x
5. Update documentation if needed
6. Submit a pull request with a clear description

### Pull Request Checklist

- [ ] Code works on Python 2.7 and 3.5-3.12
- [ ] Tests added for new functionality
- [ ] All tests pass
- [ ] Documentation updated if needed
- [ ] Follows existing code style
- [ ] No breaking changes (or clearly documented)

## Reporting Issues

- Use the GitHub issue tracker
- Include Python version and operating system
- Provide a minimal example that reproduces the issue
- Include full error messages and stack traces

## Questions?

Feel free to open an issue for questions about contributing.