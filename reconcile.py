#!/usr/bin/env python3

import json
from decimal import Decimal, InvalidOperation
from pathlib import Path

BASE = Path(__file__).resolve().parent


def main():
    latest = {}

    with (BASE / "payments.jsonl").open(encoding="utf-8") as file:
        for index, line in enumerate(file):
            try:
                event = json.loads(line)
            except json.JSONDecodeError:
                continue

            if not isinstance(event, dict):
                continue

            txn_id = event.get("txn_id")
            if not isinstance(txn_id, str) or not txn_id:
                continue

            timestamp = event.get("ts")
            if not isinstance(timestamp, str):
                continue

            previous = latest.get(txn_id)

            if previous is None or (timestamp, index) > (
                previous[0], previous[1]
            ):
                latest[txn_id] = (timestamp, index, event)

    count = 0
    total = Decimal("0")

    for _, _, event in latest.values():
        if event.get("status") != "success":
            continue

        try:
            amount = Decimal(
                str(event["amount"]).replace(",", "").strip()
            )
        except (KeyError, InvalidOperation, ValueError):
            continue

        if not amount.is_finite():
            continue

        count += 1
        total += amount

    expected = int(
        (BASE / "expected.txt").read_text().strip()
    )

    if count != expected:
        print(f"FAIL: Expected {expected}, got {count}")
    else:
        print(f"PASS: {count} successful payments")
        print(f"CODE: KOYA-{round(total)}")


if __name__ == "__main__":
    main()
