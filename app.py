"""Agri Planning System — Flask backend."""
import os
import sqlite3
from datetime import datetime
from flask import Flask, render_template, request, jsonify, g
from flask_cors import CORS
import joblib
import numpy as np
import requests

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, "model", "crop_model.pkl")
DB_PATH = os.path.join(BASE_DIR, "forum.db")

# Set this env var or replace fallback with your free key from openweathermap.org
OWM_API_KEY = os.environ.get("OWM_API_KEY", "")

app = Flask(__name__)
CORS(app)

# ---------- Model ----------
_model = None
def get_model():
    global _model
    if _model is None:
        if not os.path.exists(MODEL_PATH):
            raise RuntimeError("Model not found. Run: python train_model.py")
        _model = joblib.load(MODEL_PATH)
    return _model

# ---------- Database ----------
def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(DB_PATH)
        g.db.row_factory = sqlite3.Row
    return g.db

@app.teardown_appcontext
def close_db(_exc):
    db = g.pop("db", None)
    if db is not None:
        db.close()

def init_db():
    con = sqlite3.connect(DB_PATH)
    con.execute("""
        CREATE TABLE IF NOT EXISTS posts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            author TEXT NOT NULL,
            title TEXT NOT NULL,
            content TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
    """)
    con.commit()
    con.close()

# ---------- Routes ----------
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/recommend", methods=["POST"])
def recommend():
    try:
        d = request.get_json(force=True)
        features = np.array([[
            float(d["N"]), float(d["P"]), float(d["K"]),
            float(d["temperature"]), float(d["humidity"]),
            float(d["ph"]), float(d["rainfall"])
        ]])
        model = get_model()
        probs = model.predict_proba(features)[0]
        classes = model.classes_
        top_idx = np.argsort(probs)[::-1][:3]
        recommendations = [
            {"crop": classes[i], "confidence": round(float(probs[i]) * 100, 1)}
            for i in top_idx
        ]
        # Extra context based on land/water user inputs
        land = float(d.get("land", 0) or 0)
        water = d.get("water", "medium")
        notes = []
        if land and land < 1:
            notes.append("Small plot — consider high-value crops like vegetables or herbs.")
        elif land and land > 10:
            notes.append("Large plot — staple crops (rice, maize, sugarcane) scale well.")
        if water == "low":
            notes.append("Low water availability — favor drought-tolerant crops (millet, chickpea, lentil).")
        elif water == "high":
            notes.append("High water availability — paddy rice, sugarcane, banana thrive.")

        return jsonify({"ok": True, "recommendations": recommendations, "notes": notes})
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 400

@app.route("/api/weather")
def weather():
    city = request.args.get("city", "").strip()
    if not city:
        return jsonify({"ok": False, "error": "city required"}), 400
    if not OWM_API_KEY:
        return jsonify({"ok": False, "error": "Set OWM_API_KEY environment variable (get free key at openweathermap.org)"}), 500
    try:
        url = "https://api.openweathermap.org/data/2.5/weather"
        r = requests.get(url, params={"q": city, "appid": OWM_API_KEY, "units": "metric"}, timeout=10)
        r.raise_for_status()
        w = r.json()
        return jsonify({
            "ok": True,
            "city": w.get("name"),
            "country": w.get("sys", {}).get("country"),
            "temp": w["main"]["temp"],
            "humidity": w["main"]["humidity"],
            "description": w["weather"][0]["description"],
            "icon": w["weather"][0]["icon"],
            "wind": w["wind"]["speed"],
        })
    except requests.HTTPError as e:
        return jsonify({"ok": False, "error": f"Weather API error: {e.response.status_code}"}), 400
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500

@app.route("/api/posts", methods=["GET", "POST"])
def posts():
    db = get_db()
    if request.method == "POST":
        d = request.get_json(force=True)
        author = (d.get("author") or "").strip()[:60]
        title = (d.get("title") or "").strip()[:120]
        content = (d.get("content") or "").strip()[:4000]
        if not (author and title and content):
            return jsonify({"ok": False, "error": "author, title, content required"}), 400
        db.execute(
            "INSERT INTO posts (author, title, content, created_at) VALUES (?, ?, ?, ?)",
            (author, title, content, datetime.utcnow().isoformat(timespec="seconds") + "Z")
        )
        db.commit()
        return jsonify({"ok": True})
    rows = db.execute("SELECT id, author, title, content, created_at FROM posts ORDER BY id DESC LIMIT 100").fetchall()
    return jsonify({"ok": True, "posts": [dict(r) for r in rows]})

if __name__ == "__main__":
    init_db()
    if not os.path.exists(MODEL_PATH):
        print("Training model first...")
        from train_model import train
        train()
    app.run(host="0.0.0.0", port=5000, debug=True)
