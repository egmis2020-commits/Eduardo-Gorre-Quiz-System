EGMIS TLE-ICT-CSS Digital Quiz System — V24.4 Student Administration Patch

This is an overlay patch, not a full application. Extract its files into the existing v24 application folder and allow matching files to be replaced.

Included changes:
- Bulk student account creation from Admin > Students.
- Batch Gender and default Grade Level dropdowns.
- Per-line grade override using two spaces before grade, e.g. Juan Dela Cruz  7.
- Admin editing of complete name, gender, and grade level.
- Public self-registration disabled; old /register bookmarks redirect to Login.
- Login page tells students to request accounts from the school administrator.
- Credentials output includes gender and each student's actual grade; supports printing and CSV export.

Data safety:
- Do not delete quiz.db, analytics.duckdb, static/uploads, or the existing application folder.
- Stop the server before copying files. Back up app.py, templates/students.html, templates/login.html, and templates/bulk_student_credentials.html first.
- After copying, restart using the existing start_lan.bat.

Bulk input:
- Select one Gender for the batch.
- Select a default Grade Level.
- Enter one complete name per line. A line can optionally end in two spaces and grade number, e.g. Juan Dela Cruz  7. Allowed grades: 7–12.
- Up to 200 accounts per batch. Username uses first name in lowercase; collisions get numeric suffixes. Temporary password format is firstname.studentnumber.
- Print/download the generated credential list immediately. Temporary passwords are shown only in the generated result page and are not stored as plaintext in SQLite.


Bulk registration input format: one student per line as Complete Name, Gender, Grade Level. Example: Juan Dela Cruz, Male, 7. Gender must be Male/Female and grade must be 7–12. Commas or tabs may separate the fields.
