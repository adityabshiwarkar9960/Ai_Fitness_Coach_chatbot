# 🏋️ FitCoach AI - Smart Fitness & Nutrition Assistant

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Framework-Flask%203.x-green.svg)](https://flask.palletsprojects.com/)
[![License](https://img.shields.io/badge/License-MIT-purple.svg)](LICENSE)
[![Status](https://img.shields.io/badge/Status-Active-brightgreen.svg)]()

**FitCoach AI** is a full-stack, science-backed artificial intelligence fitness trainer and sports nutrition assistant built with **Python Flask**, **SQLite**, and a **custom glassmorphism athletic frontend**.

---


## 🌟 Key Features

### 1. 🤖 AI Fitness & Nutrition Chatbot
* **Dual-Engine Architecture**: Integrated with **Google Gemini API** (`gemini-1.5-flash`) with automatic fallback to a high-precision **Offline Fitness Heuristic Engine**.
* **Markdown Formatting**: Renders tables, structured workout splits, and nutrition breakdowns seamlessly.
* **Text-to-Speech (TTS)**: Built-in voice narration option for audio coaching.
* **Prompt Quick-Chips**: One-click prompt launchers for pre-workout meals, creatine dosage, progressive overload, and form checks.

### 2. 🏋️ AI Workout Routine Generator
* **Custom Training Splits**: Supports 3-Day (Full Body), 4-Day (Upper/Lower), 5-Day (PPL + Upper/Lower), and 6-Day (Push/Pull/Legs x2).
* **Equipment Customization**: Commercial Gym, Home Dumbbells + Bench, Barbell/Rack, or Bodyweight & Resistance Bands.
* **Safety & Injury Adaptations**: Accommodates user injury limitations and biomechanical cues.
* **One-Click Library Storage & PDF/Print Export**.

### 3. 🥗 AI Diet & Nutrition Generator
* **Macronutrient Optimization**: Formulates breakfast, lunch, snacks, and dinner with exact protein, carb, and fat targets.
* **Diet Styles**: High-Protein Athlete, Standard Balanced, Vegetarian, Vegan (100% Plant-Based), Keto (Low-Carb High-Fat), and Mediterranean.
* **Hydration & Supplement Advice**: Creatine, Vitamin D3, Omega-3, and electrolyte protocols.
* **Weekly Grocery Checklist**: Auto-generated grocery list for effortless meal prepping.

### 4. 🧮 Scientific Fitness Calculators
* **BMR & TDEE**: Mifflin-St Jeor metabolic expenditure formula with 5 activity tiers.
* **Macro Splitter**: Goal-based calorie deltas (Fat Loss, Clean Bulk, Maintenance) with interactive Doughnut chart.
* **1-Rep Max (1RM)**: Powerlifting formulas (Epley & Brzycki) with complete intensity percentage table (65% to 100%).
* **Hydration Calculator**: Bodyweight and training intensity fluid requirements.
* **Heart Rate Training Zones**: Karvonen / Tanaka formula (Zones 1 through 5).

### 5. 📈 Progress Tracker & Analytics
* **Multi-Metric Logging**: Track body weight, body fat %, chest, waist, and arms.
* **Visual Trajectory**: Multi-axis Chart.js trend curves for weight and body fat % over time.
* **History Management**: View and manage historical entries.

### 6. 💾 Saved Plans Library
* Filterable repository of all saved workout splits and nutrition blueprints with detailed inspection modals.

---

## 🚀 Quick Start & Installation

### Prerequisites
* Python 3.9+
* pip

### 1. Clone or Open Workspace
```bash

(https://github.com/adityabshiwarkar9960/Ai_Fitness_Coach_chatbot.git)
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. (Optional) Configure Google Gemini API Key
Create a `.env` file or enter the key directly in the web UI under **AI Settings**:
```env
SECRET_KEY=fitcoach-secret-key-2025
GEMINI_API_KEY=your_gemini_api_key_here
PORT=5000
DEBUG=True
```
*(FitCoach AI functions completely offline even without an API key).*

### 4. Run the Application
```bash
python app.py
```
Open your browser and navigate to: **`http://127.0.0.1:5000`**

---

## 📂 Project Structure

```
Ai Fitness Chatbot/
├── app.py                     # Main Flask application and REST API routes
├── config.py                  # Environment and configuration settings
├── database.py                # SQLite database models & CRUD operations
├── calculators.py             # Scientific fitness calculations (BMR, TDEE, Macros, 1RM)
├── ai_engine.py               # Gemini AI client & offline expert heuristic engine
├── requirements.txt           # Python dependencies
├── test_app.py                # Automated test suite
├── static/
│   ├── css/
│   │   └── style.css          # Dark athletic glassmorphism design system
│   └── js/
│       ├── chat.js            # Chatbot controller & markdown rendering
│       ├── generator.js       # Workout & Diet plan builder AJAX handlers
│       ├── calculators.js     # Live fitness calculator computations & Chart.js
│       └── progress.js        # Progress tracking & line graph analytics
└── templates/
    ├── base.html              # Responsive layout with sidebar and modals
    ├── index.html             # Command center dashboard
    ├── chat.html              # Dedicated AI Coach chat room
    ├── workout_gen.html       # Workout routine generator
    ├── diet_gen.html          # Meal & nutrition plan generator
    ├── calculators.html       # Interactive fitness calculation suite
    ├── saved_plans.html       # Saved plans library
    └── progress.html          # Body progress tracker & chart
```

---

## 🧪 Testing

Run the automated test suite:
```bash
python test_app.py
```
All unit and integration tests verify calculator accuracy, SQLite CRUD methods, API payloads, and Flask routing.
#

this is my read they can not show if i upload on git
