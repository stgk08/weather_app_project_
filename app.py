import datetime
from dataclasses import dataclass
from functools import wraps

import mysql.connector
import requests
from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    session,
    g
)
from werkzeug.security import generate_password_hash, check_password_hash


app = Flask(__name__)
app.secret_key = "your_secret_key"


# ==============================
# DATAKLASSE
# ==============================

@dataclass
class WeatherData:
    lokasjon: str
    temperatur: float
    beskrivelse: str
    sist_oppdatert: datetime.datetime | None = None


# ==============================
# KONFIGURASJON
# ==============================

DB_CONFIG = {
    # "host": "10.200.14.18",
    "host": "127.0.0.1",
    "user": "stefanosgkiokas",
    "password": "Kuben2026",
    "database": "vaer_kuben_db"
}

CACHE_DURATION = datetime.timedelta(minutes=60)

CITIES = {
    "Oslo": (59.91, 10.75),
    "Bergen": (60.39, 5.32),
    "Trondheim": (63.43, 10.39),
    "Stavanger": (58.97, 5.73),
    "Tromsø": (69.65, 18.96),
    "Bodø": (67.28, 14.40),
    "Kristiansand": (58.15, 7.99),
    "Drammen": (59.74, 10.20),
    "Fredrikstad": (59.22, 10.93),
    "Ålesund": (62.47, 6.15),
    "Molde": (62.74, 7.18),
    "Haugesund": (59.41, 5.27),
    "Moss": (59.43, 10.66),
    "Porsgrunn": (59.13, 9.66),
    "Skien": (59.21, 9.60),
    "Gjøvik": (60.79, 10.69),
    "Hamar": (60.79, 11.07)
}


# ==============================
# DATABASE CONNECTION
# ==============================

def get_db():
    if "db" not in g:
        print("Kobler til database:", DB_CONFIG["host"], DB_CONFIG["database"])
        g.db = mysql.connector.connect(**DB_CONFIG)
    return g.db


@app.teardown_appcontext
def close_db(_):
    db = g.pop("db", None)

    if db and db.is_connected():
        db.close()


# ==============================
# OPPRETT TABELLER
# ==============================

def create_tables_if_not_exists():
    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS vaerdata (
            id INT AUTO_INCREMENT PRIMARY KEY,
            lokasjon VARCHAR(255) NOT NULL UNIQUE,
            temperatur DECIMAL(4,1),
            beskrivelse VARCHAR(255),
            sist_oppdatert DATETIME
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            username VARCHAR(100) NOT NULL UNIQUE,
            password_hash VARCHAR(255) NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()
    conn.close()


# ==============================
# LOGIN REQUIRED DECORATOR
# ==============================

def login_required(route_function):
    @wraps(route_function)
    def wrapper(*args, **kwargs):
        if "user_id" not in session:
            flash("Du må logge inn først.", "error")
            return redirect(url_for("login"))

        return route_function(*args, **kwargs)

    return wrapper


# ==============================
# HENT VÆR FRA MET.NO
# ==============================

def fetch_vaer(city):
    lat, lon = CITIES[city]

    url = (
        "https://api.met.no/weatherapi/locationforecast/2.0/compact"
        f"?lat={lat}&lon={lon}"
    )

    headers = {
        "User-Agent": "KubenWeatherApp/1.0 stefanos@osloskolen.no"
    }

    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()

        data = response.json()
        vaer_na = data["properties"]["timeseries"][0]["data"]

        temperatur = vaer_na["instant"]["details"]["air_temperature"]
        symbol_kode = vaer_na["next_1_hours"]["summary"]["symbol_code"]
        beskrivelse = symbol_kode.replace("_", " ").title()

        return WeatherData(
            lokasjon=city,
            temperatur=temperatur,
            beskrivelse=beskrivelse,
            sist_oppdatert=datetime.datetime.now()
        )

    except Exception as error:
        print("API ERROR:", error)
        return None


# ==============================
# DATABASE FUNKSJONER
# ==============================

def update_db(vaer: WeatherData):
    db = get_db()
    cursor = db.cursor()

    cursor.execute("""
        INSERT INTO vaerdata
            (lokasjon, temperatur, beskrivelse, sist_oppdatert)
        VALUES
            (%s, %s, %s, NOW())
        ON DUPLICATE KEY UPDATE
            temperatur = VALUES(temperatur),
            beskrivelse = VALUES(beskrivelse),
            sist_oppdatert = VALUES(sist_oppdatert)
    """, (
        vaer.lokasjon,
        vaer.temperatur,
        vaer.beskrivelse
    ))

    db.commit()


def get_weather_from_db(city):
    db = get_db()
    cursor = db.cursor(dictionary=True)

    cursor.execute("SELECT * FROM vaerdata WHERE lokasjon = %s", (city,))
    row = cursor.fetchone()

    if not row:
        return None

    return WeatherData(
        lokasjon=row["lokasjon"],
        temperatur=row["temperatur"],
        beskrivelse=row["beskrivelse"],
        sist_oppdatert=row["sist_oppdatert"]
    )

# ==============================
# ROUTES
# ==============================

@app.route("/")
@login_required
def index():
    city = request.args.get("city", "Oslo")

    if city not in CITIES:
        city = "Oslo"

    vaer_db = get_weather_from_db(city)
    cache_status = "Ingen lagret data enda"

    if vaer_db and vaer_db.sist_oppdatert:
        age = datetime.datetime.now() - vaer_db.sist_oppdatert

        if age < CACHE_DURATION:
            minutes = int(age.total_seconds() / 60)
            cache_status = f"Lagret data, {minutes} min gammel"

            return render_template(
                "index.html",
                vaer=vaer_db,
                city=city,
                cities=CITIES,
                cache_status=cache_status,
                username=session.get("username")
            )

    vaer_api = fetch_vaer(city)

    if vaer_api:
        update_db(vaer_api)
        cache_status = "Oppdatert fra Met.no"

        return render_template(
            "index.html",
            vaer=vaer_api,
            city=city,
            cities=CITIES,
            cache_status=cache_status,
            username=session.get("username")
        )

    return render_template("error.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()
        confirm_password = request.form.get("confirm_password", "").strip()

        if not username or not password:
            flash("Fyll inn brukernavn og passord.", "error")
            return redirect(url_for("register"))

        if len(username) < 3:
            flash("Brukernavnet må ha minst 3 tegn.", "error")
            return redirect(url_for("register"))

        if len(password) < 6:
            flash("Passordet må ha minst 6 tegn.", "error")
            return redirect(url_for("register"))

        if password != confirm_password:
            flash("Passordene er ikke like.", "error")
            return redirect(url_for("register"))

        db = get_db()
        cursor = db.cursor(dictionary=True)

        cursor.execute("SELECT id FROM users WHERE username = %s", (username,))
        existing_user = cursor.fetchone()

        if existing_user:
            flash("Brukernavnet er allerede tatt.", "error")
            return redirect(url_for("register"))

        password_hash = generate_password_hash(password)

        cursor.execute("""
            INSERT INTO users (username, password_hash)
            VALUES (%s, %s)
        """, (username, password_hash))

        db.commit()

        flash("Brukeren er opprettet. Du kan logge inn nå.", "success")
        return redirect(url_for("login"))

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()

        db = get_db()
        cursor = db.cursor(dictionary=True)

        cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
        user = cursor.fetchone()

        if not user or not check_password_hash(user["password_hash"], password):
            flash("Feil brukernavn eller passord.", "error")
            return redirect(url_for("login"))

        session["user_id"] = user["id"]
        session["username"] = user["username"]

        flash("Du er logget inn.", "success")
        return redirect(url_for("index"))

    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    flash("Du er logget ut.", "success")
    return redirect(url_for("login"))


@app.route("/health")
def health():
    try:
        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT 1")
        cursor.fetchone()

        return {
            "status": "OK",
            "database": "connected"
        }

    except Exception as error:
        return {
            "status": "ERROR",
            "database": "not connected",
            "error": str(error)
        }, 500


# ==============================
# START SERVER
# ==============================

if __name__ == "__main__":
    print("KJØRER DENNE FILEN:", __file__)
    create_tables_if_not_exists()

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )