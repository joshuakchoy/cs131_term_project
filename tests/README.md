# Pytest Test Suite

## Overview
This test suite contains **8 meaningful unit tests** covering models, routes, and forms.

## Test Results
✅ **All 8 tests passing**

## Test Coverage

### Models (3 tests)
1. **test_user_password_hashing** - Verifies password hashing and verification works correctly
2. **test_user_creation_with_role** - Tests creating users with different roles (student, instructor)
3. **test_course_creation** - Tests course creation and instructor relationship

### Routes (4 tests)
4. **test_login_page_accessible** - Verifies login page loads successfully
5. **test_login_with_valid_credentials** - Tests successful login with correct credentials
6. **test_assignments_requires_login** - Ensures protected routes require authentication
7. **test_authenticated_user_can_access_assignments** - Verifies authenticated users can access assignments

### Forms (1 test)
8. **test_registration_form_validates_matching_passwords** - Tests form validation for matching passwords

## Running Tests

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run specific test file
pytest tests/test_models.py

# Run specific test
pytest tests/test_models.py::TestUserModel::test_user_password_hashing
```

## Test Files
- `conftest.py` - Pytest configuration and fixtures
- `test_models.py` - Model tests
- `test_routes.py` - Route/view tests
- `test_forms.py` - Form validation tests
- `pytest.ini` - Pytest configuration
