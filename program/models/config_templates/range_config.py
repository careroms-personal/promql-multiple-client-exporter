from pydantic import BaseModel
from typing import Literal, Union
from datetime import datetime

class RangeEntry(BaseModel):
  id: str
  type: Literal["datetime", "timestamp", "relative"]
  step: str
  start: Union[str, int, datetime]
  end: Union[str, int, datetime]

class RangeConfig(BaseModel):
  ranges: list[RangeEntry]
