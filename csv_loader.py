
"""Reading CSV files into flight records and error messages."""

import csv
import os

from validator import validate_row, to_record


def parse_files(paths: list[str], airports: set[str]) -> tuple[list[dict], list[str]]:
    """Process CSV files and return valid records and errors."""

    records = []
    errors = []
    seen_flights = set()

    for path in paths:
        filename = os.path.basename(path)

        with open(path, "r", encoding="utf-8", newline="") as file:
            # Skip the header
            next(file, None)

            for line_number, line in enumerate(file, start=2):
                # Ignore blank lines and comments
                if not line.strip() or line.lstrip().startswith("#"):
                    continue

                # Read CSV fields
                fields = next(csv.reader([line]))
                fields = [field.strip() for field in fields]

                # Validate the row
                error_code = validate_row(fields, airports)

                if error_code is not None:
                    errors.append(
                        f"{filename}:{line_number}: {error_code} | {line.strip()}"
                    )
                    continue

                # Check for duplicate flights
                flight_key = (fields[0], fields[3])

                if flight_key in seen_flights:
                    errors.append(
                        f"{filename}:{line_number}: DUPLICATE_FLIGHT | {line.strip()}"
                    )
                    continue

                seen_flights.add(flight_key)

                # Convert valid row into a record
                record = to_record(fields)
                records.append(record)

    return records, errors