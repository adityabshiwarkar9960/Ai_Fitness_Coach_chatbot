import os
import json
from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
from config import Config
from database import (
    init_db, get_user_profile, update_user_profile,
    get_chat_history, save_chat_message, clear_chat_history,
    save_workout_plan, get_workout_plans, get_workout_plan_by_id, delete_workout_plan,
    save_diet_plan, get_diet_plans, get_diet_plan_by_id, delete_diet_plan,
    add_progress_log, get_progress_logs, delete_progress_log,
    get_setting, set_setting
)
from calculators import (
    calculate_bmr, calculate_tdee, calculate_macros,
    calculate_one_rep_max, calculate_water_intake, calculate_heart_rate_zones, calculate_bmi
)
from ai_engine import get_chat_response, generate_workout_plan, generate_diet_plan, get_effective_api_key

app = Flask(__name__)
app.config.from_object(Config)

# Initialize database schema upon startup
with app.app_context():
    init_db()


# ==========================================
# PAGE ROUTES
# ==========================================

@app.route("/")
def index():
    profile = get_user_profile()
    workout_plans = get_workout_plans(limit=3)
    diet_plans = get_diet_plans(limit=3)
    progress_logs = get_progress_logs(limit=7)
    
    # Calculate key metrics
    bmr = calculate_bmr(profile['weight'], profile['height'], profile['age'], profile['gender'])
    tdee = calculate_tdee(bmr, profile['activity_level'])
    macros = calculate_macros(tdee, profile['fitness_goal'], profile['dietary_preference'], profile['weight'])
    bmi = calculate_bmi(profile['weight'], profile['height'])

    return render_template(
        "index.html",
        profile=profile,
        bmr=bmr,
        tdee=tdee,
        macros=macros,
        bmi=bmi,
        recent_workouts=workout_plans,
        recent_diets=diet_plans,
        progress_logs=progress_logs,
        has_api_key=bool(get_effective_api_key())
    )

@app.route("/chat")
def chat_page():
    profile = get_user_profile()
    history = get_chat_history()
    return render_template("chat.html", profile=profile, chat_history=history, has_api_key=bool(get_effective_api_key()))

@app.route("/workout-generator")
def workout_gen_page():
    profile = get_user_profile()
    return render_template("workout_gen.html", profile=profile)

@app.route("/diet-generator")
def diet_gen_page():
    profile = get_user_profile()
    # Calculate recommended calories from profile
    bmr = calculate_bmr(profile['weight'], profile['height'], profile['age'], profile['gender'])
    tdee = calculate_tdee(bmr, profile['activity_level'])
    macros = calculate_macros(tdee, profile['fitness_goal'], profile['dietary_preference'], profile['weight'])
    return render_template("diet_gen.html", profile=profile, tdee=tdee, recommended_cals=macros['target_calories'])

@app.route("/calculators")
def calculators_page():
    profile = get_user_profile()
    return render_template("calculators.html", profile=profile)

@app.route("/saved-plans")
def saved_plans_page():
    workouts = get_workout_plans(limit=50)
    diets = get_diet_plans(limit=50)
    return render_template("saved_plans.html", workouts=workouts, diets=diets)

@app.route("/progress")
def progress_page():
    profile = get_user_profile()
    logs = get_progress_logs(limit=100)
    return render_template("progress.html", profile=profile, logs=logs)


# ==========================================
# REST API ENDPOINTS
# ==========================================

# --- Chat API ---
@app.route("/api/chat", methods=["POST"])
def api_chat():
    data = request.get_json() or {}
    user_msg = data.get("message", "").strip()
    session_id = data.get("session_id", "default")

    if not user_msg:
        return jsonify({"error": "Message cannot be empty"}), 400

    profile = get_user_profile()
    
    # Save user message to database
    save_chat_message("user", user_msg, session_id=session_id)
    
    # Fetch recent history context
    history = get_chat_history(session_id=session_id, limit=10)
    
    # Generate AI Coach response
    ai_response = get_chat_response(user_msg, history=history, user_profile=profile)
    
    # Save assistant message to database
    save_chat_message("assistant", ai_response, session_id=session_id)

    return jsonify({
        "success": True,
        "reply": ai_response
    })

@app.route("/api/chat/history", methods=["GET"])
def api_chat_history():
    session_id = request.args.get("session_id", "default")
    history = get_chat_history(session_id=session_id)
    return jsonify({"success": True, "history": history})

@app.route("/api/chat/clear", methods=["POST"])
def api_chat_clear():
    data = request.get_json() or {}
    session_id = data.get("session_id", "default")
    clear_chat_history(session_id=session_id)
    return jsonify({"success": True, "message": "Chat history cleared successfully"})


# --- Workout Generator API ---
@app.route("/api/generate-workout", methods=["POST"])
def api_generate_workout():
    data = request.get_json() or {}
    goal = data.get("goal", "muscle_gain")
    experience_level = data.get("experience_level", "intermediate")
    days_per_week = int(data.get("days_per_week", 4))
    equipment = data.get("equipment", "Full Gym (Barbell, Dumbbells, Cables, Machines)")
    injury_notes = data.get("injury_notes", "None")

    profile = get_user_profile()
    plan_result = generate_workout_plan(goal, experience_level, days_per_week, equipment, injury_notes, user_profile=profile)

    return jsonify({
        "success": True,
        "plan": plan_result
    })

@app.route("/api/save-workout", methods=["POST"])
def api_save_workout():
    data = request.get_json() or {}
    title = data.get("title", "Custom Workout Routine")
    goal = data.get("goal", "General Fitness")
    experience_level = data.get("experience_level", "Intermediate")
    days_per_week = int(data.get("days_per_week", 4))
    equipment = data.get("equipment", "Standard")
    plan_content = data.get("plan_content", "")
    structured_data = data.get("structured_data", None)

    plan_id = save_workout_plan(title, goal, experience_level, days_per_week, equipment, plan_content, structured_data)
    return jsonify({"success": True, "plan_id": plan_id, "message": "Workout plan saved to your library!"})


# --- Diet Generator API ---
@app.route("/api/generate-diet", methods=["POST"])
def api_generate_diet():
    data = request.get_json() or {}
    goal = data.get("goal", "muscle_gain")
    diet_type = data.get("diet_type", "standard")
    target_calories = int(data.get("target_calories", 2200))
    allergies = data.get("allergies", "None")
    meals_per_day = int(data.get("meals_per_day", 4))

    profile = get_user_profile()
    plan_result = generate_diet_plan(goal, diet_type, target_calories, allergies, meals_per_day, user_profile=profile)

    return jsonify({
        "success": True,
        "plan": plan_result
    })

@app.route("/api/save-diet", methods=["POST"])
def api_save_diet():
    data = request.get_json() or {}
    title = data.get("title", "Custom Meal Plan")
    goal = data.get("goal", "General Health")
    diet_type = data.get("diet_type", "Standard")
    target_calories = int(data.get("target_calories", 2000))
    protein_g = int(data.get("protein_g", 150))
    carbs_g = int(data.get("carbs_g", 200))
    fats_g = int(data.get("fats_g", 65))
    plan_content = data.get("plan_content", "")
    structured_data = data.get("structured_data", None)

    plan_id = save_diet_plan(title, goal, diet_type, target_calories, protein_g, carbs_g, fats_g, plan_content, structured_data)
    return jsonify({"success": True, "plan_id": plan_id, "message": "Meal plan saved to your library!"})


# --- Plan Management API ---
@app.route("/api/plans/workout/<int:plan_id>", methods=["GET", "DELETE"])
def api_workout_plan(plan_id):
    if request.method == "DELETE":
        delete_workout_plan(plan_id)
        return jsonify({"success": True, "message": "Workout plan removed"})
    plan = get_workout_plan_by_id(plan_id)
    if not plan:
        return jsonify({"error": "Plan not found"}), 404
    return jsonify({"success": True, "plan": plan})

@app.route("/api/plans/diet/<int:plan_id>", methods=["GET", "DELETE"])
def api_diet_plan(plan_id):
    if request.method == "DELETE":
        delete_diet_plan(plan_id)
        return jsonify({"success": True, "message": "Diet plan removed"})
    plan = get_diet_plan_by_id(plan_id)
    if not plan:
        return jsonify({"error": "Plan not found"}), 404
    return jsonify({"success": True, "plan": plan})


# --- Profile API ---
@app.route("/api/profile", methods=["GET", "POST"])
def api_profile():
    if request.method == "POST":
        data = request.get_json() or {}
        updated = update_user_profile(data)
        return jsonify({"success": True, "profile": updated, "message": "Profile updated successfully!"})
    profile = get_user_profile()
    return jsonify({"success": True, "profile": profile})


# --- Progress Tracking API ---
@app.route("/api/progress", methods=["GET", "POST"])
def api_progress():
    if request.method == "POST":
        data = request.get_json() or {}
        log_date = data.get("log_date")
        weight = float(data.get("weight", 0))
        body_fat = float(data.get("body_fat")) if data.get("body_fat") else None
        chest = float(data.get("chest")) if data.get("chest") else None
        waist = float(data.get("waist")) if data.get("waist") else None
        arms = float(data.get("arms")) if data.get("arms") else None
        notes = data.get("notes", "")

        if not log_date or weight <= 0:
            return jsonify({"error": "Valid date and weight are required"}), 400

        log_id = add_progress_log(log_date, weight, body_fat, chest, waist, arms, notes)
        return jsonify({"success": True, "log_id": log_id, "message": "Progress logged successfully!"})

    logs = get_progress_logs()
    return jsonify({"success": True, "logs": logs})

@app.route("/api/progress/<int:log_id>", methods=["DELETE"])
def api_delete_progress(log_id):
    delete_progress_log(log_id)
    return jsonify({"success": True, "message": "Progress entry deleted"})


# --- Scientific Calculators API ---
@app.route("/api/calculate", methods=["POST"])
def api_calculate():
    data = request.get_json() or {}
    calc_type = data.get("type")

    if calc_type == "bmr_tdee":
        weight = float(data.get("weight", 70))
        height = float(data.get("height", 175))
        age = int(data.get("age", 25))
        gender = data.get("gender", "male")
        activity = data.get("activity_level", "moderate")
        goal = data.get("goal", "muscle_gain")
        dietary = data.get("dietary_preference", "standard")

        bmr = calculate_bmr(weight, height, age, gender)
        tdee = calculate_tdee(bmr, activity)
        macros = calculate_macros(tdee, goal, dietary, weight)
        bmi = calculate_bmi(weight, height)

        return jsonify({
            "success": True,
            "bmr": bmr,
            "tdee": tdee,
            "macros": macros,
            "bmi": bmi
        })

    elif calc_type == "one_rep_max":
        weight = float(data.get("weight", 100))
        reps = int(data.get("reps", 5))
        res = calculate_one_rep_max(weight, reps)
        return jsonify({"success": True, "result": res})

    elif calc_type == "water":
        weight = float(data.get("weight", 70))
        activity = data.get("activity_level", "moderate")
        res = calculate_water_intake(weight, activity)
        return jsonify({"success": True, "result": res})

    elif calc_type == "heart_rate":
        age = int(data.get("age", 25))
        res = calculate_heart_rate_zones(age)
        return jsonify({"success": True, "result": res})

    return jsonify({"error": "Unknown calculation type"}), 400


# --- App Settings API ---
@app.route("/api/settings", methods=["GET", "POST"])
def api_settings():
    if request.method == "POST":
        data = request.get_json() or {}
        gemini_key = data.get("gemini_api_key", "").strip()
        set_setting("gemini_api_key", gemini_key)
        return jsonify({"success": True, "message": "Settings saved successfully!"})

    current_key = get_effective_api_key()
    # Mask API key for UI security
    masked_key = (current_key[:4] + "..." + current_key[-4:]) if len(current_key) > 8 else ("Configured" if current_key else "")
    return jsonify({
        "success": True,
        "has_key": bool(current_key),
        "masked_key": masked_key
    })


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=Config.DEBUG)
