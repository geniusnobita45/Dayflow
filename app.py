from flask import Flask, render_template, request, jsonify, redirect, url_for, session
import sqlite3
import os
from datetime import datetime
from flask_cors import CORS

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "dayflow.db")

app = Flask(__name__, template_folder="templates", static_folder="static")
app.secret_key = "change_this_secret_in_prod"
CORS(app, support_credentials=True)

# ---------- DB helpers ----------
def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    if not os.path.exists(DB_PATH):
        conn = get_conn()
        c = conn.cursor()
        c.execute("""
        CREATE TABLE users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        );
        """)
        c.execute("""
        CREATE TABLE goals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            goal_type TEXT,
            duration INTEGER,
            start_date TEXT,
            FOREIGN KEY(user_id) REFERENCES users(id)
        );
        """)
        c.execute("""
        CREATE TABLE tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            name TEXT,
            start_time TEXT,
            end_time TEXT,
            priority TEXT,
            done INTEGER DEFAULT 0,
            FOREIGN KEY(user_id) REFERENCES users(id)
        );
        """)
        conn.commit()
        conn.close()

init_db()

# ---------- Template routes ----------
@app.route("/")
def index():
    return redirect(url_for('signup'))

@app.route("/signup", methods=["GET"])
def signup():
    return render_template("signup.html")

@app.route("/login", methods=["GET"])
def login_page():
    return render_template("login.html")

@app.route("/goal-setup", methods=["GET"])
def goal_setup_page():
    return render_template("goal-setup.html")

@app.route("/timetable-choice", methods=["GET"])
def timetable_choice_page():
    return render_template("timetable-choice.html")

@app.route("/timetable-input", methods=["GET"])
def timetable_input_page():
    return render_template("timetable-input.html")

@app.route("/timetable-generator", methods=["GET"])
def timetable_generator_page():
    return render_template("timetable-generator.html")

@app.route("/dashboard", methods=["GET"])
def dashboard_page():
    return render_template("dashboard.html")

@app.route("/settings", methods=["GET"])
def settings_page():
    return render_template("settings.html")

@app.route("/about", methods=["GET"])
def about_page():
    return render_template("about.html")


# ---------- API endpoints ----------
@app.route("/api/signup", methods=["POST"])
def api_signup():
    data = request.get_json()
    name = data.get("name","").strip()
    email = data.get("email","").strip().lower()
    password = data.get("password","")
    if not name or not email or not password:
        return jsonify({"status":"error","message":"Missing fields"}), 400
    conn = get_conn()
    c = conn.cursor()
    try:
        c.execute("INSERT INTO users (name,email,password) VALUES (?,?,?)", (name,email,password))
        conn.commit()
        user_id = c.lastrowid
        session["user_id"] = user_id
        session["name"] = name
        conn.close()
        return jsonify({"status":"ok","name":name})
    except sqlite3.IntegrityError:
        conn.close()
        return jsonify({"status":"error","message":"Email already exists"}), 400

@app.route("/api/login", methods=["POST"])
def api_login():
    data = request.get_json()
    email = data.get("email","").strip().lower()
    password = data.get("password","")
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT id,name FROM users WHERE email=? AND password=?", (email,password))
    row = c.fetchone()
    conn.close()
    if row:
        session["user_id"] = row["id"]
        session["name"] = row["name"]
        return jsonify({"status":"ok","name":row["name"]})
    else:
        return jsonify({"status":"error","message":"Invalid credentials"}), 401

@app.route("/api/logout", methods=["POST"])
def api_logout():
    session.clear()
    return jsonify({"status":"ok"})

@app.route("/api/user", methods=["GET"])
def api_user():
    uid = session.get("user_id")
    if not uid:
        return jsonify({"status":"error","message":"Not logged in"}), 401
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT id,name,email FROM users WHERE id=?", (uid,))
    row = c.fetchone()
    conn.close()
    if not row:
        return jsonify({"status":"error","message":"User not found"}), 404
    return jsonify({"status":"ok","user": {"id": row["id"], "name": row["name"], "email": row["email"]}})

@app.route("/api/goal", methods=["POST"])
def api_goal():
    uid = session.get("user_id")
    if not uid:
        return jsonify({"status":"error","message":"Not logged in"}), 401
    data = request.get_json()
    goal_type = data.get("type")
    duration = int(data.get("duration",0))
    start_date = datetime.now().strftime("%Y-%m-%d")
    conn = get_conn()
    c = conn.cursor()
    c.execute("INSERT INTO goals (user_id,goal_type,duration,start_date) VALUES (?,?,?,?)", (uid,goal_type,duration,start_date))
    conn.commit()
    conn.close()
    return jsonify({"status":"ok"})

@app.route("/api/tasks", methods=["GET","POST","PUT","DELETE"])
def api_tasks():
    uid = session.get("user_id")
    if not uid:
        return jsonify({"status":"error","message":"Not logged in"}), 401
    conn = get_conn()
    c = conn.cursor()

    if request.method == "GET":
        c.execute("SELECT id,name,start_time,end_time,priority,done FROM tasks WHERE user_id=? ORDER BY start_time", (uid,))
        rows = c.fetchall()
        tasks = [dict(r) for r in rows]
        conn.close()
        return jsonify({"status":"ok","tasks":tasks})

    if request.method == "POST":
        data = request.get_json()
        tasks = data.get("tasks", [])
        for t in tasks:
            c.execute("INSERT INTO tasks (user_id,name,start_time,end_time,priority) VALUES (?,?,?,?,?)",
                      (uid, t.get("name"), t.get("start"), t.get("end",""), t.get("priority","medium")))
        conn.commit()
        conn.close()
        return jsonify({"status":"ok"})

    if request.method == "PUT":
        data = request.get_json()
        # Expect: { id, name?, start?, end?, priority?, done? }
        tid = data.get("id")
        if not tid:
            return jsonify({"status":"error","message":"Missing id"}), 400
        # build update
        fields = []
        values = []
        for key in ("name","start","end","priority","done"):
            if key in data:
                dbcol = "start_time" if key=="start" else ("end_time" if key=="end" else ("done" if key=="done" else key))
                fields.append(f"{dbcol}=?")
                values.append(data[key])
        values.append(tid)
        query = f"UPDATE tasks SET {', '.join(fields)} WHERE id=? AND user_id=?"
        values.append(uid)
        # remove the extra uid appended incorrectly: adjust values to (fields..., tid, uid)
        # fix: we constructed values as [fieldvals..., tid] then appended uid; query expects tid AND user_id -> pass tid, uid
        # but earlier we appended tid then appended uid, ok.
        # For SQLite binding we need correct order; we'll execute with values (fieldvals..., tid, uid)
        c.execute(query, tuple(values))
        conn.commit()
        conn.close()
        return jsonify({"status":"ok"})

    if request.method == "DELETE":
        data = request.get_json()
        tid = data.get("id")
        if not tid:
            return jsonify({"status":"error","message":"Missing id"}), 400
        c.execute("DELETE FROM tasks WHERE id=? AND user_id=?", (tid, uid))
        conn.commit()
        conn.close()
        return jsonify({"status":"ok"})

# Quick utility route to wipe all data for the current user (for testing)
@app.route("/api/reset_user", methods=["POST"])
def api_reset_user():
    uid = session.get("user_id")
    if not uid:
        return jsonify({"status":"error","message":"Not logged in"}), 401
    conn = get_conn()
    c = conn.cursor()
    c.execute("DELETE FROM tasks WHERE user_id=?", (uid,))
    c.execute("DELETE FROM goals WHERE user_id=?", (uid,))
    conn.commit()
    conn.close()
    return jsonify({"status":"ok"})

if __name__ == "__main__":
    app.run(debug=True)
