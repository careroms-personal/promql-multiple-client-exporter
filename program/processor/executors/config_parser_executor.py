import re
import sys
from time import time

from itertools import product

from models.executors.config_loader_models import ConfigLoaderResult
from models.executors.config_parser_models import (
  PromqlRangeEntry, 
  PromqlRanges, 
  ServerEntry, 
  QueryEntry, 
  OutputEntry, 
  PromqlCombineQuery
)

class ConfigParserExecutor:
  def __init__(self, config_loader_result: ConfigLoaderResult):
    self.config_loader_result = config_loader_result

  def _parse_relative(self, value: str) -> int:
    if value == "now":
      return int(time())
    
    match = re.match(r"^now-(\d+)([smhdwM])$", value)

    if not match:
      print(f"❌ Invalid relative time format: {value}")
      sys.exit(1)

    amount = int(match.group(1))
    unit = match.group(2)

    multiplier = {
      "s": 1,
      "m": 60,
      "h": 3600,
      "d": 86400,
      "w": 604800,
      "M": 2592000,
    }

    return int(time()) - (amount * multiplier[unit])

  def _parse_range_config(self):
    range_config = self.config_loader_result.range_config
    parsed_ranges = []

    for range_entry in range_config.ranges:
      # Pydantic auto-converts ISO datetime string to datetime object
      # via Union[str, int, datetime] in RangeEntry model
      # so .timestamp() is safe to call directly here
      match range_entry.type:
        case "datetime":
          start = int(range_entry.start.timestamp())
          end = int(range_entry.end.timestamp())
        case "relative":
          start = self._parse_relative(range_entry.start)
          end = self._parse_relative(range_entry.end)
        case "timestamp":
          start = int(range_entry.start)
          end = int(range_entry.end)
        case _:
          print(f"❌ Unknown range type: {range_entry.type}")
          sys.exit(1)

      parsed_ranges.append(PromqlRangeEntry(
        id=range_entry.id,
        start=start,
        end=end,
        step=range_entry.step
      ))

    return PromqlRanges(ranges=parsed_ranges)
  
  def _combine_promql_query(self, server_entry: ServerEntry, query_entry: QueryEntry, range_entry: PromqlRangeEntry, output_entry: OutputEntry):

    return PromqlCombineQuery(
      server_entry=server_entry,
      query_entry=query_entry,
      range_entry=range_entry,
      output_entry=output_entry
    )
  
  def _build_combine_queries(self, range_config: PromqlRanges | None) -> list[PromqlCombineQuery]:
    combine_queries = []
    
    for server, query, output in product(
      self.config_loader_result.server_config.servers, 
      self.config_loader_result.promql_config.queries,
      self.config_loader_result.output_config.outputs):
      if query.type == "instant":
        combine_queries.append(
          self._combine_promql_query(server, query, None, output)
        )
      elif query.type == "range":
        if range_config is None:
          print(f"❌ Query {query.id} is type range but no range config provided")
          sys.exit(1)

        for range_ in range_config.ranges:
          combine_queries.append(
            self._combine_promql_query(server, query, range_, output)
          )
      else:
        print(f"❌ Unknown query type: {query.type}")
        sys.exit(1)

    return combine_queries
  
  def execute(self):
    range_config = self._parse_range_config() if self.config_loader_result.range_config else None

    return self._build_combine_queries(range_config)
