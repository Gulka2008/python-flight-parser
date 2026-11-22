
"""Running queries against the flight database."""

from datetime import datetime
import math
import re


RECORD_KEYS = {
    "flight_id",
    "origin",
    "destination",
    "departure_datetime",
    "arrival_datetime",
    "price"
}

ALLOWED_KEYS = RECORD_KEYS | {
    "min_price",
    "sort_by",
    "order",
    "limit"
}


def valid_datetime(value):
    """Check exact date and time format."""
    if not isinstance(value, str):
        return False

    if not re.fullmatch(
        r"[0-9]{4}-[0-9]{2}-[0-9]{2} [0-9]{2}:[0-9]{2}",
        value
    ):
        return False

    try:
        datetime.strptime(value, "%Y-%m-%d %H:%M")
        return True
    except ValueError:
        return False


def valid_number(value):
    """Check that a value is a finite number, not a boolean."""
    return (
        type(value) in (int, float)
        and math.isfinite(value)
    )


def run_query(db: list[dict], query: dict) -> dict:
    """Return matching flights or an INVALID_QUERY response."""

    invalid = {
        "query": query,
        "error": "INVALID_QUERY",
        "matches": []
    }

    if not isinstance(query, dict):
        return invalid

    if any(key not in ALLOWED_KEYS for key in query):
        return invalid

    for key, value in query.items():

        if key in ("flight_id", "origin", "destination"):
            if not isinstance(value, str):
                return invalid

        elif key in ("departure_datetime", "arrival_datetime"):
            if not valid_datetime(value):
                return invalid

        elif key in ("price", "min_price"):
            if not valid_number(value):
                return invalid

        elif key == "sort_by":
            if not isinstance(value, str) or value not in RECORD_KEYS:
                return invalid

        elif key == "order":
            if value not in ("asc", "desc"):
                return invalid

        elif key == "limit":
            if type(value) is not int or value < 0:
                return invalid

    if "order" in query and "sort_by" not in query:
        return invalid

    matches = []

    for flight in db:

        if "flight_id" in query:
            if flight["flight_id"] != query["flight_id"]:
                continue

        if "origin" in query:
            if flight["origin"] != query["origin"]:
                continue

        if "destination" in query:
            if flight["destination"] != query["destination"]:
                continue

        if "departure_datetime" in query:
            if flight["departure_datetime"] < query["departure_datetime"]:
                continue

        if "arrival_datetime" in query:
            if flight["arrival_datetime"] > query["arrival_datetime"]:
                continue

        if "price" in query:
            if flight["price"] > query["price"]:
                continue

        if "min_price" in query:
            if flight["price"] < query["min_price"]:
                continue

        matches.append(flight)

    if "sort_by" in query:
        sort_key = query["sort_by"]
        descending = query.get("order", "asc") == "desc"

        matches = sorted(
            matches,
            key=lambda flight: flight[sort_key],
            reverse=descending
        )

    if "limit" in query:
        matches = matches[:query["limit"]]

    return {
        "query": query,
        "matches": matches
    }


def run_queries(db: list[dict], queries: dict | list) -> list[dict]:
    """Run one query or a list of queries."""

    if isinstance(queries, dict):
        queries = [queries]

    return [run_query(db, query) for query in queries]
