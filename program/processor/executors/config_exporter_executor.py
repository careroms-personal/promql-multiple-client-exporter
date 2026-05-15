from typing import List

from models.executors.config_parser_models import PromqlCombineQuery
from models.config_templates.promql_query_export_sample import PromqlQueryExportSample, PipelineEntry, OutputEntry
from models.config_templates.pipeline_config import PipelineConfig

class ConfigExporterExecutor:
    def __init__(self, promql_combine_queries: List[PromqlCombineQuery], pipeline_config: PipelineConfig):
      self.promql_combine_queries = promql_combine_queries
      self.pipeline_config = pipeline_config

    # def _build_pipelines(self):
    #   for combine_query in self.promql_combine_queries:
    #     combine_query_dict = PipelineEntry(
          
    #     )

    def execute(self):
      pass