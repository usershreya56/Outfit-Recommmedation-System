from flask import Flask, render_template, request, redirect, session
import sqlite3
import random

app = Flask(__name__)
app.secret_key = "secret123"

# ---------- DATABASE ----------
def init_db():
    conn = sqlite3.connect("outfits.db")
    c = conn.cursor()

    # Users
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (id INTEGER PRIMARY KEY, username TEXT, password TEXT)''')

    # Wardrobe
    c.execute('''CREATE TABLE IF NOT EXISTS wardrobe
                 (id INTEGER PRIMARY KEY, user_id INTEGER, item TEXT, type TEXT)''')

    # Favorites
    c.execute('''CREATE TABLE IF NOT EXISTS favorites
                 (id INTEGER PRIMARY KEY, user_id INTEGER, outfit TEXT)''')

    conn.commit()
    conn.close()

# ---------- ROUTES ----------

@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        user = request.form["username"]
        pwd = request.form["password"]

        conn = sqlite3.connect("outfits.db")
        c = conn.cursor()

        c.execute("SELECT * FROM users WHERE username=? AND password=?", (user, pwd))
        result = c.fetchone()

        conn.close()

        if result:
            session["user_id"] = result[0]
            return redirect("/dashboard")

    return render_template("login.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        user = request.form["username"]
        pwd = request.form["password"]

        conn = sqlite3.connect("outfits.db")
        c = conn.cursor()

        c.execute("INSERT INTO users (username, password) VALUES (?, ?)", (user, pwd))
        conn.commit()
        conn.close()

        return redirect("/")

    return render_template("register.html")


@app.route("/dashboard", methods=["GET", "POST"])
def dashboard():
    if "user_id" not in session:
        return redirect("/")

    outfit = ""

    if request.method == "POST":
        weather = request.form["weather"]

        conn = sqlite3.connect("outfits.db")
        c = conn.cursor()

        # get wardrobe items
        c.execute("SELECT item FROM wardrobe WHERE user_id=?", (session["user_id"],))
        items = [i[0] for i in c.fetchall()]

        conn.close()

        if items:
            outfit = random.choice(items) + " + Jeans 👖"
        else:
            outfit = "Add clothes to wardrobe first!"

    return render_template("dashboard.html", outfit=outfit)


@app.route("/wardrobe", methods=["GET", "POST"])
def wardrobe():
    if "user_id" not in session:
        return redirect("/")

    conn = sqlite3.connect("outfits.db")
    c = conn.cursor()

    if request.method == "POST":
        item = request.form["item"]
        typ = request.form["type"]

        c.execute("INSERT INTO wardrobe (user_id, item, type) VALUES (?, ?, ?)",
                  (session["user_id"], item, typ))
        conn.commit()

    c.execute("SELECT item, type FROM wardrobe WHERE user_id=?", (session["user_id"],))
    items = c.fetchall()

    conn.close()

    return render_template("wardrobe.html", items=items)


@app.route("/favorite", methods=["POST"])
def favorite():
    outfit = request.form["outfit"]

    conn = sqlite3.connect("outfits.db")
    c = conn.cursor()

    c.execute("INSERT INTO favorites (user_id, outfit) VALUES (?, ?)",
              (session["user_id"], outfit))
    conn.commit()
    conn.close()

    return redirect("/dashboard")


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")


if __name__ == "__main__":
    init_db()
    app.run(debug=True)
