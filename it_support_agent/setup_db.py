"""
setup_db.py — Creates the MySQL database, users table, and seeds dummy data.
Run once before starting the Flask app: python setup_db.py
"""

import os
import pymysql
from dotenv import load_dotenv

load_dotenv()

MYSQL_HOST     = os.getenv("MYSQL_HOST", "localhost")
MYSQL_PORT     = int(os.getenv("MYSQL_PORT", 3306))
MYSQL_USER     = os.getenv("MYSQL_USER", "root")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD", "")
MYSQL_DB       = os.getenv("MYSQL_DB", "it_support")

DUMMY_USERS = [
    ("Alice",   "Johnson",  "alice.johnson@company.com",   "Engineering",  "Active"),
    ("Bob",     "Martinez", "bob.martinez@company.com",    "HR",           "Active"),
    ("Carol",   "White",    "carol.white@company.com",     "Finance",      "Active"),
    ("David",   "Lee",      "david.lee@company.com",       "Engineering",  "Active"),
    ("Emma",    "Brown",    "emma.brown@company.com",      "Marketing",    "Active"),
    ("Frank",   "Wilson",   "frank.wilson@company.com",    "IT",           "Active"),
    ("Grace",   "Taylor",   "grace.taylor@company.com",    "Sales",        "Active"),
    ("Henry",   "Anderson", "henry.anderson@company.com",  "Finance",      "Disabled"),
    ("Isabella","Thomas",   "isabella.thomas@company.com", "Marketing",    "Active"),
    ("James",   "Jackson",  "james.jackson@company.com",   "IT",           "Active"),
]

def setup():
    # Connect without specifying DB to allow CREATE DATABASE
    conn = pymysql.connect(
        host=MYSQL_HOST,
        port=MYSQL_PORT,
        user=MYSQL_USER,
        password=MYSQL_PASSWORD,
        charset="utf8mb4",
        cursorclass=pymysql.cursors.DictCursor,
    )
    try:
        with conn.cursor() as cur:
            print(f"[setup_db] Creating database '{MYSQL_DB}' if not exists...")
            cur.execute(f"CREATE DATABASE IF NOT EXISTS `{MYSQL_DB}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;")
            cur.execute(f"USE `{MYSQL_DB}`;")

            print("[setup_db] Creating 'users' table if not exists...")
            cur.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id          INT AUTO_INCREMENT PRIMARY KEY,
                    first_name  VARCHAR(100) NOT NULL,
                    last_name   VARCHAR(100) NOT NULL,
                    email       VARCHAR(200) UNIQUE NOT NULL,
                    department  VARCHAR(100),
                    status      ENUM('Active','Disabled') DEFAULT 'Active',
                    created_at  DATETIME DEFAULT CURRENT_TIMESTAMP
                );
            """)

            # Only seed if table is empty
            cur.execute("SELECT COUNT(*) as cnt FROM users;")
            row = cur.fetchone()
            if row["cnt"] == 0:
                print("[setup_db] Seeding dummy users...")
                cur.executemany(
                    """INSERT INTO users (first_name, last_name, email, department, status)
                       VALUES (%s, %s, %s, %s, %s)""",
                    DUMMY_USERS,
                )
                print(f"[setup_db] Inserted {len(DUMMY_USERS)} users.")
            else:
                print(f"[setup_db] Table already has {row['cnt']} users — skipping seed.")

        conn.commit()
        print("[setup_db] Database setup complete.")
    finally:
        conn.close()

if __name__ == "__main__":
    setup()
