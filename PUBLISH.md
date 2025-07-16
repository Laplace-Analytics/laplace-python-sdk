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

## Automated Publishing (GitHub Actions)

### GitHub Actions Workflow

The repository includes automated publishing via GitHub Actions:

#### **Publish Workflow** (`.github/workflows/publish.yml`)
- **Triggers**: When a new release is published on GitHub
- **Process**:
  1. Extracts version from git tag (e.g., `v1.0.0` → `1.0.0`)
  2. Updates `pyproject.toml` with the tag version
  3. Builds the package
  4. Runs package checks
  5. Publishes to PyPI using `PYPI_TOKEN` secret

#### **Test Workflow** (`.github/workflows/test.yml`)
- **Triggers**: On push to main/develop branches and pull requests
- **Process**:
  1. Tests across Python 3.8-3.12
  2. Runs full test suite
  3. Verifies package import
  4. Basic code linting

### Publishing a New Version

1. **Create and push a git tag**:
   ```bash
   git tag v1.0.0
   git push origin v1.0.0
   ```

2. **Create a GitHub Release**:
   - Go to GitHub → Releases → "Create a new release"
   - Choose the tag you just created
   - Fill in release notes
   - Click "Publish release"

3. **Automatic Publishing**:
   - GitHub Actions will automatically trigger
   - Package will be built and published to PyPI
   - Check the "Actions" tab for build status

### Repository Secrets

Ensure the following secret is configured in your GitHub repository:

- **`PYPI_TOKEN`**: Your PyPI API token
  - Go to Settings → Secrets and variables → Actions
  - Add new repository secret named `PYPI_TOKEN`
  - Value should be your PyPI API token

## Manual Publishing (Alternative)

If you prefer manual publishing, follow the original process:

### 1. Run Tests
```bash
source venv/bin/activate
python -m pytest tests/ -v
```

### 2. Update Version
Edit `pyproject.toml` and update the version number.

### 3. Build and Publish
```bash
source venv/bin/activate
python -m build
python -m twine check dist/*
python -m twine upload dist/*
```

## Current Status

✅ **Package Ready for Publishing**
- All tests passing
- Package built successfully
- Twine check passed
- Documentation complete
- GitHub Actions workflows configured
- Automated publishing ready

The package is now ready to be published to PyPI automatically via GitHub releases!