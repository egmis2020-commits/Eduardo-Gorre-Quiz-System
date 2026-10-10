V24.3 Concurrent Registration Improvements

- Keeps Waitress on 0.0.0.0:8000.
- Keeps 8 worker threads and raises accepted connection capacity/backlog for short bursts.
- Moves password hashing before opening the SQLite connection.
- Serializes only the short student-registration database write using the existing process-local DB_WRITE_LOCK.
- Gives a friendly retry message for SQLite busy/locked conditions.
- Keeps existing quiz.db, analytics.duckdb, scheduled availability, audit log, images, and LAN setup.

Operational note: stop the old server before extracting/running this version. Do not overwrite your live folder while the app is running. Keep a copy of the current folder before replacing code. SQLite is still a single-writer database; this reduces collisions but does not make writes parallel. For class use, have students register in smaller groups or create accounts in advance if many devices are slow.
