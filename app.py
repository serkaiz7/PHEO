# app.py
from flask import Flask, render_template, request, redirect, url_for, session, jsonify, flash
from werkzeug.security import generate_password_hash, check_password_hash
import os, json, time, threading
import requests
from datetime import datetime

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET", "dev-secret-change-me")

# Files (human readable JSON-lines)
DATA_DIR = "data"
USERS_FILE = os.path.join(DATA_DIR, "users.txt")
DONATION_FILE = os.path.join(DATA_DIR, "donations.txt")
TRANSACTION_FILE = os.path.join(DATA_DIR, "transactions.txt")

# Pi address (sole donation address)
PI_ADDRESS = "MALYJFJ5SVD45FBWN2GT4IW67SEZ3IBOFSBSPUFCWV427NBNLG3PWAAAAAAAAIR37PBGG"

# Admin password (set env var in production)
ADMIN_PASS = os.environ.get("ADMIN_PASS", "adminpass123")

# Price cache (simple in-memory cache with TTL)
_price_cache = {"php": 0.0, "usd": 0.0, "ts": 0}
PRICE_TTL = 60  # seconds

COINGECKO_ENDPOINT = "https://api.coingecko.com/api/v3/simple/price?ids=pi-network&vs_currencies=php,usd"

# Helpers for JSON-lines storage (one JSON object per line)
def ensure_data_dir():
    os.makedirs(DATA_DIR, exist_ok=True)
    for p in (USERS_FILE, DONATION_FILE, TRANSACTION_FILE):
        if not os.path.exists(p):
            open(p, "a", encoding="utf-8").close()

def read_lines_json(path):
    out = []
    if not os.path.exists(path):
        return out
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line: continue
            try:
                out.append(json.loads(line))
            except Exception:
                # skip bad line
                continue
    return out

def append_line_json(path, obj):
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(obj, default=str) + "\n")

def overwrite_lines_json(path, list_of_objs):
    with open(path, "w", encoding="utf-8") as f:
        for o in list_of_objs:
            f.write(json.dumps(o, default=str) + "\n")

# Price fetch with TTL caching
def fetch_prices():
    now = time.time()
    if now - _price_cache["ts"] < PRICE_TTL and _price_cache["php"] > 0:
        return {"php": _price_cache["php"], "usd": _price_cache["usd"]}
    try:
        r = requests.get(COINGECKO_ENDPOINT, timeout=6)
        data = r.json().get("pi-network", {})
        php = float(data.get("php", 0.0) or 0.0)
        usd = float(data.get("usd", 0.0) or 0.0)
        _price_cache.update({"php": php, "usd": usd, "ts": now})
        return {"php": php, "usd": usd}
    except Exception:
        # return last known or zeros
        return {"php": _price_cache.get("php", 0.0), "usd": _price_cache.get("usd", 0.0)}

# Utility for code generation
import random, string
def gen_code(n=7):
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=n))

# Compound growth calculator (30% monthly, compounded monthly)
MONTHLY_RATE = 0.30
def compound_value(amount, created_iso, now=None):
    if not now:
        now = datetime.utcnow()
    created = datetime.fromisoformat(created_iso)
    months = (now.year - created.year) * 12 + (now.month - created.month)
    if now.day < created.day:
        months -= 1
    months = max(0, months)
    value = float(amount)
    for _ in range(months):
        value *= (1 + MONTHLY_RATE)
    return round(value, 2), months

# Routes
@app.route("/")
def index():
    return render_template("index.html", pi_address=PI_ADDRESS)

@app.route("/register", methods=["GET","POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username","").strip()
        password = request.form.get("password","")
        if not username or not password:
            flash("All fields required","danger"); return redirect(url_for("register"))
        users = read_lines_json(USERS_FILE)
        if any(u.get("username","").lower()==username.lower() for u in users):
            flash("Username already exists","danger"); return redirect(url_for("register"))
        users.append({"username": username, "password": generate_password_hash(password), "created": datetime.utcnow().isoformat()})
        overwrite_lines_json(USERS_FILE, users)
        flash("Registered — please log in","success")
        return redirect(url_for("login"))
    return render_template("register.html")

@app.route("/login", methods=["GET","POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username","").strip()
        password = request.form.get("password","")
        users = read_lines_json(USERS_FILE)
        for u in users:
            if u.get("username","").lower() == username.lower() and check_password_hash(u.get("password",""), password):
                session["username"] = u["username"]
                flash("Welcome back","success")
                return redirect(url_for("dashboard"))
        flash("Invalid credentials","danger")
        return redirect(url_for("login"))
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.pop("username", None)
    flash("Logged out","info")
    return redirect(url_for("index"))

@app.route("/price")
def price_api():
    p = fetch_prices()
    return jsonify(p)

@app.route("/dashboard")
def dashboard():
    if "username" not in session:
        return redirect(url_for("login"))
    username = session["username"]
    all_entries = read_lines_json(DONATION_FILE)  # stores both provided/requested entries
    user_entries = [e for e in all_entries if e.get("username")==username]
    # compute compound values for provided donations only (and aggregate)
    provided_total = requested_total = compound_total = 0.0
    provided_pi = requested_pi = compound_pi = 0.0
    rows = []
    now = datetime.utcnow()
    for e in user_entries:
        # if older donations stored with 'amount_pi' or 'amount'
        amount_pi = float(e.get("amount_pi", e.get("amount", 0.0)))
        cur_val, months = compound_value(amount_pi, e.get("created"), now)
        rows.append({**e, "amount_pi": amount_pi, "current_value_pi": cur_val, "months": months})
        if e.get("type") == "provided":
            provided_pi += amount_pi
            provided_total += e.get("amount_php_at_time", 0.0)
        elif e.get("type") == "requested":
            requested_pi += amount_pi
            requested_total += e.get("amount_php_at_time", 0.0)
        # compound earnings measure: current_value - original for provided items
        if e.get("type") == "provided":
            compound_pi += (cur_val - amount_pi)
            compound_total += round((cur_val - amount_pi) * fetch_prices().get("php",0.0),2)
    # prepare chart data
    chart_data = {
        "labels": ["Provided (PI)", "Requested (PI)", "Compound (PI)"],
        "values": [round(provided_pi,2), round(requested_pi,2), round(compound_pi,2)]
    }
    status_pending = any(e.get("status","pending")=="pending" for e in user_entries)
    return render_template("dashboard.html",
                           username=username,
                           pi_address=PI_ADDRESS,
                           entries=rows,
                           chart_data=chart_data,
                           pending=status_pending)

@app.route("/action", methods=["POST"])
def action():
    # handles both provide and request
    if "username" not in session:
        flash("Login first","danger"); return redirect(url_for("login"))
    typ = request.form.get("type")
    try:
        amount_pi = float(request.form.get("amount_pi"))
        if amount_pi <= 0:
            raise ValueError()
    except:
        flash("Invalid amount","danger"); return redirect(url_for("dashboard"))
    prices = fetch_prices()
    amount_php = round(amount_pi * prices.get("php", 0.0),2)
    code = gen_code()
    entry = {
        "username": session["username"],
        "type": typ,  # 'provided' or 'requested'
        "amount_pi": amount_pi,
        "amount_php_at_time": amount_php,
        "created": datetime.utcnow().isoformat(),
        "status": "pending",
        "code": code
    }
    append_line_json(DONATION_FILE, entry)
    append_line_json(TRANSACTION_FILE, {"action": typ, "username": session["username"], "code": code, "amount_pi": amount_pi, "amount_php": amount_php, "created": entry["created"]})
    flash(f"{typ.title()} recorded — code: {code}","success")
    return redirect(url_for("dashboard"))

# Admin UI to view pending entries and accept/reject
@app.route("/admin", methods=["GET","POST"])
def admin():
    if request.method == "POST":
        pwd = request.form.get("password","")
        if pwd != ADMIN_PASS:
            flash("Bad admin password","danger")
            return redirect(url_for("admin"))
        session["is_admin"] = True
        return redirect(url_for("admin"))
    if not session.get("is_admin"):
        return render_template("admin.html", auth=False)
    entries = read_lines_json(DONATION_FILE)
    # show only pending
    pending = [e for e in entries if e.get("status","pending")=="pending"]
    return render_template("admin.html", auth=True, pending=pending)

@app.route("/admin/accept", methods=["POST"])
def admin_accept():
    if not session.get("is_admin"):
        flash("Admin required","danger"); return redirect(url_for("admin"))
    code = request.form.get("code")
    entries = read_lines_json(DONATION_FILE)
    changed = False
    for e in entries:
        if e.get("code")==code and e.get("status")=="pending":
            e["status"] = "accepted"
            changed = True
            append_line_json(TRANSACTION_FILE, {"action":"accept","code":code,"username":e.get("username"), "created": datetime.utcnow().isoformat()})
    if changed:
        overwrite_lines_json(DONATION_FILE, entries)
        flash("Accepted","success")
    else:
        flash("Code not found or already processed","danger")
    return redirect(url_for("admin"))

@app.route("/admin/logout")
def admin_logout():
    session.pop("is_admin", None)
    flash("Admin logged out","info")
    return redirect(url_for("admin"))

# Init
if __name__ == "__main__":
    ensure_data_dir()
    app.run(debug=True)
