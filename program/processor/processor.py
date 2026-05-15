import yaml, sys

from pathlib import Path
from pydantic import ValidationError

from models.config_templates.pipeline_config import PipelineConfig
from models.config_templates.promql_query_export_sample import PromqlQueryExportSample

from .executors.config_loader_executor import ConfigLoaderExecutor
from .executors.config_parser_executor import ConfigParserExecutor
from .executors.config_exporter_executor import ConfigExporterExecutor


class Processor:
  def __init__(self, config_path: str):
    self.config = self._load_and_validate_config(config_path=config_path)
    self._set_pipeline_file_path(config_path=config_path)

  def _load_and_validate_config(self, config_path: str):
    if not Path(config_path).exists():
      print(f"❌ Config file not found: {config_path}")
      sys.exit(1)

    try:
      with open(config_path, 'r') as f:
        yaml_data = yaml.safe_load(f)

      return PipelineConfig(**yaml_data)

    except ValidationError as e:
      print(f"❌ Invalid config file:")

      for error in e.errors():
        print(f"   - {error['loc']}: {error['msg']}")

      sys.exit(1)

  def _set_pipeline_file_path(self, config_path: str):
    resolved = str(Path(config_path).resolve().parent)
    self.config.pipeline_file_path = resolved

  def _write_yaml(self, export_data: PromqlQueryExportSample):
    output_path = Path(self.config.pipeline_file_path) / self.config.yaml_export_config.output_file_name

    with open(output_path, 'w') as f:
      yaml.dump(
        export_data.model_dump(exclude_none=True),
        f,
        default_flow_style=False,
        allow_unicode=True,
        sort_keys=False,
      )

  def execute(self):
    config_loader = ConfigLoaderExecutor(self.config)
    config_loader_result = config_loader.execute()
    
    config_parser = ConfigParserExecutor(config_loader_result, self.config)
    config_parser_result = config_parser.execute()

    config_exporter = ConfigExporterExecutor(config_parser_result, config_loader_result, self.config)
    config_exporter_result = config_exporter.execute()

    self._write_yaml(config_exporter_result)