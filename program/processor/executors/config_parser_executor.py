import re
import sys
from time import time

from itertools import product
from typing import Generator, List

from models.config_templates.pipeline_config import PipelineConfig, PipelineEntry
from models.executors.config_loader_models import ConfigLoaderResult
from models.executors.config_parser_models import (
  PromqlRangeEntry,
  PromqlRanges,
  ServerEntry,
  QueryEntry,
  PromqlCombineQuery
)

class ConfigParserExecutor:
  def __init__(self, config_loader_result: ConfigLoaderResult, pipeline_config: PipelineConfig):
    self.config_loader_result = config_loader_result
    self.pipeline_config = pipeline_config

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
  
  def _combine_promql_query(self, pipeline_id: str, pipeline_description: str, server_entry: ServerEntry, query_entry: QueryEntry, range_entry: PromqlRangeEntry):

    return PromqlCombineQuery(
      pipeline_id=pipeline_id,
      pipeline_description=pipeline_description,
      server_entry=server_entry,
      query_entry=query_entry,
      range_entry=range_entry,
    )

  def _build_combine_queries(self, pipeline_entry: PipelineEntry, range_config: PromqlRanges | None) -> Generator[PromqlCombineQuery, None, None]:
    selected_queries = [
      q for q in self.config_loader_result.promql_config.queries
      if q.id in pipeline_entry.promqls
    ]

    selected_servers = [
      s for s in self.config_loader_result.server_config.servers
      if s.id in pipeline_entry.servers
    ]

    selected_ranges = [
      r for r in range_config.ranges
      if r.id in pipeline_entry.ranges
    ] if range_config and pipeline_entry.ranges else []

    for server, query in product(selected_servers, selected_queries):
      if query.type == "instant":
        yield self._combine_promql_query(pipeline_entry.id, pipeline_entry.description, server, query, None)
      elif query.type == "range":
        if not selected_ranges:
          print(f"❌ Query {query.id} is a range query but no ranges are defined in the pipeline")
          sys.exit(1)

        for range_entry in selected_ranges:
          yield self._combine_promql_query(pipeline_entry.id, pipeline_entry.description, server, query, range_entry)
      else:
        print(f"❌ Unknown query type: {query.type}")
        sys.exit(1)
    
  
  def execute(self):
    range_config = self._parse_range_config() if self.config_loader_result.range_config else None
    
    return [
      combine_query
      for pipeline in self.pipeline_config.pipelines
      for combine_query in self._build_combine_queries(pipeline, range_config)
    ]
