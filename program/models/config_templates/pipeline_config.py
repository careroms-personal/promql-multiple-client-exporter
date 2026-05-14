from pydantic import BaseModel
from typing import Optional, List

class ConfigFiles(BaseModel):
  promql: str
  range: Optional[str] = None
  server: str
  output: str

class PipelineEntry(BaseModel):
  id: str
  name: str
  description: str
  promqls: List[str]
  ranges: Optional[List[str]] = None
  servers: List[str]
  outputs: List[str]

class PipelineConfig(BaseModel):
  pipeline_file_path: Optional[str] = None
  config_files: ConfigFiles
  pipelines: List[PipelineEntry]
