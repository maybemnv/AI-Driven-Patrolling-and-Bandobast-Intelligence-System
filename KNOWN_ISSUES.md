# Known Issues and Resolution Log

This document tracks bugs, issues, and limitations encountered during the End-to-End Testing and Verification phase.

## Resolved Issues

### 1. ONNX Runtime Installation

- **Issue**: `ModuleNotFoundError: No module named 'onnxruntime'` persisted even after `uv add onnxruntime` reported success.
- **Cause**: Potential package corruption or environment mismatch in `uv` on Windows.
- **Resolution**: explicitly uninstalled and reinstalled via `uv pip`:
  ```bash
  uv pip uninstall onnxruntime
  uv pip install onnxruntime
  ```

### 2. CopMap Endpoint 404

- **Issue**: `POST /api/v1/copmap/webhook` returned 404 Not Found.
- **Cause**: The API route was actually defined at `/api/v1/copmap/alerts` (sending) and `/api/v1/copmap/mock-receiver` (receiving). The `/webhook` path was incorrect in the test plan.
- **Resolution**: Updated validation scripts to use `/api/v1/copmap/alerts`.

### 3. Realtime Alerts Response Format

- **Issue**: Integration tests failed with `AttributeError: 'list' object has no attribute 'get'` when accessing `/realtime-alerts`.
- **Cause**: The endpoint returns a direct `list` of alerts in some cases (or when wrapped in `value` key depending on pagination/filtering), causing inconsistent parsing.
- **Resolution**: Updated `run_integration_tests.py` to handle both `list` and `dict` (with "value" key) response formats.

### 4. Database Schema Mismatch

- **Issue**: `OperationalError: no such column: patrol_sessions.zone`.
- **Cause**: The existing SQLite database did not match the latest SQLAlchemy models (missing columns).
- **Resolution**: Re-ran database initialization (`init_db.py`) to recreate the schema with all required columns.

### 5. LLM Service Signature Mismatch

- **Issue**: `TypeError` in `summarizer.py` when calling `get_llm_service(model=...)`.
- **Cause**: The `get_llm_service` function signature did not accept arguments.
- **Resolution**: Removed arguments from the call site to match the definition.

## Known Limitations

### 1. Environment Management on Windows

- **Description**: Managing complex dependencies (like `onnxruntime` + `ultralytics`) with `uv` on Windows caused path/import issues.
- **Workaround**: Use `uv pip uninstall/install` to force clean installation if imports fail.

### 2. LLM Token Speed

- **Description**: LLM generation speed via API detected as extremely fast (~1500 tokens/sec), likely due to high-performance provider (Groq).
- **Note**: Ensure rate limits are monitored if traffic scales.

### 3. Docker Persistence

- **Description**: `compose.yaml` uses named volumes.
- **Note**: Ensure `db-data` volume is backed up before container teardown in production.
