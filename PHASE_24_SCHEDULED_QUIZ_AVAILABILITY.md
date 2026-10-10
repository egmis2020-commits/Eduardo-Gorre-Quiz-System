# V24 – Scheduled Quiz Availability

## Purpose
Add optional scheduling to existing quizzes without changing the existing quiz engine or deleting existing records.

## Scheduling fields
- `available_from`: optional local server date/time.
- `available_until`: optional local server date/time.
- Both blank: quiz behaves exactly as before and remains available.

## Student behavior
- Before opening: **Scheduled / Not Yet Available**
- During window: **Available Now / Start Quiz**
- At or after closing: **Closed / Quiz Closed**

## Server enforcement
Availability is checked server-side:
- `/quiz/<qid>` refuses access outside the scheduled window.
- `/submit` refuses a new submission when the quiz has not opened.
- A quiz started before its closing time may finish and submit after the closing time.

## Validation
- Invalid date/time values are rejected.
- If both are supplied, the end must be later than the start.

## Database safety
V24 adds only two nullable columns to `quizzes`. Existing rows receive NULL values, which means always available. Existing questions and attempts are not modified by the migration.

## Testing performed
- Python syntax compilation passed for `app.py`.
- SQLite migration test passed on a copy of the supplied V23.1 `quiz.db`.
- Existing quiz/question data remained intact in the migration test.
- The live Flask server was not run in this build environment because the environment does not include the application's Flask dependency.
