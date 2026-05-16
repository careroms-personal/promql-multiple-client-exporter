import csv

from pathlib import Path
from models.executors.query_runner_executor import QueryResult, OutputExportEntry

def to_csv(query_result: QueryResult, output: OutputExportEntry, pipeline_file_path: str):
  if not query_result.rows:
    return
  
  output_dir = Path(pipeline_file_path) / output.file_path
  output_dir.mkdir(parents=True, exist_ok=True)

  file_path = output_dir / f"{query_result.pipeline_config_id}.csv"

  first_row = query_result.rows[0]
  label_keys = list(first_row.labels.keys()) if output.include_labels else []
  headers = label_keys + ["timestamp", "value"]

  with open(file_path, "w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=headers)
    writer.writeheader()

    for row in query_result.rows:
      for timestamp, value in row.values:
        line = {"timestamp": timestamp, "value": value}

        if output.include_labels:
          line = {**row.labels, **line}

        writer.writerow(line)
  
  print(f"✅ CSV written: {file_path}")
