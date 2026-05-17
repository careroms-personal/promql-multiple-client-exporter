# promql-multiple-client-exporter — Python Guide
<!-- last human review: 2026 May 13 -->
<!-- last ai update: 2026 May 15 -->

Coding conventions for this codebase.
See `AI-PROGRAM-GUIDE.md` for architecture. See `AI-CONFIG-GUIDE.md` for config structure.

---

## Coding Conventions

- **Indentation:** 2 spaces — never 4 spaces or tabs
- **Error prefix:** `❌` for all fatal errors
- **Exit:** `sys.exit(1)` on any fatal error
- **YAML parsing:** `yaml.safe_load()` only — `yaml.load()` is forbidden
- **Config validation:** always validate with Pydantic before use — never access raw yaml_data fields directly
- **Secret safety:** never print, log, or embed config values that may contain secrets

---

## Error Handling Pattern

```python
if not Path(path).exists():
  print(f"❌ File not found: {path}")
  sys.exit(1)

try:
  ...
except ValidationError as e:
  print(f"❌ Invalid config file:")
  for error in e.errors():
    print(f"   - {error['loc']}: {error['msg']}")
  sys.exit(1)
```

---

## CLI Entry Point (`main.py`)

No logic here — only wires CLI args to Processor.

```python
import argparse
from processor.processor import Processor

def main():
  parser = argparse.ArgumentParser(description="...")
  parser.add_argument("-c", "--config", required=True, help="Path to config YAML file")
  args = parser.parse_args()

  processor = Processor(args.config)
  processor.execute()

if __name__ == "__main__":
  main()
```

---

## Naming Conventions

- Executor files: `<duty>_executor.py` in `program/processor/executors/`
- Executor result models: `<duty>_models.py` in `program/models/executors/`
- Config template models: match the YAML filename in `program/models/config_templates/`
- Test files: prefix with `test_` in `program/test_suits/`

---

## Testing Patterns

Tests live in `program/test_suits/`. File names must be prefixed with `test_`.

```python
import pytest
from processor.processor import Processor

def test_config_not_found():
  with pytest.raises(SystemExit):
    Processor("nonexistent.yaml")
```

Shared fixtures and constants go in `global_test_config.py`.

Run tests with:
```bash
pytest program/test_suits/
```

---

## Dependencies

Managed in `pyproject.toml` only — never `requirements.txt`.

Current dependencies:
- `pydantic==2.12.5` — config and result model validation
- `PyYAML==6.0.3` — YAML parsing
- `requests>=2.31.0` — HTTP (for Prometheus API calls)
- `pytest==9.0.2` — testing
