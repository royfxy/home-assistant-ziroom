# Tests

## Directory Structure

- `unit/` - Unit tests (don't require real API)
  - `test_ziroom_api.py` - Basic functionality tests for API client

- `integration/` - Integration tests (require real API token)
  - `test_light_control.py` - Test light control
  - `test_aircon_control.py` - Test air conditioner control
  - `test_curtain_control.py` - Test curtain control

## Setup

1. Create a `.env` file in the root directory:
   ```
   ZIROOM_TOKEN=your_token_here
   ```

2. Install dependencies (including dev dependencies):
   ```bash
   # Install in development mode with dev dependencies
   pip install -e ".[dev]"
   
   # Or install minimum dependencies separately
   pip install -r custom_components/ziroom/requirements.txt
   pip install python-dotenv
   ```

## Running Tests

### Unit Tests
```bash
python3 tests/unit/test_ziroom_api.py
```

### Integration Tests
```bash
# List all lights
python3 tests/integration/test_light_control.py

# Control light
python3 tests/integration/test_light_control.py --device <id> --off
```
