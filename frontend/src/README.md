# Physique — Food logging & nutrition calculator

This repository contains a minimal production-minded app that accepts free-text food logs, parses them using spaCy + rule-based logic, computes nutrition using a MySQL `foods` table, stores logs, and exposes a JSON API consumed by a React frontend.

---

## File tree (key files)
- backend/
  - physiqueneeds1.py
  - app.py
  - db.py
  - models1.sql
  - requirements1.txt
  - tests/
- frontend/
  - package.json
  - src/

---

## 1) Setup MySQL database

1. Start MySQL server.
2. Create DB and tables / seed with sample rows:

```bash
# from your MySQL client:
SOURCE /path/to/backend/models1.sql;
# or copy/paste contents of backend/models1.sql into your MySQL client
