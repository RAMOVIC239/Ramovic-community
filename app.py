import sqlite3
import os
from flask import Flask, render_template, request, redirect, session

app = Flask(__name__)
app.secret_key = "ramovic_secret"

# ---------------- DATABASE ----------------
def init_db():
    conn = sqlite3.connect("database.db")
    c = conn.cursor()

    c.execute("""
    CREATE TABLE IF NOT EXISTS applicants (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        phone TEXT,
        level TEXT,
        reason TEXT,
        status TEXT DEFAULT 'pending',
        whatsapp_link TEXT
    )
    """)

    conn.commit()
    conn.close()

init_db()

# ---------------- HOME ----------------
@app.route("/")
def home():
    return render_template("index.html")

# ---------------- REGISTER ----------------
@app.route("/register")
def register():
    return render_template("register.html")

# ---------------- SUBMIT ----------------
@app.route("/submit", methods=["POST"])
def submit():
    name = request.form["name"]
    phone = request.form["phone"]
    level = request.form["level"]
    reason = request.form["reason"]

    conn = sqlite3.connect("database.db")
    c = conn.cursor()

    c.execute("""
    INSERT INTO applicants(name, phone, level, reason)
    VALUES (?, ?, ?, ?)
    """, (name, phone, level, reason))

    applicant_id = c.lastrowid

    conn.commit()
    conn.close()

    return redirect(f"/result/{applicant_id}")

# ---------------- LOGIN ----------------
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        if request.form["username"] == "admin" and request.form["password"] == "1234":
            session["admin"] = True
            return redirect("/admin")

        return "Wrong login ❌"

    return render_template("login.html")

# ---------------- ADMIN ----------------
@app.route("/admin")
def admin():
    if not session.get("admin"):
        return redirect("/login")

    conn = sqlite3.connect("database.db")
    c = conn.cursor()

    c.execute("SELECT * FROM applicants ORDER BY id DESC")
    data = c.fetchall()

    conn.close()

    return render_template("admin.html", data=data)

# ---------------- APPROVE ----------------
@app.route("/approve/<int:id>")
def approve(id):
    conn = sqlite3.connect("database.db")
    c = conn.cursor()

    link = "https://chat.whatsapp.com/KPvURPn4n0UGlfhTbZDjZC"

    c.execute("""
    UPDATE applicants
    SET status='approved', whatsapp_link=?
    WHERE id=?
    """, (link, id))

    conn.commit()
    conn.close()

    return redirect(f"/result/{id}")

# ---------------- REJECT ----------------
@app.route("/reject/<int:id>")
def reject(id):
    conn = sqlite3.connect("database.db")
    c = conn.cursor()

    c.execute("""
    UPDATE applicants
    SET status='rejected'
    WHERE id=?
    """, (id,))

    conn.commit()
    conn.close()

    return redirect(f"/result/{id}")

# ---------------- RESULT ----------------
@app.route("/result/<int:id>")
def result(id):
    conn = sqlite3.connect("database.db")
    c = conn.cursor()

    c.execute("SELECT * FROM applicants WHERE id=?", (id,))
    user = c.fetchone()

    conn.close()

    return render_template("result.html", user=user)

# ---------------- LOGOUT ----------------
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

# ---------------- RUN ----------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
