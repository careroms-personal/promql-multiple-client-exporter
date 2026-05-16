import sys
import requests

from typing import Generator

from models.config_templates.promql_query_export_sample import PromqlQueryExportSample, OutputExportEntry, PipelineExportEntry
from models.executors.query_runner_executor import QueryResult, QueryResultRow

class QueryRunnerExecutor:
    def __init__(self, pipeline_export_entries: PromqlQueryExportSample):
      self.pipeline_export_entries = pipeline_export_entries
      self.client = requests.Session()

    def _executor_query(self, pipeline_entry: PipelineExportEntry) -> Generator[QueryResult, None, None]:
      match pipeline_entry.type:
        case "instant":
          response = self.client.get(
            url=f"{pipeline_entry.url}/{pipeline_entry.api}",
            params={
              "query": pipeline_entry.expr,
            },
            timeout=pipeline_entry.timeout,
          )

        case "range":
          response = self.client.get(
            url=f"{pipeline_entry.url}/{pipeline_entry.api}",
            params={
              "query": pipeline_entry.expr,
              "start": pipeline_entry.range.start,
              "end": pipeline_entry.range.end,
              "step": pipeline_entry.range.step,
            },
            timeout=pipeline_entry.timeout,
          )
        case _:
          raise ValueError(f"Unsupported query type: {pipeline_entry.type}")
        
      response.raise_for_status()
      res_result = response.json()

      if res_result["status"] != "success":
        print(f"❌ Prometheus error: {res_result.get('error', 'unknown')}")
        sys.exit(1)

      rows = []
      for result in res_result["data"]["result"]:
        rows.append(QueryResultRow(
          labels=self._filter_labels(
            metric=result["metric"],
            export_labels=pipeline_entry.export_labels
          ),
          values=result["values"] if pipeline_entry.type == "range" 
            else [result["value"]]
        ))

      yield QueryResult(
        pipeline_config_id=pipeline_entry.id,
        rows=rows,
        outputs=pipeline_entry.outputs,
      )

    def _filter_labels(self, metric: dict, export_labels: list[str]) -> dict:
      return {
        k: v for k, v in metric.items() if k in export_labels
      }

    def execute(self) -> list[QueryResult]:
      results = []

      for pipeline_entry in self.pipeline_export_entries.pipelines:
        results.extend(self._executor_query(pipeline_entry))
      return results
