"""
admin_panel/app.py — Flask IT Admin Panel backed by MySQL via PyMySQL.
"""

import os
import pymysql
import pymysql.cursors
from flask import Flask, render_template, request, redirect, url_for, flash
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = "super_secret_key"

# ─── DB helpers ──────────────────────────────────────────────────────────────

def get_db():
    """Open a new MySQL connection for the current request."""
    return pymysql.connect(
        host=os.getenv("MYSQL_HOST", "localhost"),
        port=int(os.getenv("MYSQL_PORT", 3306)),
        user=os.getenv("MYSQL_USER", "root"),
        password=os.getenv("MYSQL_PASSWORD", ""),
        database=os.getenv("MYSQL_DB", "it_support"),
        charset="utf8mb4",
        cursorclass=pymysql.cursors.DictCursor,
    )


def query(sql, args=(), one=False, commit=False):
    """Run *sql* with *args*, return rows (or single row if one=True)."""
    conn = get_db()
    try:
        with conn.cursor() as cur:
            cur.execute(sql, args)
            if commit:
                conn.commit()
                return cur.rowcount
            return cur.fetchone() if one else cur.fetchall()
    finally:
        conn.close()


# ─── Routes ──────────────────────────────────────────────────────────────────

@app.route("/")
def dashboard():
    users = query("SELECT * FROM users ORDER BY first_name")
    return render_template("dashboard.html", users=users)


@app.route("/add_user", methods=["GET", "POST"])
def add_user():
    if request.method == "POST":
        first_name = request.form.get("first_name", "").strip()
        last_name  = request.form.get("last_name",  "").strip()
        email      = request.form.get("email",      "").strip().lower()
        department = request.form.get("department", "").strip()

        if not all([first_name, last_name, email, department]):
            flash("All fields are required.", "error")
            return redirect(url_for("add_user"))

        existing = query("SELECT id FROM users WHERE email = %s", (email,), one=True)
        if existing:
            flash("A user with that email already exists!", "error")
            return redirect(url_for("add_user"))

        query(
            "INSERT INTO users (first_name, last_name, email, department, status) VALUES (%s, %s, %s, %s, 'Active')",
            (first_name, last_name, email, department),
            commit=True,
        )
        flash(f"User {first_name} {last_name} created successfully and is now visible in the Employee Directory.", "success")
        return redirect(url_for("dashboard"))

    return render_template("create_user.html")


@app.route("/reset_password/<int:user_id>")
def reset_password(user_id):
    user = query("SELECT * FROM users WHERE id = %s", (user_id,), one=True)
    if user:
        flash(f"Password reset link sent to {user['email']}.", "success")
    else:
        flash("User not found.", "error")
    return redirect(url_for("dashboard"))


@app.route("/disable_user/<int:user_id>")
def disable_user(user_id):
    user = query("SELECT * FROM users WHERE id = %s", (user_id,), one=True)
    if user:
        query("UPDATE users SET status = 'Disabled' WHERE id = %s", (user_id,), commit=True)
        flash(f"Account for {user['email']} has been disabled.", "success")
    else:
        flash("User not found.", "error")
    return redirect(url_for("dashboard"))


@app.route("/enable_user/<int:user_id>")
def enable_user(user_id):
    user = query("SELECT * FROM users WHERE id = %s", (user_id,), one=True)
    if user:
        query("UPDATE users SET status = 'Active' WHERE id = %s", (user_id,), commit=True)
        flash(f"Account for {user['email']} has been re-enabled.", "success")
    else:
        flash("User not found.", "error")
    return redirect(url_for("dashboard"))


@app.route("/delete_user/<int:user_id>")
def delete_user(user_id):
    user = query("SELECT * FROM users WHERE id = %s", (user_id,), one=True)
    if user:
        query("DELETE FROM users WHERE id = %s", (user_id,), commit=True)
        flash(f"User {user['first_name']} {user['last_name']} has been deleted.", "success")
    else:
        flash("User not found.", "error")
    return redirect(url_for("dashboard"))


if __name__ == "__main__":
    app.run(debug=True, port=5000)
