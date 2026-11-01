"""Boring technology: a hand-rolled file format with its own parser and index
is replaced by sqlite3, which ships with Python and has well-known failure modes."""
from __future__ import annotations

import os
import sqlite3
import tempfile


# --- Violation: a home-made append-only store ---
class JobLog:
    def __init__(self, path: str) -> None:
        self.path = path
        open(path, "a").close()

    def put(self, job_id: str, status: str) -> None:
        with open(self.path, "a", encoding="utf-8") as f:
            f.write(f"{job_id}\t{status}\n")  # breaks if a value contains a tab

    def get(self, job_id: str) -> str | None:
        latest = None
        with open(self.path, encoding="utf-8") as f:
            for line in f:  # full scan; compaction, locking and recovery still unwritten
                key, value = line.rstrip("\n").split("\t")
                if key == job_id:
                    latest = value
        return latest


# --- Fix: the boring, already-installed database ---
class JobStore:
    def __init__(self, path: str) -> None:
        self.db = sqlite3.connect(path)
        self.db.execute("CREATE TABLE IF NOT EXISTS jobs (id TEXT PRIMARY KEY, status TEXT NOT NULL)")

    def put(self, job_id: str, status: str) -> None:
        with self.db:
            self.db.execute(
                "INSERT INTO jobs (id, status) VALUES (?, ?) ON CONFLICT(id) DO UPDATE SET status = excluded.status",
                (job_id, status),
            )

    def get(self, job_id: str) -> str | None:
        row = self.db.execute("SELECT status FROM jobs WHERE id = ?", (job_id,)).fetchone()
        return row[0] if row else None


if __name__ == "__main__":
    with tempfile.TemporaryDirectory() as tmp:
        log = JobLog(os.path.join(tmp, "jobs.log"))
        store = JobStore(os.path.join(tmp, "jobs.sqlite3"))
        for job_id, status in (("invoice-1042", "queued"), ("invoice-1043", "queued"), ("invoice-1042", "sent")):
            log.put(job_id, status)
            store.put(job_id, status)
        for job_id in ("invoice-1042", "invoice-1043", "invoice-9999"):
            before, after = log.get(job_id), store.get(job_id)
            print(job_id, after, "same" if before == after else "DIFFERENT")
        store.db.close()
