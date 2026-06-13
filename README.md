# 🌾 Agri Planning System

AI-powered crop recommendation system with live weather updates and a community forum for farmers.

Built with **HTML, CSS, JavaScript, and Python (Flask + scikit-learn)**.

## Features

- 🌱 **Crop Recommendation** — Random Forest ML model trained on soil (N, P, K, pH), climate (temperature, humidity, rainfall), water and land inputs. Returns top 3 suitable crops with confidence scores.
- ☀️ **Live Weather Updates** — Real-time weather via OpenWeatherMap API.
- 💬 **Community Forum** — SQLite-backed forum where farmers share posts.

## Project Structure

```
agri-planning-system/
├── app.py                  # Flask backend (API + routes)
├── train_model.py          # Train the ML model
├── requirements.txt
├── data/
│   └── crop_data.csv       # Training dataset
├── model/
│   └── crop_model.pkl      # Saved ML model (generated)
├── templates/
│   └── index.html          # Main page
├── static/
│   ├── css/style.css
│   └── js/app.js
└── forum.db                # SQLite forum DB (auto-created)
```

## Setup

### 1. Install Python dependencies
```bash
pip install -r requirements.txt
```

### 2. Train the ML model
```bash
python train_model.py
```
This creates `model/crop_model.pkl`.

### 3. Get a free OpenWeatherMap API key
Sign up at https://openweathermap.org/api → copy your API key.

Set it as an environment variable:

**Linux / macOS:**
```bash
export OWM_API_KEY="your_key_here"
```

**Windows (PowerShell):**
```powershell
$env:OWM_API_KEY="your_key_here"
```

### 4. Run the app
```bash
python app.py
```
Open http://localhost:5000

## Tech Stack

| Layer       | Tech                                    |
|-------------|-----------------------------------------|
| Frontend    | HTML5, CSS3, Vanilla JavaScript         |
| Backend     | Python 3, Flask, Flask-CORS             |
| ML          | scikit-learn (Random Forest), pandas    |
| Database    | SQLite (forum)                          |
| Weather     | OpenWeatherMap REST API                 |

## API Endpoints

| Method | Endpoint           | Description                       |
|--------|--------------------|-----------------------------------|
| POST   | `/api/recommend`   | Get crop recommendations          |
| GET    | `/api/weather?city=` | Get live weather for a city     |
| GET    | `/api/posts`       | List forum posts                  |
| POST   | `/api/posts`       | Create a new post                 |

## Push to GitHub

```bash
git init
git add .
git commit -m "Initial commit: Agri Planning System"
git branch -M main
git remote add origin https://github.com/<your-username>/agri-planning-system.git
git push -u origin main
```

## License
MIT
