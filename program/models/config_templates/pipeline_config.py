from pydantic import BaseModel
from typing import Optional, List

class YamlExportConfig(BaseModel):
  output_file_name: str
  export_version: str

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
  yaml_export_config: Optional[YamlExportConfig] = None
  config_files: ConfigFiles
  pipelines: List[PipelineEntry]
