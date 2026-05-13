# pyconfplate — AI Guide
<!-- last human review: 2026 May 13 -->
<!-- last ai update: 2026 May 13 -->

Quick reference for AI assistants working in this codebase.
See `vibe-code-rule.yaml` for project rules.

---

## Project Purpose

CLI tool that reads a pipeline YAML config and runs PromQL queries against multiple Prometheus servers, then exports results to configured outputs (CSV, JSON, PostgreSQL).

---

## Project Structure

```
promql-multiple-client-exporter/
├── vibe-code-rule.yaml              # AI instruction manifest — read first
├── pyproject.toml                   # dependencies and build config (only place for deps)
├── .ai/
│   ├── AI-PRINCIPLE-GUIDE.md        # design principles
│   └── AI-PYTHON-GUIDE.md           # this file
└── program/
    ├── app/
    │   └── main.py                  # CLI entry point — do not add logic here
    ├── models/
    │   ├── pipeline_config.py       # PipelineConfig, PipelineEntry, ConfigFiles
    │   ├── server_config.py         # ServerConfig, ServerEntry, AuthConfig
    │   ├── promql_config.py         # PromqlConfig, QueryEntry
    │   ├── range_config.py          # RangeConfig, RangeEntry
    │   └── output_config.py         # OutputConfig, OutputEntry
    ├── processor/
    │   ├── processor.py             # orchestrator: config load + executor chain
    │   └── <duty>_executor.py       # one file per executor (to be added)
    ├── global_config.py             # reserved — do not add models here
    ├── config_templates/
    │   ├── pipeline_config.yaml     # top-level config: file refs + pipeline definitions
    │   ├── server_config.yaml       # Prometheus server list
    │   ├── promql_config.yaml       # PromQL query list
    │   ├── range_config.yaml        # time range list (datetime / timestamp / relative)
    │   └── output_config.yaml       # output target list (csv / json / postgresql)
    └── test_suits/
        ├── global_test_config.py    # shared test fixtures/constants
        └── test_configs/
            ├── test_pipeline.yaml
            ├── test_server.yaml
            ├── test_promql.yaml
            ├── test_range.yaml
            └── test_output.yaml
```

---

## How to Look Things Up

| What you need | Where to look |
|---|---|
| CLI argument parsing | `program/app/main.py` |
| Executor chain and flow | `program/processor/processor.py` |
| Base executor contract | `program/processor/base_executor.py` |
| Pipeline config model | `program/models/pipeline_config.py` |
| Server config model | `program/models/server_config.py` |
| PromQL query config model | `program/models/promql_config.py` |
| Time range config model | `program/models/range_config.py` |
| Output config model | `program/models/output_config.py` |
| YAML config templates | `program/config_templates/` |
| Test YAML configs | `program/test_suits/test_configs/` |
| Shared test fixtures | `program/test_suits/global_test_config.py` |
| Dependencies | `pyproject.toml` |

---

## Architecture: Processor + Executor Chain

```
YAML Config File
      ↓
  Processor
  ├─→ __init__: load + validate config → self.config
  └─→ execute():
        ├─→ FirstExecutor(config).execute()            → ResultA
        ├─→ SecondExecutor(result_a, config).execute() → ResultB
        └─→ ThirdExecutor(result_b, config).execute()  → (side effects / final output)
```

**Rules:**
- Processor holds all executor instances and their results as `self.*`
- Each executor receives the full config — it extracts only what it needs
- Each executor returns a typed pydantic model (never a plain dict or tuple)
- Executors do not call each other — Processor manages the chain

---

## Coding Conventions

- **Indentation:** 2 spaces — never 4 spaces or tabs
- **Error prefix:** `❌` for all fatal errors
- **Exit:** `sys.exit(1)` on any fatal error

---

## Core Patterns

### 1. CLI Entry Point (`main.py`)

No logic here — only wires CLI args to Processor.

```python
import argparse
from processor.processor import Processor

def main():
  parser = argparse.ArgumentParser(description="<program description>")
  parser.add_argument("-c", "--config", required=True, help="Path to config Yaml file")
  args = parser.parse_args()

  processor = Processor(args.config)
  processor.execute()

if __name__ == "__main__":
  main()
```

---

### 2. Processor (`processor.py`)

Loads config, chains executors. No business logic.

```python
import yaml, sys
from pathlib import Path
from pydantic import ValidationError
from models.config_models import AppConfig
from processor.first_executor import FirstExecutor
from processor.second_executor import SecondExecutor

class Processor:
  def __init__(self, config_path: str):
    self.config = self._load_and_validate_config(config_path)

  def _load_and_validate_config(self, config_path: str) -> AppConfig:
    if not Path(config_path).exists():
      print(f"❌ Config file not found: {config_path}")
      sys.exit(1)
    try:
      with open(config_path, 'r') as f:
        yaml_data = yaml.safe_load(f)
      return AppConfig(**yaml_data)
    except ValidationError as e:
      print(f"❌ Invalid config file:")
      for error in e.errors():
        print(f"   - {error['loc']}: {error['msg']}")
      sys.exit(1)

  def execute(self):
    self.first_executor = FirstExecutor(self.config)
    self.first_result = self.first_executor.execute()

    self.second_executor = SecondExecutor(self.first_result, self.config)
    self.second_result = self.second_executor.execute()
```

---

### 3. Base Executor (`base_executor.py`)

All executors must inherit from `BaseExecutor`. It enforces the `execute()` contract.

```python
# program/processor/base_executor.py
from abc import ABC, abstractmethod
from typing import Any

class BaseExecutor(ABC):
  @abstractmethod
  def execute(self) -> Any:
    """Execute this executor's duty and return a typed result."""
    pass
```

---

### 4. Executor (`<duty>_executor.py`)

One duty per executor. Inherits `BaseExecutor`. Receives previous result + full config. Returns typed model.

```python
from processor.base_executor import BaseExecutor
from models.config_models import AppConfig
from models.result_models import FirstResult, SecondResult

class SecondExecutor(BaseExecutor):
  def __init__(self, first_result: FirstResult, config: AppConfig):
    self.first_result = first_result
    # extract only the config section this executor needs
    self.task_config = config.second_task_config

  def execute(self) -> SecondResult:
    data = self._process(self.first_result)
    return SecondResult(...)

  def _process(self, input: FirstResult) -> ...:
    ...
```

**Naming:** `<duty>_executor.py` — e.g., `data_prepare_executor.py`, `training_executor.py`

---

### 5. Config Models (`models/config_models.py`)

Top-level model validated on startup. Sub-models scoped to each executor's duty.

```python
from pydantic import BaseModel
from typing import Optional

class FirstTaskConfig(BaseModel):
  source: str
  timeout: int = 30

class SecondTaskConfig(BaseModel):
  output_dir: str

class AppConfig(BaseModel):
  first_task: FirstTaskConfig
  second_task: SecondTaskConfig
```

---

### 6. Result Models (`models/result_models.py`)

Typed outputs passed between executors by Processor.

```python
from pydantic import BaseModel

class FirstResult(BaseModel):
  data: list
  count: int

class SecondResult(BaseModel):
  output_path: str
  success: bool
```

---

### 7. YAML Config Template (`config_templates/config.yaml`)

Mirror the pydantic model structure. Use `REQUEST` as placeholder for values the user must fill in.

```yaml
first_task:
  source: REQUEST
  timeout: 30

second_task:
  output_dir: REQUEST
```

---

## Error Handling Convention

- File not found → `❌ Config file not found: <path>` + `sys.exit(1)`
- Pydantic validation error → `❌ Invalid config file:` + per-field errors + `sys.exit(1)`
- Always use `❌` prefix for fatal errors
- Never swallow exceptions silently

---

## Testing Patterns

Tests live in `program/test_suits/`. File names must be prefixed with `test_`.

```python
# program/test_suits/test_processor.py
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
- `requests>=2.31.0` — HTTP (available for use in executors)
- `pytest==9.0.2` — testing
