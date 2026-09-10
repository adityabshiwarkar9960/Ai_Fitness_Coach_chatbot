import math

def calculate_bmr(weight_kg, height_cm, age, gender="male"):
    """
    Calculate Basal Metabolic Rate using the Mifflin-St Jeor Equation:
    Men: BMR = (10 × weight in kg) + (6.25 × height in cm) - (5 × age in years) + 5
    Women: BMR = (10 × weight in kg) + (6.25 × height in cm) - (5 × age in years) - 161
    """
    weight_kg = float(weight_kg)
    height_cm = float(height_cm)
    age = int(age)

    base = (10 * weight_kg) + (6.25 * height_cm) - (5 * age)
    if gender.lower() == "male":
        bmr = base + 5
    else:
        bmr = base - 161
    return round(bmr, 1)

def calculate_tdee(bmr, activity_level="moderate"):
    """
    Activity Multipliers:
    - sedentary: Little or no exercise (1.2)
    - light: Exercise 1-3 times/week (1.375)
    - moderate: Exercise 4-5 times/week (1.55)
    - active: Intense exercise 6-7 times/week (1.725)
    - very_active: Very intense daily exercise/physical job (1.9)
    """
    multipliers = {
        "sedentary": 1.2,
        "light": 1.375,
        "moderate": 1.55,
        "active": 1.725,
        "very_active": 1.9
    }
    multiplier = multipliers.get(activity_level.lower(), 1.55)
    return round(bmr * multiplier)

def calculate_macros(tdee, goal="muscle_gain", dietary_pref="standard", weight_kg=70):
    """
    Calculates target calories and macro splits (Protein, Carbs, Fats).
    Goal adjustments:
    - fat_loss: TDEE - 500 kcal (~0.5 kg loss/week)
    - extreme_fat_loss: TDEE - 750 kcal
    - maintenance: TDEE
    - muscle_gain: TDEE + 300 kcal (clean lean bulk)
    - aggressive_gain: TDEE + 500 kcal
    """
    weight_kg = float(weight_kg)
    goal_cal_deltas = {
        "fat_loss": -500,
        "extreme_fat_loss": -750,
        "maintenance": 0,
        "muscle_gain": 300,
        "aggressive_gain": 500
    }
    
    target_calories = max(1200, tdee + goal_cal_deltas.get(goal, 0))

    if dietary_pref == "keto":
        # Keto: 70% Fat, 25% Protein, 5% Carbs
        protein_cals = target_calories * 0.25
        fat_cals = target_calories * 0.70
        carb_cals = target_calories * 0.05
    elif dietary_pref == "high_protein" or goal in ("muscle_gain", "fat_loss"):
        # High Protein: ~2.0 - 2.2g per kg bodyweight or 30% Protein, 45% Carbs, 25% Fat
        protein_g = min(target_calories * 0.35 / 4, weight_kg * 2.2)
        protein_cals = protein_g * 4
        fat_cals = target_calories * 0.25
        carb_cals = target_calories - protein_cals - fat_cals
    elif dietary_pref == "low_carb":
        protein_cals = target_calories * 0.35
        fat_cals = target_calories * 0.45
        carb_cals = target_calories * 0.20
    else: # Standard balanced: 30% Protein, 45% Carbs, 25% Fat
        protein_cals = target_calories * 0.25
        fat_cals = target_calories * 0.30
        carb_cals = target_calories * 0.45

    protein_grams = round(protein_cals / 4)
    carbs_grams = round(carb_cals / 4)
    fats_grams = round(fat_cals / 9)

    return {
        "target_calories": target_calories,
        "protein_g": protein_grams,
        "protein_cal": round(protein_grams * 4),
        "protein_pct": round((protein_grams * 4 / target_calories) * 100),
        "carbs_g": carbs_grams,
        "carbs_cal": round(carbs_grams * 4),
        "carbs_pct": round((carbs_grams * 4 / target_calories) * 100),
        "fats_g": fats_grams,
        "fats_cal": round(fats_grams * 9),
        "fats_pct": round((fats_grams * 9 / target_calories) * 100)
    }

def calculate_one_rep_max(weight_lifted, reps):
    """
    Epley Formula: 1RM = Weight * (1 + 0.0333 * Reps)
    Brzycki Formula: 1RM = Weight * (36 / (37 - Reps))
    Returns 1RM and percentage intensity breakdown table (95%, 90%, 85%, 80%, 75%, 70%, 65%, 60%).
    """
    weight_lifted = float(weight_lifted)
    reps = int(reps)

    if reps == 1:
        epley_1rm = weight_lifted
        brzycki_1rm = weight_lifted
    elif reps > 30:
        epley_1rm = weight_lifted * (1 + 0.0333 * 30)
        brzycki_1rm = weight_lifted * (36 / 7)
    else:
        epley_1rm = weight_lifted * (1 + 0.0333 * reps)
        brzycki_1rm = weight_lifted * (36 / (37 - reps))

    avg_1rm = round((epley_1rm + brzycki_1rm) / 2, 1)

    percentages = [
        {"pct": 100, "reps": 1, "weight": round(avg_1rm, 1)},
        {"pct": 95, "reps": 2, "weight": round(avg_1rm * 0.95, 1)},
        {"pct": 90, "reps": 3, "weight": round(avg_1rm * 0.90, 1)},
        {"pct": 85, "reps": 5, "weight": round(avg_1rm * 0.85, 1)},
        {"pct": 80, "reps": 8, "weight": round(avg_1rm * 0.80, 1)},
        {"pct": 75, "reps": 10, "weight": round(avg_1rm * 0.75, 1)},
        {"pct": 70, "reps": 12, "weight": round(avg_1rm * 0.70, 1)},
        {"pct": 65, "reps": 15, "weight": round(avg_1rm * 0.65, 1)},
    ]

    return {
        "one_rep_max": avg_1rm,
        "epley": round(epley_1rm, 1),
        "brzycki": round(brzycki_1rm, 1),
        "table": percentages
    }

def calculate_water_intake(weight_kg, activity_level="moderate"):
    """
    Base: 35ml per kg of bodyweight + activity surplus
    """
    weight_kg = float(weight_kg)
    base_ml = weight_kg * 35
    surplus_map = {
        "sedentary": 0,
        "light": 300,
        "moderate": 600,
        "active": 900,
        "very_active": 1200
    }
    total_ml = base_ml + surplus_map.get(activity_level.lower(), 500)
    liters = round(total_ml / 1000, 2)
    glasses = round(total_ml / 250)
    return {
        "liters": liters,
        "ounces": round(liters * 33.814, 1),
        "glasses": glasses
    }

def calculate_heart_rate_zones(age):
    """
    Max Heart Rate: 220 - Age (or Tanaka formula: 208 - 0.7 * age)
    Zones:
    Zone 1: Very Light / Active Recovery (50-60%)
    Zone 2: Light / Aerobic Fat Burn (60-70%)
    Zone 3: Moderate / Aerobic Endurance (70-80%)
    Zone 4: Hard / Anaerobic Threshold (80-90%)
    Zone 5: Maximum Effort / VO2 Max (90-100%)
    """
    age = int(age)
    max_hr = round(208 - (0.7 * age))
    
    zones = [
        {"zone": 1, "name": "Active Recovery", "pct": "50-60%", "min_hr": round(max_hr * 0.50), "max_hr": round(max_hr * 0.60), "benefit": "Warm-up, cooldown, active recovery, capillary density"},
        {"zone": 2, "name": "Fat Burn / Aerobic Base", "pct": "60-70%", "min_hr": round(max_hr * 0.60), "max_hr": round(max_hr * 0.70), "benefit": "Maximal fat oxidation, mitochondrial health, endurance"},
        {"zone": 3, "name": "Aerobic Endurance", "pct": "70-80%", "min_hr": round(max_hr * 0.70), "max_hr": round(max_hr * 0.80), "benefit": "Cardiovascular capacity, tempo pacing, glycogen efficiency"},
        {"zone": 4, "name": "Anaerobic Threshold", "pct": "80-90%", "min_hr": round(max_hr * 0.80), "max_hr": round(max_hr * 0.90), "benefit": "Lactate threshold, speed endurance, high-intensity capacity"},
        {"zone": 5, "name": "VO2 Max / Neuromuscular", "pct": "90-100%", "min_hr": round(max_hr * 0.90), "max_hr": max_hr, "benefit": "Peak sprint speed, maximum oxygen uptake, power"}
    ]
    return {
        "max_heart_rate": max_hr,
        "zones": zones
    }

def calculate_bmi(weight_kg, height_cm):
    """
    BMI = weight (kg) / (height (m) ^ 2)
    """
    weight_kg = float(weight_kg)
    height_m = float(height_cm) / 100.0
    bmi = round(weight_kg / (height_m * height_m), 1)

    if bmi < 18.5:
        category = "Underweight"
        badge_class = "text-info"
    elif 18.5 <= bmi < 25:
        category = "Healthy Weight"
        badge_class = "text-success"
    elif 25 <= bmi < 30:
        category = "Overweight"
        badge_class = "text-warning"
    else:
        category = "Obese"
        badge_class = "text-danger"

    return {
        "bmi": bmi,
        "category": category,
        "badge_class": badge_class
    }
