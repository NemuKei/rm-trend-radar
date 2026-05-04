from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

from .db import init_db
from .fetch import (
    exit_code_for_results,
    fetch_sources,
    has_failures,
    unknown_source_names,
)
from .snapshot import build_snapshot, snapshot_has_failures, write_snapshot


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="python -m rm_trend_radar")
    subparsers = parser.add_subparsers(dest="command")

    subparsers.add_parser("init", help="Initialize the local SQLite database.")

    fetch_parser = subparsers.add_parser("fetch", help="Fetch RSS items manually.")
    fetch_parser.add_argument(
        "--source",
        action="append",
        default=[],
        help="Fetch only the named source. Can be specified multiple times.",
    )
    fetch_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Parse feeds without writing articles to SQLite.",
    )
    fetch_parser.add_argument(
        "--json",
        action="store_true",
        help="Print machine-readable JSON to stdout.",
    )
    fetch_parser.add_argument(
        "--timeout",
        type=float,
        default=20,
        help="HTTP timeout in seconds for each source.",
    )

    snapshot_parser = subparsers.add_parser(
        "fetch-snapshot",
        help="Fetch RSS metadata and write a JSON artifact without updating SQLite.",
    )
    snapshot_parser.add_argument(
        "--source",
        action="append",
        default=[],
        help="Fetch only the named source. Can be specified multiple times.",
    )
    snapshot_parser.add_argument(
        "--output",
        default="artifacts/rss_snapshot.json",
        help="Path to the JSON snapshot artifact.",
    )
    snapshot_parser.add_argument(
        "--timeout",
        type=float,
        default=20,
        help="HTTP timeout in seconds for each source.",
    )

    args = parser.parse_args(argv)

    if args.command in (None, "init"):
        init_db(seed=True)
        print("Initialized rm_trend_radar.db")
        return 0

    if args.command == "fetch":
        unknown_sources = unknown_source_names(args.source)
        if unknown_sources:
            print("Unknown source: " + ", ".join(unknown_sources), file=sys.stderr)
            return 1

        results = fetch_sources(
            source_names=args.source,
            dry_run=args.dry_run,
            timeout_seconds=args.timeout,
        )
        if args.json:
            print(json.dumps([result.to_dict() for result in results], ensure_ascii=False))
        else:
            for result in results:
                print(
                    "source={source} fetched={fetched} added={added} "
                    "updated={updated} unchanged={unchanged} failed={failed}".format(
                        **result.to_dict()
                    )
                )
        if has_failures(results):
            for result in results:
                if result.error:
                    print(f"{result.source}: {result.error}", file=sys.stderr)
        return exit_code_for_results(results)

    if args.command == "fetch-snapshot":
        unknown_sources = unknown_source_names(args.source)
        if unknown_sources:
            print("Unknown source: " + ", ".join(unknown_sources), file=sys.stderr)
            return 1

        snapshot = build_snapshot(
            source_names=args.source,
            timeout_seconds=args.timeout,
        )
        write_snapshot(snapshot, Path(args.output))
        for source in snapshot["sources"]:
            print(
                "source={source} fetched={fetched} failed={failed}".format(
                    **source
                )
            )
        print(f"output={args.output}")
        if snapshot_has_failures(snapshot):
            return 3
        return 0

    parser.error(f"Unknown command: {args.command}")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
