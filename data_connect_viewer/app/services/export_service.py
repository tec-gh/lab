import csv
import io
import json

from app.models.record import Record


EXPORT_FIELDS = [
    "id",
    "hostname",
    "ipaddress",
    "area",
    "building",
    "category",
    "model",
    "ping_test_result",
    "exec_result",
    "received_at",
    "mapping_version",
    "payload_json",
]


def render_csv(records: list[Record]) -> str:
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=EXPORT_FIELDS)
    writer.writeheader()
    for record in records:
        writer.writerow({field: getattr(record, field) for field in EXPORT_FIELDS})
    return output.getvalue()


def render_json(records: list[Record]) -> str:
    payload = [{field: getattr(record, field) for field in EXPORT_FIELDS} for record in records]
    return json.dumps(payload, ensure_ascii=False, indent=2, default=str)
