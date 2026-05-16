from models.executors.query_runner_executor import QueryResult
from .exporter_functions.to_csv import to_csv

class QueryOutputExporterExecutor:
    def __init__(self, query_results: list[QueryResult], pipeline_file_path: str):
      self.query_results = query_results
      self.pipeline_file_path = pipeline_file_path
    def _export_results(self):
      output_functions  = {
        "csv": to_csv
      }

      for query_result in self.query_results:
        if not query_result.rows:
          print(f"⚠️ No data for {query_result.pipeline_config_id}, skipping")
          continue

        for output in query_result.outputs:
          fn = output_functions.get(output.type)

          if fn:
            fn(query_results=query_result, output=output, pipeline_file_path=self.pipeline_file_path)

    def execute(self):
      self._export_results()