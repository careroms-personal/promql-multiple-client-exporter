from pydantic import BaseModel
from models.config_templates.promql_query_export_sample import OutputExportEntry

class QueryResultRow(BaseModel):
  labels: dict
  values: list[tuple[float, str]]

class QueryResult(BaseModel):
  pipeline_config_id: str
  rows: list[QueryResultRow]
  outputs: list[OutputExportEntry]