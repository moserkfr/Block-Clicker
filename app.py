from cs50 import SQL
from flask import Flask, flash, jsonify, render_template, redirect, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash

app = Flask(__name__)

app.config["TEMPLATES_AUTO_RELOAD"] = True

db = SQL("sqlite:///gamers.db")

app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

@app.route("/")
def index():
    if not session.get("user_id"):
        return redirect("/login")
    
    user_id = session["user_id"]
    user = db.execute("SELECT * FROM users WHERE id = ?", user_id)[0]

    upgrades = {
        "pickaxe": {"cost": 10, "multiplier": 1.2, "effect": "bpc", "power": 1},
        "friend": {"cost": 100, "multiplier": 1.5, "effect": "bps", "power": 1},
        "beacon": {"cost": 1000, "multiplier": 2, "effect": "bps", "power": 10}
    }

    template_upgrades = {}
    for upgrade_type, stats in upgrades.items():
        row = db.execute("SELECT level FROM upgrades WHERE user_id = ? AND upgrade_name = ?", user_id, upgrade_type)
        
        if not row:
            level = 0
        else:
            level = row[0]["level"]
        
        current_cost = int(stats["cost"] * (stats["multiplier"] ** level))
        
        template_upgrades[upgrade_type] = {
            "cost": current_cost,
            "level": level
        }

    return render_template("index.html", user=user, upgrades=template_upgrades)


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")

        if not username or not password or not confirmation:
            return render_template("register.html", message="Please fill out all fields.")

        if password != confirmation:
            return render_template("register.html", message="Passwords do not match.")
        
        existing = db.execute("SELECT * FROM users WHERE username = ?", username)
        if existing:
            return render_template("register.html", message="Username already taken.")

        hash_password = generate_password_hash(password)

        db.execute("INSERT INTO users (username, hash) VALUES (?, ?)", username, hash_password)

        flash("Registered successfully!")
        return redirect("/login")

    else:
        return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        if not username or not password:
            return render_template("login.html", message="Please fill out all fields.")

        rows = db.execute("SELECT * FROM users WHERE username = ?", username)

        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], password):
            return render_template("login.html", message="Invalid username and/or password.")

        session["user_id"] = rows[0]["id"]

        flash("Logged in successfully!")
        return redirect("/")
    else:
        return render_template("login.html")

@app.route("/logout")
def logout():
    """Log user out"""
    session.clear()
    flash("Logged out successfully!")
    return redirect("/")

@app.route("/leaderboard")
def leaderboard():
    """Show leaderboard"""
    users = db.execute("SELECT username, blocks FROM users ORDER BY blocks DESC")
    return render_template("leaderboard.html", users=users)

@app.route("/mine", methods=["POST"])
def mine():
    """Mine a block"""
    if not session.get("user_id"):
        return redirect("/login")

    bpc=db.execute("SELECT bpc FROM users WHERE id = ?", session["user_id"])[0]["bpc"]
    db.execute("UPDATE users SET blocks = blocks + ? WHERE id = ?",bpc, session["user_id"])
    total = db.execute("SELECT blocks FROM users WHERE id = ?", session["user_id"])[0]["blocks"]
    return {"blocks": total}

@app.route("/upgrade", methods=["POST"])
def upgrade():
    if not session.get("user_id"):
        return redirect("/login")
    
    upgrade_type = request.json.get("upgrade_type")
    user_id = session["user_id"]

    user = db.execute("SELECT * FROM users WHERE id = ?", user_id)[0]

    upgrades = {
        "pickaxe": {"cost": 10, "multiplier": 1.2, "effect": "bpc", "power": 1},
        "friend": {"cost": 100, "multiplier": 1.5, "effect": "bps", "power": 1},
        "beacon": {"cost": 1000, "multiplier": 2, "effect": "bps", "power": 10}
    }

    if upgrade_type not in upgrades:
        return jsonify({"error": "Invalid upgrade type"}), 400

    stats = upgrades[upgrade_type]

    row = db.execute("SELECT level FROM upgrades WHERE user_id = ? AND upgrade_name = ?", user_id, upgrade_type)

    if not row:
        db.execute("INSERT INTO upgrades (user_id, upgrade_name, level) VALUES (?, ?, ?)", user_id, upgrade_type, 0)
        level = 0
    else:
        level = row[0]["level"]

    base = stats["cost"]
    cost = int(base * (stats["multiplier"] ** level))

    if user["blocks"] < cost:
        return jsonify({"error": "Not enough blocks"}), 400

    db.execute("UPDATE users SET blocks = blocks - ? WHERE id = ?", cost, user_id)

    db.execute("UPDATE upgrades SET level = level + 1 WHERE user_id = ? AND upgrade_name = ?", user_id, upgrade_type)

    if stats["effect"] == "bpc":
        db.execute("UPDATE users SET bpc = bpc + ? WHERE id = ?", stats["power"], user_id)
    elif stats["effect"] == "bps":
        db.execute("UPDATE users SET bps = bps + ? WHERE id = ?", stats["power"], user_id)


    updated = db.execute("SELECT * FROM users WHERE id = ?", user_id)[0]
    new_level = level + 1
    next_cost = int(base * (stats["multiplier"] ** new_level))

    return jsonify({
        "blocks": updated["blocks"],
        "bpc": updated["bpc"],
        "bps": updated["bps"],
        "level": new_level,
        "next_cost": next_cost,
        "upgrade_type": upgrade_type
    })

@app.route("/auto_mine", methods=["POST"])
def auto_mine():
    """Add BPS blocks automatically"""
    if not session.get("user_id"):
        return jsonify({"error": "Not logged in"}), 401 

    user_id = session["user_id"]
    
    bps = db.execute("SELECT bps FROM users WHERE id = ?", user_id)[0]["bps"]

    if bps > 0:
        db.execute("UPDATE users SET blocks = blocks + ? WHERE id = ?", bps, user_id)
    
    total = db.execute("SELECT blocks FROM users WHERE id = ?", user_id)[0]["blocks"]
    return jsonify({"blocks": total})