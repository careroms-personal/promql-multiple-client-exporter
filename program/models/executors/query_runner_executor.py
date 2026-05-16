from pydantic import BaseModel
from models.config_templates.promql_query_export_sample import PipelineExportEntry

class QueryResultRow(BaseModel):
  labels: dict
  values: list[tuple[float, str]]

class QueryResult(BaseModel):
  pipeline_entry: PipelineExportEntry
  rows: list[QueryResultRow]