# promql-multiple-client-exporter — Config Guide
<!-- last human review: -->
<!-- last ai update: 2026 May 15 (embedded outputs in export sample) -->

Reference for all config template files. Each section shows the YAML structure and its matching Pydantic model.
See `vibe-code-rule.yaml` for project rules. See `AI-PROGRAM-GUIDE.md` for architecture.

---

## pipeline_config

Entry point config. References all other config files and defines pipelines.

**YAML:** `program/config_templates/pipeline_config.yaml`
**Model:** `program/models/config_templates/pipeline_config.py`

```yaml
yaml_export_config:             # optional
  output_file_name: "output.yaml"
  export_version: "1.0"

config_files:
  promql: "promql_config.yaml"
  range: "range_config.yaml"    # optional — omit for instant-only pipelines
  server: "server_config.yaml"
  output: "output_config.yaml"

pipelines:
  - id: "pipeline_1"
    name: "Pipeline 1"
    description: "..."
    promqls:
      - "query_id_1"
    ranges:                     # optional — omit for instant-only pipelines
      - "range_id_1"
    servers:
      - "server_id_1"
    outputs:
      - "output_id_1"
```

**Models:**
- `YamlExportConfig` — `output_file_name: str`, `export_version: str`
- `ConfigFiles` — `promql: str`, `range: Optional[str]`, `server: str`, `output: str`
- `PipelineEntry` — `id`, `name`, `description`, `promqls: list[str]`, `ranges: Optional[list[str]]`, `servers: list[str]`, `outputs: list[str]`
- `PipelineConfig` — `pipeline_file_path: Optional[str]` (injected by Processor, not in YAML), `yaml_export_config: Optional[YamlExportConfig]`, `config_files: ConfigFiles`, `pipelines: list[PipelineEntry]`

---

## server_config

Prometheus server list.

**YAML:** `program/config_templates/server_config.yaml`
**Model:** `program/models/config_templates/server_config.py`

```yaml
servers:
  - id: server_id
    url: "http://localhost:9090"
    api: "api/v1"     # optional, default: api/v1
    timeout: 30       # seconds (int)
    auth:             # optional
      type: none      # none / bearer / basic
```

**Models:**
- `AuthConfig` — `type: Literal["none", "bearer", "basic"]` default `"none"`
- `ServerEntry` — `id`, `url`, `api` (default `"api/v1"`), `timeout: int`, `auth: Optional[AuthConfig]`
- `ServerConfig` — `servers: list[ServerEntry]`

---

## promql_config

PromQL query list.

**YAML:** `program/config_templates/promql_config.yaml`
**Model:** `program/models/config_templates/promql_config.py`

```yaml
queries:
  - id: "query_id"
    query: "up{job='prometheus'}"
    type: instant     # instant / range
    export_labels:
      - "instance"
      - "job"
```

**Models:**
- `QueryEntry` — `id`, `query`, `type: Literal["instant", "range"]`, `export_labels: list[str]`
- `PromqlConfig` — `queries: list[QueryEntry]`

---

## range_config

Time range list. Three supported types.

**YAML:** `program/config_templates/range_config.yaml`
**Model:** `program/models/config_templates/range_config.py`

```yaml
ranges:
  - id: range_datetime
    type: datetime
    step: 15s
    start: 2026-01-01T00:00:00Z   # PyYAML parses this to datetime object
    end: 2026-01-02T00:00:00Z

  - id: range_timestamp
    type: timestamp
    step: 15s
    start: 1767225600             # Unix timestamp (int)
    end: 1767312000

  - id: range_relative
    type: relative
    step: 15s
    start: now-24h                # supports: now, now-Xs/m/h/d/w/M
    end: now
```

**Note:** PyYAML auto-parses ISO 8601 strings into `datetime` objects — `start`/`end` typed as `Union[str, int, datetime]` to handle all three cases.

**Models:**
- `RangeEntry` — `id`, `type: Literal["datetime", "timestamp", "relative"]`, `step: str`, `start: Union[str, int, datetime]`, `end: Union[str, int, datetime]`
- `RangeConfig` — `ranges: list[RangeEntry]`

---

## output_config

Output target list.

**YAML:** `program/config_templates/output_config.yaml`
**Model:** `program/models/config_templates/output_config.py`

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

**Models:**
- `OutputEntry` — `id`, `type: Literal["csv", "json", "postgresql"]`, `file_path: Optional[str]`, `include_labels: Optional[bool]`, `connection_string: Optional[str]`, `table_name: Optional[str]`
- `OutputConfig` — `outputs: list[OutputEntry]`

---

## promql_query_export_sample

Flattened export format. Output structure written by `ConfigExporterExecutor`.

**YAML:** `program/config_templates/promql_query_export_sample.yaml`
**Model:** `program/models/config_templates/promql_query_export_sample.py`

```yaml
pipelines:
  - id: "<generated_by_program>"
    pipeline_id: "pipeline_1"
    pipeline_description: "Instance query pipeline"
    query_id: "query_1"
    server_id: "server_1"
    type: "instance"          # instance / range
    url: "http://localhost:9090"
    api: "api/v1/query"
    auth: {}
    timeout: 30
    expr: "up{job='prometheus'}"
    export_labels: ["instance", "job"]
    outputs:                  # embedded — one query writes to all outputs simultaneously
      - id: "csv_output"
        type: "csv"
        file_path: "output.csv"
        include_labels: true
      - id: "pg_store"
        type: "postgresql"
        connection_string: "postgresql://user:password@localhost:5432/mydatabase"
        table_name: "prometheus_data"

  - id: "<generated_by_program>"
    pipeline_id: "pipeline_2"
    pipeline_description: "Range query pipeline"
    query_id: "query_2"
    server_id: "server_1"
    range_id: "range_1"       # optional, range queries only
    type: "range"
    url: "http://localhost:9090"
    api: "api/v1/query_range"
    auth: {}
    timeout: 30
    expr: "cpu_usage_seconds_total{job='node'}"
    export_labels: ["instance", "job"]
    range:                    # optional, range queries only
      start: 1700000000
      end: 1700003600
      step: "15s"
    outputs:
      - id: "csv_output"
        type: "csv"
        file_path: "output.csv"
        include_labels: true
      - id: "pg_store"
        type: "postgresql"
        connection_string: "postgresql://user:password@localhost:5432/mydatabase"
        table_name: "prometheus_data"
```

**Design note:** `outputs` is embedded per pipeline entry — one query execution writes to all outputs simultaneously. No top-level `outputs` section.

**Models:**
- `RangeBlock` — `start: int`, `end: int`, `step: str`
- `OutputExportEntry` — `id`, `type`, `file_path: Optional[str]`, `include_labels: Optional[bool]`, `connection_string: Optional[str]`, `table_name: Optional[str]`
- `PipelineExportEntry` — all pipeline + query + server fields flattened; `range_id: Optional[str]`, `range: Optional[RangeBlock]`, `outputs: list[OutputExportEntry]`
- `PromqlQueryExportSample` — `pipelines: list[PipelineExportEntry]`
