from pydantic import BaseModel
from typing import Literal, List

class QueryEntry(BaseModel):
  id: str
  query: str
  type: Literal["instant", "range"]
  export_labels: List[str]

class PromqlConfig(BaseModel):
  queries: List[QueryEntry]
