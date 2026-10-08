#!/usr/bin/env python3
"""Pre-compute monthly average 311 response times (in hours) per zipcode.

Reads the big 311 CSV once and writes a small summary file that the
dashboard can load instantly.
"""

import argparse
import csv
from collections import defaultdict
from datetime import datetime


def parse_timestamp(text):
    """Parse 'MM/DD/YYYY HH:MM:SS AM' quickly; return None if blank/invalid."""
    try:
        hour = int(text[11:13]) % 12
        if text[20:22] == "PM":
            hour += 12
        return datetime(int(text[6:10]), int(text[0:2]), int(text[3:5]),
                        hour, int(text[14:16]), int(text[17:19]))
    except (ValueError, IndexError):
        return None


def clean_zip(text):
    """Return a 5-digit zipcode, or None if the value isn't one."""
    z = (text or "").strip()[:5]
    return z if len(z) == 5 and z.isdigit() else None


def main():
    parser = argparse.ArgumentParser(
        description="Compute monthly average create-to-closed time (hours) "
                    "for each zipcode, plus an ALL row.")
    parser.add_argument("-i", "--input", required=True, help="311 CSV file")
    parser.add_argument("-o", "--output", default="monthly_response_times.csv",
                        help="summary CSV to write (default: %(default)s)")
    parser.add_argument("-y", "--year", type=int, default=2024,
                        help="year of incident creation to include (default: %(default)s)")
    args = parser.parse_args()

    total_hours = defaultdict(float)   # (zipcode, month) -> sum of hours
    n_incidents = defaultdict(int)     # (zipcode, month) -> number of incidents

    with open(args.input, newline="", encoding="utf-8", errors="replace") as f:
        for row in csv.DictReader(f):
            created = parse_timestamp(row["Created Date"])
            closed = parse_timestamp(row["Closed Date"])
            if created is None or closed is None:   # skip incidents not yet closed
                continue
            if created.year != args.year:
                continue
            hours = (closed - created).total_seconds() / 3600
            if hours < 0:                           # closed before created: bad data
                continue

            zipcode = clean_zip(row["Incident Zip"])
            keys = ["ALL"] if zipcode is None else ["ALL", zipcode]
            for key in keys:
                total_hours[(key, created.month)] += hours
                n_incidents[(key, created.month)] += 1

    with open(args.output, "w", newline="") as out:
        writer = csv.writer(out, lineterminator="\n")
        writer.writerow(["zipcode", "month", "avg_hours", "count"])
        for (zipcode, month) in sorted(total_hours):
            n = n_incidents[(zipcode, month)]
            writer.writerow([zipcode, month,
                             round(total_hours[(zipcode, month)] / n, 3), n])

    print(f"Wrote {len(total_hours)} rows to {args.output}")


if __name__ == "__main__":
    main()
