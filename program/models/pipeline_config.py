from pydantic import BaseModel
from typing import Optional

class ConfigFiles(BaseModel):
  promql: str
  range: Optional[str] = None
  server: str
  output: str

class PipelineEntry(BaseModel):
  id: str
  name: str
  description: str
  promqls: list[str]
  ranges: Optional[list[str]] = None
  servers: list[str]
  outputs: list[str]

class PipelineConfig(BaseModel):
  config_files: ConfigFiles
  pipelines: list[PipelineEntry]
