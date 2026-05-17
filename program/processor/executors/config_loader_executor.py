import sys
import yaml

from pathlib import Path
from pydantic import ValidationError
from typing import Union

from models.executors.config_loader_models import ConfigLoaderResult
from models.config_templates.pipeline_config import PipelineConfig
from models.config_templates.promql_config import PromqlConfig
from models.config_templates.output_config import OutputConfig
from models.config_templates.server_config import ServerConfig
from models.config_templates.range_config import RangeConfig

class ConfigLoaderExecutor:
  def __init__(self, pipeline_config: PipelineConfig):
    self.pipeline_config = pipeline_config

  def _load_configs_from_pipeline(self) -> ConfigLoaderResult:
    base = Path(self.pipeline_config.pipeline_file_path)
    cf = self.pipeline_config.config_files

    return ConfigLoaderResult(
      promql_config=self._load_and_validate_subconfig(base / cf.promql, "promql"),
      output_config=self._load_and_validate_subconfig(base / cf.output, "output"),
      server_config=self._load_and_validate_subconfig(base / cf.server, "server"),
      range_config=self._load_and_validate_subconfig(base / cf.range, "range") if cf.range else None
    )

  def _load_and_validate_subconfig(self, subconfig_path: Path, subconfig_type: str) -> Union[PromqlConfig, OutputConfig, ServerConfig, RangeConfig]:
    if not subconfig_path.exists():
      print(f"❌ Sub-config file not found: {subconfig_path}")
      sys.exit(1)

    try:
      with open(subconfig_path, 'r') as f:
        yaml_data = yaml.safe_load(f)

      match subconfig_type:
        case "promql":
          return PromqlConfig(**yaml_data)
        case "output":
          return OutputConfig(**yaml_data)
        case "server":
          return ServerConfig(**yaml_data)
        case "range":
          return RangeConfig(**yaml_data)
        case _:
          raise ValueError(f"Unknown subconfig type: {subconfig_type}")

    except ValidationError as e:
      print(f"❌ Invalid sub-config file ({subconfig_type}):")
      for error in e.errors():
        print(f"   - {error['loc']}: {error['msg']}")
      sys.exit(1)

  def execute(self) -> ConfigLoaderResult:
    return self._load_configs_from_pipeline()
