#!/usr/bin/env python3

"""Count NYC 311 complaint types per borough within a creation-date range."""

import argparse
import csv
import sys
from collections import Counter
from datetime import date, datetime

def parse_cli_date(text):
    try:
        return datetime.strptime(text, "%Y-%m-%d").date()
    except ValueError:
        raise argparse.ArgumentTypeError(
            f"invalid date '{text}' (use YYYY-MM-DD)")

def build_parser():
    parser = argparse.ArgumentParser(
            prog="borough_complaints.py",
            description="Count the number of each complaint type per borough " 
            "for 311 requests created within a date range.",
    ) 
    parser.add_argument("-i", "--input", required=True, 
                        help="the 311 CSV file to read")
    parser.add_argument("-s", "--start", required=True, type=parse_cli_date,
                        help="first creation date to includ (YYYY-MM--DD)")
    parser.add_argument("-e", "--end", required=True, type=parse_cli_date,
                        help="last creation date to include (YYYY-MM-DD)")
    parser.add_argument("-o", "--output",
                        help="write results here instead of printing them")
    return parser

def parse_created_date(text):
    try:
        return date(int(text[6:10]), int(text[0:2]), int(text[3:5]))
    except ValueError:
        return None


def count_complaints(path, start, end):
    counts = Counter()
    with open(path, newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            created = parse_created_date(row["Created Date"])
            if created is None or not (start <= created <= end):
                continue
            key = (row["Complaint Type"], row["Borough"])
            counts[key] += 1
    return counts

def write_results(counts, out):
    writer = csv.writer(out, lineterminator="\n")
    writer.writerow(["complaint type", "borough", "count"])
    for (complaint, borough), n in sorted(counts.items()):
        writer.writerow([complaint, borough, n])

def main():
    args = build_parser().parse_args()
    counts = count_complaints(args.input, args.start, args.end)
    if args.output:
        with open(args.output, "w", newline="") as out:
            write_results(counts, out)
    else:
        write_results(counts, sys.stdout)
#"Run main when this file executes"
if __name__ == "__main__":
    main()
