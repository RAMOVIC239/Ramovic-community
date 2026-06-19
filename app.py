
import sqlite3
import os
from flask import Flask, render_template, request, redirect, session

app = Flask(__name__)
app.secret_key = "ramovic_secret"


# DATABASE
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


# HOME
@app.route("/")
def home():
    return render_template("index.html")


# REGISTER
@app.route("/register")
def register():
    return render_template("register.html")


# SUBMIT APPLICATION
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

    return render_template(
        "status.html",
        applicant_id=applicant_id
    )


# CHECK STATUS PAGE
@app.route("/check-status")
def check_status():
    return render_template("check_status.html")


# SEARCH APPLICATION
@app.route("/search", methods=["POST"])
def search():

    applicant_id = request.form["applicant_id"]

    conn = sqlite3.connect("database.db")
    c = conn.cursor()

    c.execute(
        "SELECT * FROM applicants WHERE id=?",
        (applicant_id,)
    )

    user = c.fetchone()

    conn.close()

    if user:
        return render_template("result.html", user=user)

    return "Application Not Found ❌"


# LOGIN
@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        if username == "admin" and password == "1234":
            session["admin"] = True
            return redirect("/admin")

        return "Wrong Login ❌"

    return render_template("login.html")


# ADMIN DASHBOARD
@app.route("/admin")
def admin():

    if not session.get("admin"):
        return redirect("/login")

    conn = sqlite3.connect("database.db")
    c = conn.cursor()

    c.execute(
        "SELECT * FROM applicants ORDER BY id DESC"
    )

    data = c.fetchall()

    conn.close()

    return render_template(
        "admin.html",
        data=data
    )


# APPROVE
@app.route("/approve/<int:id>")
def approve(id):

    if not session.get("admin"):
        return redirect("/login")

    whatsapp_link = "https://chat.whatsapp.com/KPvURPn4n0UGlfhTbZDjZC"

    conn = sqlite3.connect("database.db")
    c = conn.cursor()

    c.execute("""
        UPDATE applicants
        SET status='approved',
            whatsapp_link=?
        WHERE id=?
    """, (whatsapp_link, id))

    conn.commit()
    conn.close()

    return redirect("/admin")


# REJECT
@app.route("/reject/<int:id>")
def reject(id):

    if not session.get("admin"):
        return redirect("/login")

    conn = sqlite3.connect("database.db")
    c = conn.cursor()

    c.execute("""
        UPDATE applicants
        SET status='rejected'
        WHERE id=?
    """, (id,))

    conn.commit()
    conn.close()

    return redirect("/admin")


# RESULT
@app.route("/result/<int:id>")
def result(id):

    conn = sqlite3.connect("database.db")
    c = conn.cursor()

    c.execute(
        "SELECT * FROM applicants WHERE id=?",
        (id,)
    )

    user = c.fetchone()

    conn.close()

    if user:
        return render_template(
            "result.html",
            user=user
        )

    return "Application Not Found ❌"


# LOGOUT
@app.route("/logout")
def logout():

    session.clear()

    return redirect("/")


# RUN
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))

    app.run(
        host="0.0.0.0",
        port=port
    )
