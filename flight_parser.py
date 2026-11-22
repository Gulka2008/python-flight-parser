
"""Flight Schedule Parser and Query Tool."""

import argparse
import json
import logging
import os
import sys
from datetime import datetime

from validator import load_airports
from csv_loader import parse_files
from query import run_queries


STUDENT_ID = "251ADB250"
FIRST_NAME = "Gulnara"
LAST_NAME = "Akbarli"


def main(argv: list[str] | None = None) -> int:
    """Run the program and return exit code 0, 1, or 2."""

    parser = argparse.ArgumentParser(
        description="Flight Schedule Parser and Query Tool"
    )

    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("-i", metavar="FILE")
    source.add_argument("-d", metavar="FOLDER")
    source.add_argument("-j", metavar="FILE")

    parser.add_argument("-a", metavar="FILE")
    parser.add_argument("-o", metavar="FILE")
    parser.add_argument("-q", metavar="FILE")
    parser.add_argument("-r", metavar="FOLDER", default=".")

    args = parser.parse_args(argv)

    if (args.i or args.d) and not args.a:
        parser.error("-a is required with -i or -d")

    if args.j and args.o is not None:
        parser.error("-o cannot be used with -j")

    logger = logging.getLogger("flight_parser")
    logger.setLevel(logging.INFO)
    handler = None

    try:
        if args.j:
            with open(args.j, "r", encoding="utf-8") as file:
                records = json.load(file)

            if not isinstance(records, list):
                raise ValueError("Database must be a JSON array")

            if not all(isinstance(item, dict) for item in records):
                raise ValueError("Database must contain objects")

        else:
            airports = load_airports(args.a)

            if args.i:
                paths = [args.i]
            else:
                paths = sorted(
                    os.path.join(args.d, name)
                    for name in os.listdir(args.d)
                    if name.endswith(".csv")
                    and os.path.isfile(os.path.join(args.d, name))
                )

                if not paths:
                    raise ValueError("No CSV files found")

            output_path = args.o or "db.json"
            log_path = os.path.join(
                os.path.dirname(output_path) or ".",
                "errors.log"
            )

            handler = logging.FileHandler(
                log_path,
                mode="w",
                encoding="utf-8"
            )
            handler.setFormatter(
                logging.Formatter(
                    "%(asctime)s %(levelname)s %(message)s",
                    datefmt="%Y-%m-%d %H:%M:%S"
                )
            )
            logger.addHandler(handler)

            records, errors = parse_files(paths, airports)

            with open(output_path, "w", encoding="utf-8") as file:
                json.dump(records, file, indent=4)

            for error in errors:
                logger.warning(error)

        if args.q:
            with open(args.q, "r", encoding="utf-8") as file:
                queries = json.load(file)

            if isinstance(queries, dict):
                pass
            elif isinstance(queries, list):
                if not all(isinstance(q, dict) for q in queries):
                    raise ValueError("Queries must be JSON objects")
            else:
                raise ValueError("Invalid query file format")

            results = run_queries(records, queries)

            timestamp = datetime.now().strftime("%Y%m%d_%H%M")

            response_name = (
                f"response_{STUDENT_ID}_"
                f"{FIRST_NAME}_{LAST_NAME}_"
                f"{timestamp}.json"
            )

            response_path = os.path.join(args.r, response_name)

            with open(response_path, "w", encoding="utf-8") as file:
                json.dump(results, file, indent=4)

        return 0

    except (OSError, ValueError, json.JSONDecodeError) as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1

    finally:
        if handler is not None:
            logger.removeHandler(handler)
            handler.close()


if __name__ == "__main__":
    sys.exit(main())
