import sys
import yaml

from pathlib import Path
from typing import List, Generator

from models.executors.config_loader_models import ConfigLoaderResult
from models.executors.config_parser_models import PromqlCombineQuery
from models.config_templates.output_config import OutputEntry
from models.config_templates.pipeline_config import PipelineConfig
from models.config_templates.promql_query_export_sample import (
  PromqlQueryExportSample,
  PipelineExportEntry,
  OutputExportEntry,
  RangeBlock
)

class ConfigExporterExecutor:
  def __init__(self, promql_combine_queries: List[PromqlCombineQuery], config_loader_result: ConfigLoaderResult, pipeline_config: PipelineConfig):
    self.promql_combine_queries = promql_combine_queries
    self.config_loader_result = config_loader_result
    self.pipeline_config = pipeline_config

  def _build_pipeline_query_export(self, pipeline_queries: List[PromqlCombineQuery], selected_outputs: List[OutputEntry]) -> Generator[PipelineExportEntry, None, None]:
    output_entries = [
      OutputExportEntry(
        id=o.id,
        type=o.type,
        file_path=o.file_path,
        include_labels=o.include_labels,
        connection_string=o.connection_string,
        table_name=o.table_name
      )
      for o in selected_outputs
    ]

    for combine_query in pipeline_queries:
      if combine_query.range_entry:
        entry_id = f"{combine_query.pipeline_id}_{combine_query.query_entry.id}_{combine_query.range_entry.id}_{combine_query.server_entry.id}"
      else:
        entry_id = f"{combine_query.pipeline_id}_{combine_query.query_entry.id}_{combine_query.server_entry.id}"

      api = f"{combine_query.server_entry.api}/{'query_range' if combine_query.query_entry.type == 'range' else 'query'}"

      range_block = RangeBlock(
        start=combine_query.range_entry.start,
        end=combine_query.range_entry.end,
        step=combine_query.range_entry.step
      ) if combine_query.range_entry else None

      yield PipelineExportEntry(
        id=entry_id,
        pipeline_id=combine_query.pipeline_id,
        pipeline_description=combine_query.pipeline_description,
        query_id=combine_query.query_entry.id,
        server_id=combine_query.server_entry.id,
        range_id=combine_query.range_entry.id if combine_query.range_entry else None,
        type=combine_query.query_entry.type,
        url=combine_query.server_entry.url,
        api=api,
        auth=combine_query.server_entry.auth.model_dump() if combine_query.server_entry.auth else {},
        timeout=combine_query.server_entry.timeout,
        expr=combine_query.query_entry.query,
        export_labels=combine_query.query_entry.export_labels,
        range=range_block,
        outputs=output_entries
      )

  def _write_yaml(self, export_data: PromqlQueryExportSample):
    if not self.pipeline_config.yaml_export_config:
      print(f"❌ yaml_export_config is not defined in pipeline config")
      sys.exit(1)

    output_path = Path(self.pipeline_config.pipeline_file_path) / self.pipeline_config.yaml_export_config.output_file_name

    with open(output_path, 'w') as f:
      yaml.dump(
        export_data.model_dump(exclude_none=True),
        f,
        default_flow_style=False,
        allow_unicode=True,
        sort_keys=False,
      )

  def execute(self) -> PromqlQueryExportSample:
    all_outputs = self.config_loader_result.output_config.outputs
    all_entries = []

    for pipeline_entry in self.pipeline_config.pipelines:
      pipeline_queries = [q for q in self.promql_combine_queries if q.pipeline_id == pipeline_entry.id]
      selected_outputs = [o for o in all_outputs if o.id in pipeline_entry.outputs]
      all_entries.extend(self._build_pipeline_query_export(pipeline_queries, selected_outputs))

    export_data = PromqlQueryExportSample(pipelines=all_entries)
    self._write_yaml(export_data)
    
    return export_data
