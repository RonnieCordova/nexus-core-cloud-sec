import sqlite3
import unittest
from pathlib import Path

from app.core import db as db_module


class DbInitTests(unittest.TestCase):
    def test_init_db_creates_expected_tables(self):
        tmp_dir = Path(".tmp-tests")
        tmp_dir.mkdir(exist_ok=True)
        db_file = tmp_dir / "test.db"
        original_path = db_module.settings.db_path
        db_module.settings.db_path = str(db_file)

        try:
            db_module.init_db()
            with sqlite3.connect(db_file) as conn:
                tables = {
                    row[0]
                    for row in conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
                }
            expected = {"tenants", "users", "tokens", "aws_accounts", "scans", "findings"}
            self.assertTrue(expected.issubset(tables))
        finally:
            db_module.settings.db_path = original_path
            if db_file.exists():
                db_file.unlink()
            if tmp_dir.exists() and not any(tmp_dir.iterdir()):
                tmp_dir.rmdir()


if __name__ == "__main__":
    unittest.main()
