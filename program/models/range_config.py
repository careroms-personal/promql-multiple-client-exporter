from pydantic import BaseModel
from typing import Literal, Union

class RangeEntry(BaseModel):
  id: str
  type: Literal["datetime", "timestamp", "relative"]
  step: str
  start: Union[str, int]
  end: Union[str, int]

class RangeConfig(BaseModel):
  ranges: list[RangeEntry]
