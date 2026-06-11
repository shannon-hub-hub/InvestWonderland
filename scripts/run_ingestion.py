#!/usr/bin/env python3
"""CLI entrypoint for manual ingestion."""

import argparse
import logging
import sys

from app.etl.pipeline import SOURCES, run_pipeline

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)
logger = logging.getLogger("run_ingestion")


def main() -> int:
    parser = argparse.ArgumentParser(description="Run ETL ingestion into PostgreSQL")
    parser.add_argument(
        "--source",
        choices=SOURCES,
        default="investors",
        help="Data source to ingest (default: investors)",
    )
    args = parser.parse_args()

    try:
        run_ids = run_pipeline(args.source)
    except Exception:
        logger.exception("Ingestion failed")
        return 1

    logger.info("Ingestion complete. run_ids=%s", run_ids)
    return 0


if __name__ == "__main__":
    sys.exit(main())
