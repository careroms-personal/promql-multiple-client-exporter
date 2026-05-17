from pydantic import BaseModel
from typing import List, Optional
from models.config_templates.promql_config import QueryEntry
from models.config_templates.server_config import ServerEntry

class PromqlRangeEntry(BaseModel):
  id: str
  start: int
  end: int
  step: str

class PromqlRanges(BaseModel):
  ranges: List[PromqlRangeEntry]

class PromqlCombineQuery(BaseModel):
  pipeline_id: str
  pipeline_description: str
  server_entry: ServerEntry
  query_entry: QueryEntry
  range_entry: Optional[PromqlRangeEntry] = None