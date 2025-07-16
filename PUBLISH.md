# Publishing to PyPI

This guide explains how to publish the Laplace Python SDK to PyPI.

## Prerequisites

1. **PyPI Account**: Create accounts on both:
   - [PyPI](https://pypi.org/account/register/) (production)
   - [TestPyPI](https://test.pypi.org/account/register/) (testing)

2. **API Tokens**: Generate API tokens from your PyPI account settings for secure authentication.

## Setup

### 1. Install Build Tools

```bash
source venv/bin/activate
pip install build twine
```

### 2. Configure PyPI Credentials

Create a `~/.pypirc` file with your credentials:

```ini
[distutils]
index-servers =
    pypi
    testpypi

[pypi]
repository = https://upload.pypi.org/legacy/
username = __token__
password = <your-pypi-api-token>

[testpypi]
repository = https://test.pypi.org/legacy/
username = __token__
password = <your-testpypi-api-token>
```

## Publishing Process

### 1. Run Tests

```bash
source venv/bin/activate
python -m pytest tests/ -v
```

### 2. Update Version

Update version in `pyproject.toml`:

```toml
[project]
name = "laplace-python-sdk"
version = "0.1.0"  # Update this
```

### 3. Build Package

```bash
source venv/bin/activate
python -m build
```

This creates:
- `dist/laplace_python_sdk-VERSION-py3-none-any.whl`
- `dist/laplace_python_sdk-VERSION.tar.gz`

### 4. Check Package

```bash
source venv/bin/activate
python -m twine check dist/*
```

### 5. Test Upload (TestPyPI)

```bash
source venv/bin/activate
python -m twine upload --repository testpypi dist/*
```

Test installation:

```bash
pip install --index-url https://test.pypi.org/simple/ laplace-python-sdk
```

### 6. Production Upload (PyPI)

```bash
source venv/bin/activate
python -m twine upload dist/*
```

## Post-Publishing

### 1. Test Installation

```bash
pip install laplace-python-sdk
```

### 2. Test Basic Usage

```python
from laplace import LaplaceClient

client = LaplaceClient(api_key="your-api-key")
stocks = client.stocks.get_all(region="us", page=1, page_size=5)
print(f"Found {len(stocks)} stocks")
```

### 3. Create Git Tag

```bash
git tag v0.1.0
git push origin v0.1.0
```

## Package Structure

The built package includes:

```
laplace_python_sdk-0.1.0/
├── README.md
├── LICENSE
├── pyproject.toml
└── src/laplace/
    ├── __init__.py
    ├── base.py
    ├── client.py
    ├── collections.py
    ├── financials.py
    ├── funds.py
    ├── li.py
    ├── models.py
    └── stocks.py
```

## Version Management

### Semantic Versioning

- `MAJOR.MINOR.PATCH` (e.g., `1.0.0`)
- **MAJOR**: Breaking changes
- **MINOR**: New features, backward compatible
- **PATCH**: Bug fixes, backward compatible

### Version Examples

- `0.1.0` - Initial release
- `0.1.1` - Bug fix
- `0.2.0` - New features (collections, financials)
- `1.0.0` - First stable release

## Troubleshooting

### Common Issues

1. **Authentication Errors**
   - Ensure API tokens are correct
   - Check `~/.pypirc` configuration

2. **Package Name Conflicts**
   - Package name must be unique on PyPI
   - Consider alternative names if needed

3. **Build Errors**
   - Check `pyproject.toml` syntax
   - Ensure all dependencies are specified

### Clean Build

```bash
rm -rf dist/ build/ src/*.egg-info/
python -m build
```

## Current Status

✅ **Package Ready for Publishing**
- All tests passing
- Package built successfully
- Twine check passed
- Documentation complete

The package is now ready to be published to PyPI!