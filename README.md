# promql-multiple-client-exporter

A Python CLI tool for querying multiple Prometheus servers via PromQL, with configurable time ranges and multi-format export (CSV, JSON, PostgreSQL).

---

## Features

- Query **multiple Prometheus servers** in a single run
- Supports **instant** and **range** queries
- Three time range types: `datetime`, `timestamp`, `relative` (e.g. `now-24h`)
- Export results to **CSV**, **JSON**, or **PostgreSQL** simultaneously
- Pipeline-based config: one pipeline entry cross-joins servers × queries × ranges × outputs
- Generates a flattened export YAML before execution for inspection

---

## Requirements

- Python >= 3.9

---

## Installation

```bash
pip install -e .
```

---

## Usage

```bash
python -m program.app.main -c path/to/pipeline_config.yaml
```

The `-c` / `--config` flag points to your `pipeline_config.yaml`. All other config files are resolved relative to the directory containing that file.

---

## Configuration

The tool is driven by five YAML config files. `pipeline_config.yaml` is the entry point and references the rest.

### pipeline_config.yaml

```yaml
yaml_export_config:             # optional — write flattened plan to YAML before running
  output_file_name: "output.yaml"
  export_version: "1.0"

config_files:
  promql: "promql_config.yaml"
  range: "range_config.yaml"   # optional — omit for instant-only pipelines
  server: "server_config.yaml"
  output: "output_config.yaml"

pipelines:
  - id: "pipeline_1"
    name: "Pipeline 1"
    description: "Instant query across two servers"
    promqls:
      - "query_1"
    servers:
      - "server_prod"
      - "server_staging"
    outputs:
      - "csv_output"

  - id: "pipeline_2"
    name: "Pipeline 2"
    description: "Range query with time window"
    promqls:
      - "query_range_1"
    ranges:
      - "last_24h"
    servers:
      - "server_prod"
    outputs:
      - "csv_output"
      - "pg_store"
```

### server_config.yaml

```yaml
servers:
  - id: server_prod
    url: "http://prometheus.example.com:9090"
    api: "api/v1"      # optional, default: api/v1
    timeout: 30
    auth:
      type: none        # none / bearer / basic

  - id: server_staging
    url: "http://prometheus-staging.example.com:9090"
    timeout: 30
```

### promql_config.yaml

```yaml
queries:
  - id: "query_1"
    query: "up{job='node_exporter'}"
    type: instant
    export_labels:
      - "instance"
      - "job"

  - id: "query_range_1"
    query: "cpu_usage_seconds_total{job='node_exporter'}"
    type: range
    export_labels:
      - "instance"
      - "job"
```

### range_config.yaml

Three supported range types:

```yaml
ranges:
  - id: range_datetime
    type: datetime
    step: 15s
    start: 2026-01-01T00:00:00Z
    end: 2026-01-02T00:00:00Z

  - id: range_timestamp
    type: timestamp
    step: 15s
    start: 1767225600
    end: 1767312000

  - id: last_24h
    type: relative
    step: 15s
    start: now-24h
    end: now
```

Relative offsets support: `s`, `m`, `h`, `d`, `w`, `M`.

### output_config.yaml

```yaml
outputs:
  - id: "csv_output"
    type: "csv"
    file_path: "output_{query_id}.csv"
    include_labels: true

  - id: "json_output"
    type: "json"
    file_path: "output_{query_id}.json"
    include_labels: true

  - id: "pg_store"
    type: "postgresql"
    connection_string: "postgresql://user:password@localhost:5432/db"
    table_name: "prometheus_data"
```

Multiple outputs can be listed in a pipeline — the query executes once and writes to all outputs simultaneously.

---

## Project Structure

```
promql-multiple-client-exporter/
├── pyproject.toml
├── program/
│   ├── app/
│   │   └── main.py                     # CLI entry point
│   ├── config_templates/               # example YAML configs
│   ├── models/
│   │   ├── config_templates/           # Pydantic models for each config file
│   │   └── executors/                  # Pydantic result models
│   ├── processor/
│   │   ├── processor.py                # orchestrates executor chain
│   │   └── executors/
│   │       ├── config_loader_executor.py
│   │       ├── config_parser_executor.py
│   │       ├── config_exporter_executor.py
│   │       └── query_runner_executor.py
│   └── test_suits/
│       └── test_configs/               # YAML configs used in tests
└── .ai/                                # AI assistant guides
```

---

## License

See [LICENSE](LICENSE).
