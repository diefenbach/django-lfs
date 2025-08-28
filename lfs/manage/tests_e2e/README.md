# LFS Manage E2E Tests

End-to-End tests using Python Playwright for the LFS Management interface.

## Setup

### Prerequisites
```bash
# Install Playwright and browser
pip install pytest-playwright
playwright install chromium
```

### Structure
```
tests_e2e/
├── __init__.py                    # Package marker
├── conftest.py                    # Playwright fixtures and configuration
├── test_static_blocks_crud_e2e.py # StaticBlock CRUD user journey tests
└── README.md                      # This file
```

## Running E2E Tests

### All E2E tests
```bash
cd src/lfs/lfs/manage
pytest tests_e2e/
```

### Specific test file
```bash
pytest tests_e2e/test_static_blocks_crud_e2e.py
```

### With headed browser (visual debugging)
```bash
pytest tests_e2e/ --headed
```

### Slow down for debugging
```bash
pytest tests_e2e/ --headed --slowmo=1000
```

## Test Philosophy

### End-to-End Focus
- Test complete user workflows from login to completion
- Validate JavaScript functionality (Select All, Modals, HTMX)
- Test real browser interactions (clicks, form submissions, file uploads)

### Complement Unit Tests
- Unit tests: Fast, isolated, implementation details
- E2E tests: Slow, integrated, user behavior validation
- Both are needed for comprehensive coverage

## Test Scenarios

### StaticBlock CRUD Journey
1. **Authentication** - Login as manager
2. **Navigation** - Access StaticBlocks management
3. **Create** - Add new StaticBlock via modal
4. **Edit** - Modify StaticBlock data and files
5. **File Management** - Upload, select all, delete files
6. **Delete** - Remove StaticBlock with confirmation

### JavaScript Testing
- Modal opening/closing behavior
- Select All checkbox three-state functionality
- HTMX content swapping
- TinyMCE editor interactions
- Bootstrap component behavior

## Best Practices

### Test Independence
- Each test should be completely independent
- Use fresh test data for each test
- Clean up any created resources

### Reliable Selectors
- Prefer `data-testid` attributes over CSS classes
- Use semantic selectors when possible
- Avoid fragile selectors tied to styling

### Waiting Strategies
- Use `page.wait_for_selector()` for dynamic content
- Use `expect()` with automatic retries
- Avoid `time.sleep()` - use proper waits

### Error Handling
- Capture screenshots on failure
- Include detailed error messages
- Test both success and error scenarios

## Configuration

Tests use the Django `live_server` fixture to run against a real Django server instance with a test database.

Browser configuration is handled in `conftest.py` with sensible defaults for local development.
