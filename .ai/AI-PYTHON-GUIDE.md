# promql-multiple-client-exporter — AI Guide
<!-- last human review: 2026 May 13 -->
<!-- last ai update: 2026 May 14 -->

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
    │   ├── config_templates/
    │   │   ├── pipeline_config.py         # PipelineConfig, PipelineEntry, ConfigFiles
    │   │   ├── server_config.py           # ServerConfig, ServerEntry, AuthConfig
    │   │   ├── promql_config.py           # PromqlConfig, QueryEntry
    │   │   ├── range_config.py            # RangeConfig, RangeEntry
    │   │   ├── output_config.py           # OutputConfig, OutputEntry
    │   │   └── promql_query_export_sample.py  # PromqlQueryExportSample, PipelineEntry, OutputEntry, RangeBlock
    │   └── executors/
    │       ├── config_loader_models.py    # ConfigLoaderResult
    │       └── config_parser_models.py    # PromqlCombineQuery, PromqlRanges, PromqlRangeEntry
    ├── processor/
    │   ├── processor.py             # orchestrator: config load + executor chain
    │   └── executors/
    │       ├── config_loader_executor.py  # loads all sub-configs from pipeline file paths
    │       └── config_parser_executor.py  # parses/combines configs into query execution units
    ├── global_config.py             # reserved — do not add models here
    ├── config_templates/
    │   ├── pipeline_config.yaml           # top-level config: file refs + pipeline definitions
    │   ├── server_config.yaml             # Prometheus server list
    │   ├── promql_config.yaml             # PromQL query list
    │   ├── range_config.yaml              # time range list (datetime / timestamp / relative)
    │   ├── output_config.yaml             # output target list (csv / json / postgresql)
    │   └── promql_query_export_sample.yaml  # flattened single-pipeline export sample
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
| Config loader executor | `program/processor/executors/config_loader_executor.py` |
| Config parser executor | `program/processor/executors/config_parser_executor.py` |
| Pipeline config model | `program/models/config_templates/pipeline_config.py` |
| Server config model | `program/models/config_templates/server_config.py` |
| PromQL query config model | `program/models/config_templates/promql_config.py` |
| Time range config model | `program/models/config_templates/range_config.py` |
| Output config model | `program/models/config_templates/output_config.py` |
| Flattened export sample model | `program/models/config_templates/promql_query_export_sample.py` |
| Config loader result model | `program/models/executors/config_loader_models.py` |
| Config parser result models | `program/models/executors/config_parser_models.py` |
| YAML config templates | `program/config_templates/` |
| Test YAML configs | `program/test_suits/test_configs/` |
| Shared test fixtures | `program/test_suits/global_test_config.py` |
| Dependencies | `pyproject.toml` |

---

## Architecture: Processor + Executor Chain

```
pipeline_config.yaml
      ↓
  Processor
  ├─→ __init__: load + validate PipelineConfig → self.config
  ├─→ _set_pipeline_file_path(): inject resolved dir into self.config.pipeline_file_path
  └─→ execute():
        ├─→ ConfigLoaderExecutor(config).execute()              → ConfigLoaderResult
        └─→ ConfigParserExecutor(loader_result, config).execute() → ConfigParserResult (TBD)
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

Loads config, injects pipeline file path, chains executors. No business logic.

```python
import yaml, sys
from pathlib import Path
from pydantic import ValidationError
from models.config_templates.pipeline_config import PipelineConfig
from .executors.config_loader_executor import ConfigLoaderExecutor

class Processor:
  def __init__(self, config_path: str):
    self.config = self._load_and_validate_config(config_path=config_path)
    self._set_pipeline_file_path(config_path=config_path)

  def _load_and_validate_config(self, config_path: str):
    if not Path(config_path).exists():
      print(f"❌ Config file not found: {config_path}")
      sys.exit(1)
    try:
      with open(config_path, 'r') as f:
        yaml_data = yaml.safe_load(f)
      return PipelineConfig(**yaml_data)
    except ValidationError as e:
      print(f"❌ Invalid config file:")
      for error in e.errors():
        print(f"   - {error['loc']}: {error['msg']}")
      sys.exit(1)

  def _set_pipeline_file_path(self, config_path: str):
    self.config.pipeline_file_path = str(Path(config_path).resolve().parent)

  def execute(self):
    self.config_loader = ConfigLoaderExecutor(self.config)
    self.config_loader_result = self.config_loader.execute()
```

---

### 3. Executor (`<duty>_executor.py`)

One duty per executor. Receives previous result + full config. Returns typed model.

```python
from models.config_templates.pipeline_config import PipelineConfig
from models.executors.config_loader_models import ConfigLoaderResult
from models.executors.config_parser_models import ConfigParserResult

class ConfigParserExecutor:
  def __init__(self, loader_result: ConfigLoaderResult, config: PipelineConfig):
    self.loader_result = loader_result
    self.config = config

  def execute(self) -> ConfigParserResult:
    ...
```

**Naming:** `<duty>_executor.py` — lives in `program/processor/executors/`

---

### 4. Config Template Models (`models/config_templates/`)

One file per YAML config template. Each file owns its top-level model and sub-models.

```python
# models/config_templates/server_config.py
from pydantic import BaseModel
from typing import Literal, Optional

class AuthConfig(BaseModel):
  type: Literal["none", "bearer", "basic"] = "none"

class ServerEntry(BaseModel):
  id: str
  url: str
  api: str = "api/v1"
  timeout: int
  auth: Optional[AuthConfig] = None

class ServerConfig(BaseModel):
  servers: list[ServerEntry]
```

---

### 5. Executor Result Models (`models/executors/`)

Typed outputs passed between executors by Processor.

```python
# models/executors/config_loader_models.py
from pydantic import BaseModel
from typing import Optional
from models.config_templates.promql_config import PromqlConfig
from models.config_templates.server_config import ServerConfig
from models.config_templates.output_config import OutputConfig
from models.config_templates.range_config import RangeConfig

class ConfigLoaderResult(BaseModel):
  promql_config: PromqlConfig
  output_config: OutputConfig
  server_config: ServerConfig
  range_config: Optional[RangeConfig] = None
```

---

### 6. YAML Config Templates (`config_templates/`)

Mirror the pydantic model structure. Use `REQUEST` as placeholder for required values.

```yaml
# server_config.yaml
servers:
  - id: REQUEST
    url: REQUEST
    timeout: 30
    auth:
      type: none
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
