from pydantic import BaseModel
from typing import Optional

from models.config_templates.output_config import OutputConfig
from models.config_templates.promql_config import PromqlConfig
from models.config_templates.range_config import RangeConfig
from models.config_templates.server_config import ServerConfig

class ConfigLoaderResult(BaseModel):
  promql_config: PromqlConfig
  output_config: OutputConfig
  server_config: ServerConfig
  range_config: Optional[RangeConfig] = None
