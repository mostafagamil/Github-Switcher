# Testing Documentation

GitHub Switcher maintains enterprise-grade quality with comprehensive test coverage and rigorous testing practices.

## Test Statistics

- **Total Tests**: 273
- **Test Coverage**: 99.58%
- **Success Rate**: 100%
- **Test Execution Time**: ~1 second
- **Missing Lines**: Only 4 lines uncovered (system-level entry points and deep error handling)

## Test Architecture

### Test Structure

```
tests/
├── test_cli.py          # CLI interface tests (40 tests)
├── test_config.py       # Configuration management tests (20 tests)
├── test_export.py       # Import/export functionality tests (31 tests)
├── test_git_manager.py  # Git operations tests (17 tests)
├── test_profiles.py     # Profile management tests (24 tests)
├── test_ssh_manager.py  # SSH key management tests (37 tests)
├── test_utils.py        # Utility functions tests (58 tests)
└── test_wizard.py       # Interactive wizard tests (46 tests)
```

### Coverage by Module

| Module | Statements | Missing | Coverage | Key Test Areas |
|--------|------------|---------|----------|----------------|
| CLI | 199 | 1 | 99% | Command parsing, argument validation, error handling |
| Config | 84 | 0 | 100% | File I/O, TOML parsing, profile management |
| Export | 77 | 0 | 100% | TOML/JSON/YAML export, import validation |
| Git Manager | 46 | 0 | 100% | Git command execution, configuration management |
| Profiles | 83 | 0 | 100% | Profile CRUD operations, validation |
| SSH Manager | 176 | 3 | 98% | Key generation, SSH config management |
| Utils | 96 | 0 | 100% | Cross-platform utilities, time formatting |
| Wizard | 196 | 0 | 100% | Interactive flows, user input handling |

**Total: 957 statements, 4 missing, 99.58% coverage**

## Test Categories

### 1. Unit Tests
Test individual functions and methods in isolation.

**Examples:**
- `test_validate_email()` - Email format validation
- `test_generate_ssh_key()` - SSH key generation
- `test_format_time_ago()` - Time formatting utilities

### 2. Integration Tests
Test interactions between modules and components.

**Examples:**
- `test_profile_creation_workflow()` - End-to-end profile creation
- `test_ssh_key_activation()` - SSH config file management
- `test_export_import_cycle()` - Complete export/import process

### 3. CLI Tests
Test command-line interface with comprehensive mocking.

**Examples:**
- `test_create_profile_interactive()` - Interactive profile creation
- `test_switch_profile_success()` - Profile switching commands
- `test_export_profiles_to_file()` - File export operations

### 4. Error Handling Tests
Test edge cases, error conditions, and recovery scenarios.

**Examples:**
- `test_invalid_email_format()` - Input validation
- `test_ssh_key_generation_failure()` - SSH key operation errors
- `test_file_permission_errors()` - File system error handling

### 5. Cross-Platform Tests
Ensure compatibility across different operating systems.

**Examples:**
- `test_expand_path_with_tilde()` - Path expansion on different systems
- `test_ssh_config_permissions()` - File permission handling
- `test_command_availability()` - System command detection

## Testing Best Practices

### Mocking Strategy

We use comprehensive mocking to:
- **Isolate units under test** from external dependencies
- **Control test environments** for predictable results
- **Simulate error conditions** that are hard to reproduce
- **Speed up test execution** by avoiding real I/O operations

### Test Fixtures

Reusable test components for consistent test setup:

```python
@pytest.fixture
def temp_config_dir():
    """Create a temporary configuration directory."""
    temp_dir = Path(tempfile.mkdtemp())
    yield temp_dir
    shutil.rmtree(temp_dir)

@pytest.fixture
def profile_manager(temp_config_dir):
    """Create a ProfileManager instance with temporary directory."""
    with patch('pathlib.Path.home', return_value=temp_config_dir.parent):
        manager = ProfileManager()
        manager.config.config_dir = temp_config_dir / "github-switcher"
        return manager
```

### Error Scenarios

Every module includes comprehensive error testing:

- **File system errors** (permissions, disk space, missing files)
- **Network errors** (connection failures, timeouts)
- **Input validation errors** (malformed data, invalid formats)
- **System command failures** (missing dependencies, command errors)
- **Configuration errors** (invalid TOML, missing sections)

## Running Tests

### Basic Test Execution

```bash
# Run all tests
uv run python -m pytest

# Run with coverage report
uv run python -m pytest --cov=github_switcher --cov-report=term-missing

# Run specific test file
uv run python -m pytest tests/test_cli.py

# Run specific test method
uv run python -m pytest tests/test_cli.py::TestCreateProfile::test_create_profile_success
```

### Advanced Test Options

```bash
# Run tests in parallel
uv run python -m pytest -n auto

# Run tests with verbose output
uv run python -m pytest -v

# Run only failed tests from last run
uv run python -m pytest --lf

# Run tests with coverage HTML report
uv run python -m pytest --cov=github_switcher --cov-report=html
```

### Test Categories

```bash
# Run only fast tests
uv run python -m pytest -m "not slow"

# Run only integration tests
uv run python -m pytest -k "integration"

# Run only CLI tests
uv run python -m pytest tests/test_cli.py
```

## Coverage Analysis

### Coverage Report Interpretation

```
Name                                 Stmts   Miss  Cover   Missing
------------------------------------------------------------------
src/github_switcher/cli.py             199      3    98%   299-300, 373
```

- **Stmts**: Total executable statements
- **Miss**: Uncovered statements
- **Cover**: Coverage percentage
- **Missing**: Line numbers of uncovered code

### Coverage Goals

- **Minimum Coverage**: 95% (enforced in CI)
- **Current Coverage**: 99.58%
- **Target Coverage**: Maintain >95% for all modules
- **Critical Paths**: 100% coverage for core functionality

## Continuous Integration

### Automated Testing

Tests run automatically on:
- **Every commit** to feature branches
- **Pull request creation** and updates
- **Merge to main branch**
- **Scheduled nightly builds**

### Quality Gates

Pull requests must pass:
- ✅ All 273 tests must pass
- ✅ Coverage must remain ≥95%
- ✅ No new linting errors
- ✅ Type checking must pass
- ✅ Documentation must build

## Test Maintenance

### Adding New Tests

When adding new functionality:

1. **Write tests first** (TDD approach)
2. **Cover happy path** scenarios
3. **Include error cases** and edge conditions
4. **Test user interactions** for CLI features
5. **Maintain existing coverage** percentage

### Test Review Checklist

- [ ] Tests cover all new code paths
- [ ] Error conditions are tested
- [ ] Mocking is appropriate and minimal
- [ ] Test names are descriptive
- [ ] Assertions are specific and clear
- [ ] Test data is realistic

### Debugging Failed Tests

```bash
# Run with detailed output
uv run python -m pytest -v -s

# Drop into debugger on failure
uv run python -m pytest --pdb

# Run specific test with full traceback
uv run python -m pytest tests/test_cli.py::test_specific_function --tb=long
```

## Performance Testing

While not part of the main test suite, performance considerations:

- **CLI startup time** should be <100ms
- **Profile switching** should complete in <500ms
- **SSH key generation** benchmarked and monitored
- **Large profile set handling** (100+ profiles) tested

## Security Testing

Security-focused testing includes:

- **Input validation** for all user inputs
- **File permission** verification for SSH keys
- **Path traversal** prevention in file operations
- **Credential exposure** prevention in logs/output

---

This comprehensive testing approach ensures GitHub Switcher maintains the highest quality standards while providing confidence for users and contributors.