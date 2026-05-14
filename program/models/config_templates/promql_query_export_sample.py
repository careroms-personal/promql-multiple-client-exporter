from pydantic import BaseModel
from typing import Optional, Union

class RangeBlock(BaseModel):
  start: int
  end: int
  step: str

class PipelineEntry(BaseModel):
  id: str
  query_id: str
  server_id: str
  range_id: Optional[str] = None
  description: str
  type: str
  url: str
  api: str
  auth: dict
  timeout: int
  expr: str
  export_labels: list[str]
  range: Optional[RangeBlock] = None

class OutputEntry(BaseModel):
  id: str
  type: str
  file_path: Optional[str] = None
  include_labels: Optional[bool] = None
  connection_string: Optional[str] = None
  table_name: Optional[str] = None

class PromqlQueryExportSample(BaseModel):
  pipelines: list[PipelineEntry]
  outputs: list[OutputEntry]
