from pydantic import BaseModel
from typing import Literal

class QueryEntry(BaseModel):
  id: str
  query: str
  type: Literal["instant", "range"]
  export_labels: list[str]

class PromqlConfig(BaseModel):
  queries: list[QueryEntry]
