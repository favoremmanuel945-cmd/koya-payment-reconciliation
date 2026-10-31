const fs = require("fs");

const latest = new Map();

const lines = fs.readFileSync("payments.jsonl", "utf8").split(/\r?\n/);

for (const line of lines) {
  if (!line.trim()) continue;

  let event;

  try {
    event = JSON.parse(line);
  } catch {
    continue;
  }

  if (!event || !event.txn_id) continue;

  const timestamp = Date.parse(event.ts);
  const previous = latest.get(event.txn_id);

  if (
    !previous ||
    timestamp >= Date.parse(previous.ts)
  ) {
    latest.set(event.txn_id, event);
  }
}

let count = 0;
let total = 0;

for (const event of latest.values()) {
  if (event.status === "success") {
    count++;
    const amount = Number(
      String(event.amount).replace(/,/g, "")
    );
    if (!Number.isFinite(amount)) {
      throw new Error(`Invalid amount for ${event.txn_id}`);
    }
    total += amount;
  }
}

const expected = Number(
  fs.readFileSync("expected.txt", "utf8").trim()
);

if (count !== expected) {
  console.log(
    `Check failed: counted ${count} successful payments, expected ${expected}.`
  );
  process.exitCode = 1;
} else {
  console.log(`Check passed: ${count} successful payments.`);
  console.log(`Your code: KOYA-${Math.round(total)}`);
}
