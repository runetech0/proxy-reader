# Proxy Reader Tests

This directory contains comprehensive tests for the `ProxiesReader` class.

## Test Files

- `test_reader.py` - Comprehensive test suite for the ProxiesReader class
- `__init__.py` - Makes tests a Python package

## Running Tests

### Option 1: Using pytest (Recommended)

First, install pytest:
```bash
pip install pytest
```

Then run the tests:
```bash
# Run all tests
pytest tests/ -v

# Run a specific test file
pytest tests/test_reader.py -v

# Run a specific test method
pytest tests/test_reader.py::TestProxiesReader::test_init_with_proxies_file -v
```

### Option 2: Using the test runner script

```bash
python run_tests.py
```

### Option 3: Basic functionality test

```bash
python test_basic.py
```

## Test Coverage

The test suite covers:

1. **Initialization Tests**
   - Creating ProxiesReader with proxies.txt file
   - Testing with check_proxies=True/False
   - Testing the load_list class method

2. **Proxy Parsing Tests**
   - Verifying proxy IP and port extraction
   - Testing HTTP, HTTPS, and SOCKS5 URL generation

3. **Random Proxy Methods**
   - get_random_http()
   - get_random_socks5()

4. **Sequential Proxy Methods**
   - next_http_from_list()
   - next_http_from_cycle()
   - next_socks5_from_list()
   - next_socks5_from_cycle()

5. **Telegram Proxy Format Tests**
   - next_http_telegram_from_list()
   - next_http_telegram_from_cycle()

6. **File Operations**
   - write_working_proxies()
   - get_working_proxies_list_http()

7. **Utility Methods**
   - String representation (__str__, __repr__)
   - Working proxies setter
   - Multiple proxies handling

8. **Error Handling**
   - File not found errors

## Test Data

The tests use the `proxies.txt` file in the project root, which contains:
```
23.95.150.145:6114
```

## Adding New Tests

To add new tests:

1. Add new test methods to the `TestProxiesReader` class in `test_reader.py`
2. Follow the naming convention: `test_<feature_name>()`
3. Add return type annotation: `-> None`
4. Include descriptive docstrings

Example:
```python
def test_new_feature(self) -> None:
    """Test description of what this test does"""
    # Test implementation
    pass
``` 