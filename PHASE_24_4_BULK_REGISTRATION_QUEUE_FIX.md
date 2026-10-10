# V24.4 Student Administration Patch

- Adds a batch Gender dropdown and grade dropdown to Admin > Students.
- Accepts `Complete Name  7` to override the default grade for an individual line.
- Stores each generated student's gender and grade in SQLite.
- Allows Admin to edit complete name, gender, and grade level.
- Disables student self-registration and removes the registration HTML from the patch. The legacy `/register` URL redirects to login.
- Credential print/CSV list includes student number, complete name, username, temporary password, gender, and actual grade level.
- Uses one transaction for a batch, checks username collisions, and retains short database write locking.

This patch has not been load-tested with a full classroom. Validate it on the school laptop with a small batch before class.


Bulk registration input format: one student per line as Complete Name, Gender, Grade Level. Example: Juan Dela Cruz, Male, 7. Gender must be Male/Female and grade must be 7–12. Commas or tabs may separate the fields.
