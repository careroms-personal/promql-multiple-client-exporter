import json

from pathlib import Path
from models.executors.query_runner_executor import QueryResult, OutputExportEntry

def to_json(query_result: QueryResult, output: OutputExportEntry, pipeline_file_path: str):
  if not query_result.rows:
    return
  
  output_dir = Path(pipeline_file_path) / output.file_path
  output_dir.mkdir(parents=True, exist_ok=True)

  file_path = output_dir / f"{query_result.pipeline_config_id}.json"

  data = []
  for row in query_result.rows:
    for timestamp, value in row.values:
      entry = {
        "timestamp": timestamp,
        "value": value,
      }

      if output.include_labels:
        entry = {**row.labels, **entry}

      data.append(entry)

  with open(file_path, "w") as f:
    json.dump(data, f, indent=2)

  print(f"✅ JSON written: {file_path}")