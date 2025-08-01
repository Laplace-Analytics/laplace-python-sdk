# Testing Guide

This directory contains comprehensive tests for the Laplace Python SDK.

## Test Types

### Unit Tests
- **test_base_client.py**: Tests for base client functionality
- Mock all external dependencies
- Fast execution, no network calls

### Integration Tests
- **test_stocks_integration.py**: Tests for stocks client with real API responses
- **test_collections_integration.py**: Tests for collections client with real API responses
- **test_politician_integration.py**: Tests for politician client with real API responses
- Use mocked responses based on real API calls
- Test both mocked and real API scenarios

## Setup

### Create Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### Install Dependencies
```bash
pip install --upgrade pip
pip install pytest pytest-asyncio httpx pydantic typing-extensions
pip install -e .
```

## Running Tests

### Run All Tests
```bash
source venv/bin/activate
pytest
```

### Run Unit Tests Only
```bash
pytest -m "not integration"
```

### Run Integration Tests Only
```bash
pytest -m integration
```

### Run Specific Test File
```bash
pytest tests/test_stocks_integration.py
```

### Run with Verbose Output
```bash
pytest -v
```

### Run with Coverage (optional)
```bash
pip install pytest-cov
pytest --cov=laplace --cov-report=html
```

## Integration Tests with Real API

Some tests are marked with `@pytest.mark.integration` and require a real API key.

To run these tests:
1. Set the `LAPLACE_API_KEY` environment variable:
   ```bash
   export LAPLACE_API_KEY="your-api-key-here"
   ```

2. Run integration tests:
   ```bash
   LAPLACE_API_KEY=your-api-key pytest -m integration
   ```

## Test Results

✅ **All tests are currently passing:**
- **20 passed** - All mocked integration tests and unit tests
- **4 skipped** - Real API integration tests (require API key)
- **4 warnings** - Minor pytest marker warnings (can be ignored)

## Test Configuration

- **pytest.ini**: Pytest configuration with custom markers
- **conftest.py**: Shared fixtures and test utilities
- Tests use real API responses captured from actual API calls
- Mocking is used to avoid network calls during regular test runs
- Virtual environment ensures isolated dependencies

## Writing New Tests

When adding new endpoints:
1. **Get real API responses** by calling the endpoint with a real API key
2. **Create mocked tests** using the real response data in the test files
3. **Add integration tests** that use real API calls (marked with `@pytest.mark.integration`)
4. **Follow existing patterns** in `test_stocks_integration.py` and `test_collections_integration.py`
5. **Test field mapping** to ensure Pydantic aliases work correctly
6. **Test error scenarios** for validation and edge cases

## Test Structure

```
tests/
├── __init__.py
├── conftest.py                      # Test fixtures and utilities
├── test_base_client.py              # Base client unit tests
├── test_stocks_integration.py       # Stocks client integration tests
├── test_collections_integration.py  # Collections client integration tests
├── test_politician_integration.py   # Politician client integration tests
└── README.md                       # This file
```

## Current Test Coverage

- ✅ **Base Client**: Authentication, error handling, request methods
- ✅ **Stocks Client**: All endpoints with real API responses
- ✅ **Collections Client**: All endpoints with real API responses
- ✅ **Politician Client**: All endpoints with real API responses
- ✅ **Field Mapping**: Pydantic model validation and aliases
- ✅ **Error Handling**: Invalid regions, HTTP errors, network errors
- ✅ **Real API Integration**: Tests with actual API calls