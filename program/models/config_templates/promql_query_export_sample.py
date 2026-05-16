from pydantic import BaseModel
from typing import Optional

class RangeBlock(BaseModel):
  start: int
  end: int
  step: str

class OutputExportEntry(BaseModel):
  id: str
  type: str
  file_path: Optional[str] = None
  include_labels: Optional[bool] = None
  connection_string: Optional[str] = None
  table_name: Optional[str] = None

class PipelineExportEntry(BaseModel):
  id: str
  pipeline_id: str
  pipeline_description: str
  query_id: str
  server_id: str
  range_id: Optional[str] = None
  type: str
  url: str
  api: str
  auth: dict
  headers: dict
  timeout: int
  expr: str
  export_labels: list[str]
  range: Optional[RangeBlock] = None
  outputs: list[OutputExportEntry]

class PromqlQueryExportSample(BaseModel):
  pipelines: list[PipelineExportEntry]
