from flask import Flask, render_template, request, jsonify, redirect, url_for, session
import sqlite3
import os
import tempfile
import json
import secrets
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime
from flask_cors import CORS
from brain import BrainInputError, BrainProviderError, chat_reply, generate_schedule

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.environ.get("DAYFLOW_DB_PATH", os.path.join(tempfile.gettempdir(), "dayflow_runtime.db"))

app = Flask(__name__, template_folder="templates", static_folder="static")
app.secret_key = os.environ.get("DAYFLOW_SECRET_KEY", "change_this_secret_in_prod")
CORS(app, support_credentials=True)

@app.after_request
def add_build_header(response):
    response.headers["X-DayFlow-Build"] = "brain-2"
    return response

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
            password TEXT NOT NULL,
            google_id TEXT,
            auth_provider TEXT DEFAULT 'password'
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

    conn = get_conn()
    c = conn.cursor()
    c.execute("PRAGMA table_info(users)")
    user_columns = {row[1] for row in c.fetchall()}
    if "google_id" not in user_columns:
        c.execute("ALTER TABLE users ADD COLUMN google_id TEXT")
    if "auth_provider" not in user_columns:
        c.execute("ALTER TABLE users ADD COLUMN auth_provider TEXT DEFAULT 'password'")
    c.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_users_google_id ON users(google_id) WHERE google_id IS NOT NULL")
    c.execute("PRAGMA table_info(tasks)")
    task_columns = {row[1] for row in c.fetchall()}
    if "kind" not in task_columns:
        c.execute("ALTER TABLE tasks ADD COLUMN kind TEXT DEFAULT 'focus'")
    c.execute("""
        CREATE TABLE IF NOT EXISTS reminders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            task_id INTEGER,
            title TEXT NOT NULL,
            remind_time TEXT NOT NULL,
            enabled INTEGER DEFAULT 1,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(user_id) REFERENCES users(id),
            FOREIGN KEY(task_id) REFERENCES tasks(id)
        )
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


# ---------- Google OAuth ----------
def google_oauth_config():
    return {
        "client_id": os.environ.get("GOOGLE_CLIENT_ID", "").strip(),
        "client_secret": os.environ.get("GOOGLE_CLIENT_SECRET", "").strip(),
        "redirect_uri": os.environ.get("GOOGLE_REDIRECT_URI", url_for("google_callback", _external=True)),
    }

@app.route("/auth/google")
def google_login():
    config = google_oauth_config()
    if not config["client_id"] or not config["client_secret"]:
        return redirect(url_for("login_page", error="Google sign-in is not configured yet."))

    state = secrets.token_urlsafe(24)
    session["google_oauth_state"] = state
    params = {
        "client_id": config["client_id"],
        "redirect_uri": config["redirect_uri"],
        "response_type": "code",
        "scope": "openid email profile",
        "state": state,
        "prompt": "select_account",
    }
    auth_url = "https://accounts.google.com/o/oauth2/v2/auth?" + urllib.parse.urlencode(params)
    return redirect(auth_url)

@app.route("/auth/google/callback")
def google_callback():
    if request.args.get("error"):
        provider_error = (
            request.args.get("error_description")
            or request.args.get("error")
            or "The request was cancelled."
        )
        return redirect(url_for("login_page", error=f"Google sign-in failed: {provider_error}"))

    state = request.args.get("state")
    if not state or state != session.pop("google_oauth_state", None):
        return redirect(url_for("login_page", error="Google sign-in could not be verified."))

    code = request.args.get("code")
    if not code:
        return redirect(url_for("login_page", error="Google did not return a sign-in code."))

    config = google_oauth_config()
    try:
        token_body = urllib.parse.urlencode({
            "code": code,
            "client_id": config["client_id"],
            "client_secret": config["client_secret"],
            "redirect_uri": config["redirect_uri"],
            "grant_type": "authorization_code",
        }).encode("utf-8")
        token_request = urllib.request.Request(
            "https://oauth2.googleapis.com/token",
            data=token_body,
            headers={"Content-Type": "application/x-www-form-urlencoded", "Accept": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(token_request, timeout=10) as response:
            token_data = json.loads(response.read().decode("utf-8"))

        access_token = token_data.get("access_token")
        if not access_token:
            return redirect(url_for("login_page", error="Google did not return an access token."))

        user_request = urllib.request.Request(
            "https://www.googleapis.com/oauth2/v3/userinfo",
            headers={"Authorization": f"Bearer {access_token}", "Accept": "application/json"},
        )
        with urllib.request.urlopen(user_request, timeout=10) as response:
            profile = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        try:
            error_data = json.loads(exc.read().decode("utf-8"))
            provider_error = (
                error_data.get("error_description")
                or error_data.get("error")
                or f"Google returned HTTP {exc.code}."
            )
        except (json.JSONDecodeError, UnicodeDecodeError):
            provider_error = f"Google returned HTTP {exc.code}."
        return redirect(url_for("login_page", error=f"Google sign-in failed: {provider_error}"))
    except urllib.error.URLError as exc:
        reason = getattr(exc, "reason", exc)
        return redirect(url_for("login_page", error=f"Google connection failed: {reason}"))
    except json.JSONDecodeError:
        return redirect(url_for("login_page", error="Google returned an unreadable response."))

    google_id = profile.get("sub")
    email = (profile.get("email") or "").strip().lower()
    name = (profile.get("name") or email.split("@")[0]).strip()
    if not google_id or not email:
        return redirect(url_for("login_page", error="Google did not share the required profile details."))

    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT id,name FROM users WHERE google_id=? OR email=?", (google_id, email))
    row = c.fetchone()
    if row:
        user_id = row["id"]
        display_name = row["name"] or name
        c.execute(
            "UPDATE users SET google_id=?, auth_provider=?, name=? WHERE id=?",
            (google_id, "google", display_name, user_id),
        )
    else:
        c.execute(
            "INSERT INTO users (name,email,password,google_id,auth_provider) VALUES (?,?,?,?,?)",
            (name, email, "", google_id, "google"),
        )
        user_id = c.lastrowid
        display_name = name
    conn.commit()
    conn.close()

    session["user_id"] = user_id
    session["name"] = display_name
    return redirect(url_for("dashboard_page"))
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

@app.route("/api/goal", methods=["GET"])
def api_goal_get():
    uid = session.get("user_id")
    if not uid:
        return jsonify({"status":"error","message":"Not logged in"}), 401
    conn = get_conn()
    c = conn.cursor()
    c.execute("""
        SELECT goal_type, duration, start_date
        FROM goals
        WHERE user_id=?
        ORDER BY id DESC
        LIMIT 1
    """, (uid,))
    row = c.fetchone()
    conn.close()
    if not row:
        return jsonify({"status":"ok","goal": None})
    return jsonify({"status":"ok","goal": dict(row)})
@app.route("/api/generate_schedule", methods=["POST"])
def api_generate_schedule():
    uid = session.get("user_id")
    if not uid:
        return jsonify({"status": "error", "message": "Not logged in"}), 401

    data = request.get_json(silent=True) or {}
    wake = str(data.get("wake", "")).strip()
    sleep = str(data.get("sleep", "")).strip()
    constraints = str(data.get("constraints", "")).strip()
    routine = data.get("routine") if isinstance(data.get("routine"), dict) else {}

    conn = get_conn()
    c = conn.cursor()
    c.execute(
        """
        SELECT goal_type, duration, start_date
        FROM goals
        WHERE user_id=?
        ORDER BY id DESC
        LIMIT 1
        """,
        (uid,),
    )
    goal_row = c.fetchone()
    if not goal_row:
        conn.close()
        return jsonify({
            "status": "error",
            "message": "Set your goal before generating a schedule.",
        }), 400

    try:
        result = generate_schedule(dict(goal_row), wake, sleep, constraints, routine)
    except BrainInputError as error:
        conn.close()
        return jsonify({"status": "error", "message": str(error)}), 400
    except BrainProviderError as error:
        conn.close()
        return jsonify({"status": "error", "message": str(error)}), 502

    if result.get("status") == "needs_clarification":
        conn.close()
        return jsonify({
            "status": "needs_clarification",
            "message": "I need a little more detail before building the day.",
            "questions": result.get("questions", []),
        }), 422

    reminders = []
    try:
        c.execute("DELETE FROM reminders WHERE user_id=?", (uid,))
        c.execute("DELETE FROM tasks WHERE user_id=?", (uid,))
        for task in result["tasks"]:
            c.execute(
                """
                INSERT INTO tasks (user_id, name, start_time, end_time, priority, kind)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    uid,
                    task["name"],
                    task["start"],
                    task["end"],
                    task["priority"],
                    task.get("kind", "focus"),
                ),
            )
            task_id = c.lastrowid
            title = f"Start: {task['name']}"
            c.execute(
                """
                INSERT INTO reminders (user_id, task_id, title, remind_time, enabled)
                VALUES (?, ?, ?, ?, 1)
                """,
                (uid, task_id, title, task["start"]),
            )
            reminders.append({
                "id": c.lastrowid,
                "task_id": task_id,
                "title": title,
                "remind_time": task["start"],
                "enabled": 1,
            })
        conn.commit()
    except sqlite3.Error:
        conn.rollback()
        conn.close()
        return jsonify({
            "status": "error",
            "message": "The schedule was generated but could not be saved.",
        }), 500
    conn.close()

    return jsonify({
        "status": "ok",
        "tasks": result["tasks"],
        "reminders": reminders,
        "brain": {"engine": result["engine"], "ai": result["ai"]},
    })


@app.route("/api/reminders", methods=["GET", "POST", "PUT", "DELETE"])
def api_reminders():
    uid = session.get("user_id")
    if not uid:
        return jsonify({"status": "error", "message": "Not logged in"}), 401

    conn = get_conn()
    c = conn.cursor()

    if request.method == "GET":
        c.execute(
            """
            SELECT id, task_id, title, remind_time, enabled
            FROM reminders
            WHERE user_id=?
            ORDER BY remind_time
            """,
            (uid,),
        )
        rows = [dict(row) for row in c.fetchall()]
        conn.close()
        return jsonify({"status": "ok", "reminders": rows})

    data = request.get_json(silent=True) or {}
    if request.method == "POST":
        title = str(data.get("title", "")).strip()
        remind_time = str(data.get("remind_time", "")).strip()
        task_id = data.get("task_id")
        if not title or len(remind_time) != 5 or remind_time[2] != ":":
            conn.close()
            return jsonify({"status": "error", "message": "Add a title and valid reminder time."}), 400
        c.execute(
            """
            INSERT INTO reminders (user_id, task_id, title, remind_time, enabled)
            VALUES (?, ?, ?, ?, 1)
            """,
            (uid, task_id, title, remind_time),
        )
        conn.commit()
        reminder_id = c.lastrowid
        conn.close()
        return jsonify({
            "status": "ok",
            "reminder": {
                "id": reminder_id,
                "task_id": task_id,
                "title": title,
                "remind_time": remind_time,
                "enabled": 1,
            },
        })

    reminder_id = data.get("id")
    if not reminder_id:
        conn.close()
        return jsonify({"status": "error", "message": "Missing reminder id."}), 400

    if request.method == "PUT":
        enabled = 1 if data.get("enabled") else 0
        c.execute("UPDATE reminders SET enabled=? WHERE id=? AND user_id=?", (enabled, reminder_id, uid))
        conn.commit()
        conn.close()
        return jsonify({"status": "ok"})

    if request.method == "DELETE":
        c.execute("DELETE FROM reminders WHERE id=? AND user_id=?", (reminder_id, uid))
        conn.commit()
        conn.close()
        return jsonify({"status": "ok"})


@app.route("/api/chat", methods=["POST"])
def api_chat():
    uid = session.get("user_id")
    if not uid:
        return jsonify({"status": "error", "message": "Not logged in"}), 401

    data = request.get_json(silent=True) or {}
    message = str(data.get("message", "")).strip()
    conn = get_conn()
    c = conn.cursor()
    c.execute(
        """
        SELECT goal_type, duration, start_date
        FROM goals
        WHERE user_id=?
        ORDER BY id DESC
        LIMIT 1
        """,
        (uid,),
    )
    goal = c.fetchone()
    c.execute(
        """
        SELECT name, start_time, end_time, priority, kind, done
        FROM tasks
        WHERE user_id=?
        ORDER BY start_time
        LIMIT 12
        """,
        (uid,),
    )
    tasks = [dict(row) for row in c.fetchall()]
    conn.close()

    try:
        result = chat_reply(message, {
            "goal": dict(goal) if goal else None,
            "tasks": tasks,
        })
    except BrainInputError as error:
        return jsonify({"status": "error", "message": str(error)}), 400
    except BrainProviderError as error:
        return jsonify({"status": "error", "message": str(error)}), 502

    return jsonify({
        "status": "ok",
        "reply": result["reply"],
        "brain": {"engine": result["engine"], "ai": result["ai"]},
    })
@app.route("/api/tasks", methods=["GET","POST","PUT","DELETE"])
def api_tasks():
    uid = session.get("user_id")
    if not uid:
        return jsonify({"status":"error","message":"Not logged in"}), 401
    conn = get_conn()
    c = conn.cursor()

    if request.method == "GET":
        c.execute("SELECT id,name,start_time,end_time,priority,kind,done FROM tasks WHERE user_id=? ORDER BY start_time", (uid,))
        rows = c.fetchall()
        tasks = [dict(r) for r in rows]
        conn.close()
        return jsonify({"status":"ok","tasks":tasks})

    if request.method == "POST":
        data = request.get_json()
        tasks = data.get("tasks", [])
        for t in tasks:
            c.execute("INSERT INTO tasks (user_id,name,start_time,end_time,priority,kind) VALUES (?,?,?,?,?,?)",
                      (uid, t.get("name"), t.get("start"), t.get("end",""), t.get("priority","medium"), t.get("kind","focus")))
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
        for key in ("name","start","end","priority","kind","done"):
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



