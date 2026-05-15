# promql-multiple-client-exporter — Program Guide
<!-- last human review: -->
<!-- last ai update: 2026 May 15 (ConfigExporterExecutor complete, PromqlCombineQuery updated) -->

Architecture, executor chain, and data flow.
See `AI-PYTHON-GUIDE.md` for conventions. See `AI-CONFIG-GUIDE.md` for config structure.

---

## Project Structure

```
promql-multiple-client-exporter/
├── vibe-code-rule.yaml
├── pyproject.toml
├── .ai/
│   ├── AI-PRINCIPLE-GUIDE.md
│   ├── AI-PYTHON-GUIDE.md
│   ├── AI-CONFIG-GUIDE.md
│   └── AI-PROGRAM-GUIDE.md
└── program/
    ├── app/
    │   └── main.py
    ├── models/
    │   ├── config_templates/
    │   │   ├── pipeline_config.py          # PipelineConfig, PipelineEntry, ConfigFiles, YamlExportConfig
    │   │   ├── server_config.py            # ServerConfig, ServerEntry, AuthConfig
    │   │   ├── promql_config.py            # PromqlConfig, QueryEntry
    │   │   ├── range_config.py             # RangeConfig, RangeEntry
    │   │   ├── output_config.py            # OutputConfig, OutputEntry
    │   │   └── promql_query_export_sample.py  # PromqlQueryExportSample, PipelineEntry, OutputEntry, RangeBlock
    │   └── executors/
    │       ├── config_loader_models.py     # ConfigLoaderResult
    │       └── config_parser_models.py     # PromqlCombineQuery, PromqlRanges, PromqlRangeEntry
    ├── processor/
    │   ├── processor.py
    │   └── executors/
    │       ├── config_loader_executor.py
    │       ├── config_parser_executor.py
    │       └── config_exporter_executor.py
    ├── global_config.py                    # reserved — do not add models here
    ├── config_templates/
    │   ├── pipeline_config.yaml
    │   ├── server_config.yaml
    │   ├── promql_config.yaml
    │   ├── range_config.yaml
    │   ├── output_config.yaml
    │   └── promql_query_export_sample.yaml
    └── test_suits/
        ├── global_test_config.py
        └── test_configs/
            ├── test_pipeline.yaml
            ├── test_server.yaml
            ├── test_promql.yaml
            ├── test_range.yaml
            └── test_output.yaml
```

---

## Executor Chain

```
pipeline_config.yaml
        ↓
    Processor.__init__
    ├── _load_and_validate_config()   →  PipelineConfig
    └── _set_pipeline_file_path()     →  injects resolved dir into PipelineConfig.pipeline_file_path
        ↓
    Processor.execute()
    ├── ConfigLoaderExecutor(pipeline_config)
    │       → loads server / promql / range / output YAMLs from config_files paths
    │       → returns ConfigLoaderResult
    │
    ├── ConfigParserExecutor(loader_result, pipeline_config)
    │       → parses ranges to Unix timestamps
    │       → cross-joins servers × queries × ranges × outputs per pipeline entry
    │       → returns list[PromqlCombineQuery]
    │
    └── ConfigExporterExecutor(combine_queries, loader_result, pipeline_config)
            → groups combine queries by pipeline_id
            → embeds selected outputs per pipeline entry
            → returns PromqlQueryExportSample
```

---

## Executor Reference

### ConfigLoaderExecutor
**File:** `program/processor/executors/config_loader_executor.py`
**Input:** `PipelineConfig`
**Output:** `ConfigLoaderResult`
**Duty:** Reads `config_files` paths from `PipelineConfig`, loads and validates each YAML sub-config (server, promql, range, output).

```
ConfigLoaderResult
  ├── promql_config: PromqlConfig
  ├── output_config: OutputConfig
  ├── server_config: ServerConfig
  └── range_config: Optional[RangeConfig]
```

---

### ConfigParserExecutor
**File:** `program/processor/executors/config_parser_executor.py`
**Input:** `ConfigLoaderResult`, `PipelineConfig`
**Output:** `list[PromqlCombineQuery]`
**Duty:**
- Parses range entries to Unix timestamps:
  - `datetime` → `.timestamp()`
  - `relative` → `int(time()) - offset` (supports `s/m/h/d/w/M`)
  - `timestamp` → passthrough
- Per `PipelineEntry`: selects matching queries / servers / ranges by ID reference
- Cross-joins servers × queries via `itertools.product`
- `instant` queries: `range_entry = None`
- `range` queries: expands one `PromqlCombineQuery` per range entry; exits with `❌` if no ranges defined

```
PromqlCombineQuery
  ├── pipeline_id: str
  ├── pipeline_description: str
  ├── server_entry: ServerEntry
  ├── query_entry: QueryEntry
  └── range_entry: Optional[PromqlRangeEntry]
```

---

### ConfigExporterExecutor
**File:** `program/processor/executors/config_exporter_executor.py`
**Input:** `list[PromqlCombineQuery]`, `ConfigLoaderResult`, `PipelineConfig`
**Output:** `PromqlQueryExportSample`
**Duty:**
- Groups combine queries by `pipeline_id`
- Per pipeline: filters selected outputs by ID from `config_loader_result.output_config`
- Builds one `PipelineExportEntry` per combine query with all selected outputs embedded as `list[OutputExportEntry]`
- One query → multiple outputs simultaneously (no duplicate query execution per output)

---

## How to Look Things Up

| What you need | Where to look |
|---|---|
| CLI entry point | `program/app/main.py` |
| Executor chain | `program/processor/processor.py` |
| Config loader executor | `program/processor/executors/config_loader_executor.py` |
| Config parser executor | `program/processor/executors/config_parser_executor.py` |
| Config exporter executor | `program/processor/executors/config_exporter_executor.py` |
| Pipeline config model | `program/models/config_templates/pipeline_config.py` |
| Server config model | `program/models/config_templates/server_config.py` |
| PromQL config model | `program/models/config_templates/promql_config.py` |
| Range config model | `program/models/config_templates/range_config.py` |
| Output config model | `program/models/config_templates/output_config.py` |
| Export output model | `program/models/config_templates/promql_query_export_sample.py` |
| Loader result model | `program/models/executors/config_loader_models.py` |
| Parser result models | `program/models/executors/config_parser_models.py` |
| YAML config templates | `program/config_templates/` |
| Test YAML configs | `program/test_suits/test_configs/` |
| Dependencies | `pyproject.toml` |
