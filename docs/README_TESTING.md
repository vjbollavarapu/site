# Testing Guide

This document provides information about running tests and achieving code coverage.

## Test Structure

The test suite is organized by app:

```
apps/
├── contacts/tests/
│   ├── factories.py          # Test data factories
│   ├── test_models.py        # Model tests
│   ├── test_serializers.py   # Serializer tests
│   ├── test_api_views.py     # API endpoint tests
│   ├── test_services.py      # Service tests
│   ├── test_permissions.py   # Permission tests
│   └── test_rate_limiting.py # Rate limiting tests
├── waitlist/tests/
├── leads/tests/
├── newsletter/tests/
├── analytics/tests/
├── gdpr/tests/
└── integrations/tests/
```

## Running Tests

### Run all tests
```bash
python manage.py test
```

### Run tests for a specific app
```bash
python manage.py test apps.contacts
python manage.py test apps.waitlist
python manage.py test apps.leads
```

### Run a specific test class
```bash
python manage.py test apps.contacts.tests.test_models.ContactSubmissionModelTest
```

### Run a specific test method
```bash
python manage.py test apps.contacts.tests.test_models.ContactSubmissionModelTest.test_create_contact_submission
```

### Run with verbose output
```bash
python manage.py test --verbosity=2
```

### Run with coverage
```bash
coverage run --source='.' manage.py test
coverage report
coverage html  # Generate HTML report in htmlcov/
```

## Test Coverage

Target: **80%+ code coverage**

### Generate coverage report
```bash
# Run tests with coverage
coverage run --source='.' manage.py test

# View text report
coverage report

# Generate HTML report
coverage html

# Open HTML report
open htmlcov/index.html  # macOS
# or
xdg-open htmlcov/index.html  # Linux
```

### Coverage exclusions
The following are excluded from coverage:
- Migration files
- Test files
- Virtual environment
- Settings files
- WSGI/ASGI files

## Test Categories

### 1. Model Tests (`test_models.py`)
- Model creation
- Model methods
- Model constraints
- Model relationships
- Model validation

### 2. Serializer Tests (`test_serializers.py`)
- Serializer validation
- Data transformation
- Field validation
- Required fields
- Custom validation logic

### 3. API View Tests (`test_api_views.py`)
- GET requests
- POST requests
- PATCH requests
- DELETE requests
- Success cases
- Error cases
- Response formats

### 4. Service Tests (`test_services.py`)
- Email service
- CRM service
- Spam detection
- Anonymization service
- External API integration (mocked)

### 5. Permission Tests (`test_permissions.py`)
- Public endpoints (AllowAny)
- Admin-only endpoints
- Staff permissions
- Authentication requirements

### 6. Rate Limiting Tests (`test_rate_limiting.py`)
- Rate limit enforcement
- Rate limit exceptions
- IP-based limiting

## Test Data Factories

We use `factory_boy` for generating test data:

```python
from apps.contacts.tests.factories import ContactSubmissionFactory

# Create a single instance
contact = ContactSubmissionFactory()

# Create multiple instances
contacts = ContactSubmissionFactory.create_batch(5)

# Create with specific attributes
contact = ContactSubmissionFactory(email='test@example.com', status='new')
```

## Mocking External Services

External services are mocked in tests:

```python
from unittest.mock import patch, MagicMock

@patch('apps.contacts.views.email_service')
def test_send_email(self, mock_email):
    mock_email.send_contact_confirmation = MagicMock()
    # ... test code ...
    mock_email.send_contact_confirmation.assert_called_once()
```

## Continuous Integration

Tests should be run in CI/CD pipeline:

```yaml
# Example GitHub Actions
- name: Run tests
  run: |
    python manage.py test
    coverage run --source='.' manage.py test
    coverage report --fail-under=80
```

## Best Practices

1. **Isolation**: Each test should be independent
2. **Naming**: Use descriptive test method names
3. **Arrange-Act-Assert**: Structure tests clearly
4. **Mocking**: Mock external dependencies
5. **Coverage**: Aim for 80%+ coverage
6. **Speed**: Keep tests fast
7. **Clarity**: Tests should be easy to understand

## Troubleshooting

### Database issues
```bash
# Reset test database
python manage.py test --keepdb
```

### Import errors
```bash
# Ensure all apps are in INSTALLED_APPS
# Check PYTHONPATH
```

### Coverage not working
```bash
# Ensure coverage is installed
pip install coverage

# Check .coveragerc configuration
```

