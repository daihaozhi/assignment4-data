import argparse
import gzip
import uuid
from datetime import datetime, timezone
from pathlib import Path

from fastwarc.warc import ArchiveIterator, WarcRecordType

from todo0 import foo


def _header_to_str(record, key: str, default: str = "") -> str:
    value = record.headers.get(key, default)
    if isinstance(value, bytes):
        return value.decode("utf-8", errors="replace")
    return str(value) if value is not None else default


def _build_wet_record(uri: str, date_str: str, text: str) -> str:
    payload = text.encode("utf-8")
    record_id = f"<urn:uuid:{uuid.uuid4()}>"
    lines = [
        "WARC/1.0",
        "WARC-Type: conversion",
        f"WARC-Target-URI: {uri}",
        f"WARC-Date: {date_str}",
        f"WARC-Record-ID: {record_id}",
        "Content-Type: text/plain; charset=utf-8",
        f"Content-Length: {len(payload)}",
        "",
        text,
        "",
    ]
    return "\n".join(lines)


def convert_warc_gz_to_wet(input_path: Path, output_path: Path) -> tuple[int, int]:
    total = 0
    written = 0
    output_path.parent.mkdir(parents=True, exist_ok=True)

    open_output = (
        (lambda p: gzip.open(p, "wt", encoding="utf-8", newline="\n"))
        if output_path.suffix == ".gz"
        else (lambda p: p.open("w", encoding="utf-8", newline="\n"))
    )

    with input_path.open("rb") as fin, open_output(output_path) as fout:
        for record in ArchiveIterator(fin, parse_http=True):
            if record.record_type != WarcRecordType.response:
                continue

            total += 1
            payload = record.reader.read()
            if not payload:
                continue

            text = foo(payload).strip()
            if not text:
                continue

            uri = _header_to_str(record, "WARC-Target-URI", "unknown://unknown")
            warc_date = _header_to_str(
                record,
                "WARC-Date",
                datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
            )
            fout.write(_build_wet_record(uri, warc_date, text))
            written += 1

    return total, written


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Read a .warc.gz file and write a .wet or .wet.gz file using todo0.foo()."
    )
    parser.add_argument("input_warc_gz", type=Path, help="Path to input .warc.gz")
    parser.add_argument("output_wet", type=Path, help="Path to output .wet or .wet.gz")
    args = parser.parse_args()

    total, written = convert_warc_gz_to_wet(args.input_warc_gz, args.output_wet)
    print(f"Done. response records seen: {total}, WET records written: {written}")


if __name__ == "__main__":
    main()
