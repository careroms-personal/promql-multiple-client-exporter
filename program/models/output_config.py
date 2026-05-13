from pydantic import BaseModel
from typing import Literal, Optional

class OutputEntry(BaseModel):
  id: str
  type: Literal["csv", "json", "postgresql"]
  file_path: Optional[str] = None
  include_labels: Optional[bool] = None
  connection_string: Optional[str] = None
  table_name: Optional[str] = None

class OutputConfig(BaseModel):
  outputs: list[OutputEntry]
