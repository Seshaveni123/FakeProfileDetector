"""One-time, non-destructive migration from the legacy SQLite history database.

Usage: DATABASE_URL=... python services/history-service/migrate_sqlite.py backend/predictions.db
"""
import os
import sqlite3
import sys

import psycopg

if len(sys.argv) != 2:
    raise SystemExit("Usage: migrate_sqlite.py PATH_TO_LEGACY_PREDICTIONS_DB")

database_url = os.environ["DATABASE_URL"]
sqlite_path = sys.argv[1]
source = sqlite3.connect(sqlite_path)
source.row_factory = sqlite3.Row
rows = source.execute("SELECT timestamp, platform, username, followers_count, following_count, follower_ratio, posts_or_tweets, bio_length, engagement_rate, prediction, probability, risk_level, source FROM predictions ORDER BY id").fetchall()

statement = """INSERT INTO predictions (timestamp, platform, username, followers_count, following_count, follower_ratio, posts_or_tweets, bio_length, engagement_rate, prediction, probability, risk_level, source)
VALUES (%(timestamp)s, %(platform)s, %(username)s, %(followers_count)s, %(following_count)s, %(follower_ratio)s, %(posts_or_tweets)s, %(bio_length)s, %(engagement_rate)s, %(prediction)s, %(probability)s, %(risk_level)s, %(source)s)"""
with psycopg.connect(database_url) as destination:
    with destination.cursor() as cursor:
        for row in rows:
            cursor.execute(statement, dict(row))
    destination.commit()
print(f"Migrated {len(rows)} history records; the SQLite source was not changed.")
