import os
import json
import random
import requests
from config import Config
from database import get_setting

SYSTEM_PROMPT = """You are FitCoach AI, an elite personal trainer, CSCS-certified strength & conditioning specialist, and registered sports nutritionist.
Your mission is to provide science-based, highly practical, motivating, and personalized health, fitness, and nutrition coaching.

Core Guidelines:
1. Tone: Motivational, professional, clear, evidence-based, and encouraging.
2. Safety First: Always provide proper form cues and recommend consulting a physician when dealing with severe injuries or medical conditions.
3. Structure & Clarity: Use GitHub markdown with clear headings, bullet points, bold key takeaways, and tables when listing routines or meal plans.
4. Actionable Advice: Give concrete numbers (sets, reps, rest intervals, grams of protein, water targets) rather than vague suggestions.
5. Empathy: Acknowledge user constraints (time, equipment, dietary restrictions) and offer tailored adaptations.
"""

def get_effective_api_key():
    """Retrieve Gemini API key from database setting, environment, or Config."""
    db_key = get_setting("gemini_api_key")
    if db_key and db_key.strip():
        return db_key.strip()
    if Config.GEMINI_API_KEY and Config.GEMINI_API_KEY.strip():
        return Config.GEMINI_API_KEY.strip()
    return os.environ.get("GEMINI_API_KEY", "").strip()

def call_gemini_api(prompt, system_instruction=SYSTEM_PROMPT, history=None):
    """
    Call Google Gemini REST API.
    """
    api_key = get_effective_api_key()
    if not api_key:
        return None  # Will trigger offline expert fallback

    # Try gemini-1.5-flash or gemini-2.5-flash endpoint
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
    
    contents = []
    
    # Add history if provided
    if history:
        for msg in history[-8:]: # keep recent context
            role = "user" if msg.get("role") == "user" else "model"
            contents.append({
                "role": role,
                "parts": [{"text": msg.get("content", "")}]
            })
            
    contents.append({
        "role": "user",
        "parts": [{"text": prompt}]
    })

    payload = {
        "contents": contents,
        "systemInstruction": {
            "parts": [{"text": system_instruction}]
        },
        "generationConfig": {
            "temperature": 0.7,
            "topP": 0.95,
            "maxOutputTokens": 2048
        }
    }

    try:
        response = requests.post(
            url,
            headers={"Content-Type": "application/json"},
            json=payload,
            timeout=15
        )
        if response.status_code == 200:
            data = response.json()
            candidates = data.get("candidates", [])
            if candidates and "content" in candidates[0]:
                parts = candidates[0]["content"].get("parts", [])
                if parts and "text" in parts[0]:
                    return parts[0]["text"]
        print(f"Gemini API returned code {response.status_code}: {response.text[:200]}")
    except Exception as e:
        print(f"Gemini API connection error: {e}")
    
    return None


# ==========================================
# OFFLINE EXPERT FITNESS HEURISTIC ENGINE
# ==========================================

def get_chat_response(user_message, history=None, user_profile=None):
    """
    Generate response using Gemini API if key is present; otherwise use expert fallback.
    """
    prompt_with_context = user_message
    if user_profile:
        context_str = f"[User Profile: {user_profile.get('name', 'Athlete')}, {user_profile.get('age', 25)}yo {user_profile.get('gender', 'male')}, Weight: {user_profile.get('weight', 70)}kg, Height: {user_profile.get('height', 175)}cm, Goal: {user_profile.get('fitness_goal', 'muscle_gain')}, Level: {user_profile.get('activity_level', 'moderate')}]\n\nUser Question: {user_message}"
        prompt_with_context = context_str

    ai_reply = call_gemini_api(prompt_with_context, history=history)
    if ai_reply:
        return ai_reply

    # Offline Expert Heuristic Engine
    return offline_expert_chat_response(user_message, user_profile)


def offline_expert_chat_response(message, profile=None):
    """
    Rich, offline, rule-based expert conversational responses.
    """
    msg = message.lower()
    name = profile.get("name", "Champion") if profile else "Champion"
    weight = profile.get("weight", 70) if profile else 70
    goal = profile.get("fitness_goal", "muscle_gain") if profile else "muscle_gain"

    # 1. Protein Questions
    if any(k in msg for k in ["protein", "how much protein", "protein intake", "powder"]):
        opt_min = round(weight * 1.6, 1)
        opt_max = round(weight * 2.2, 1)
        return f"""### 🥩 Optimal Protein Strategy for {name}

For your target goal (**{goal.replace('_', ' ').title()}**), scientific evidence (ISSN & Morton et al.) recommends:

* **Daily Target:** **{opt_min}g – {opt_max}g of protein per day** (approx. 1.6 to 2.2g per kg of body weight).
* **Per Meal Distribution:** 25g – 40g of high-quality protein per meal across 3–5 meals to optimize Muscle Protein Synthesis (MPS).
* **Leucine Threshold:** Ensure each meal has ~2.5g–3g of Leucine (found in eggs, whey, chicken, fish, soy, and dairy).

**Top Protein Sources:**
| Category | Top Food Sources | Typical Serving |
| :--- | :--- | :--- |
| **Lean Poultry / Meat** | Chicken breast, Turkey breast, 95% Lean Beef | ~30g protein per 100g |
| **Seafood** | Salmon, Tuna, Tilapia, Shrimp | ~25-30g protein per 100g |
| **Vegetarian / Dairy** | Greek Yogurt (0%), Cottage Cheese, Eggs & Egg whites | ~15-20g per cup / 6g per egg |
| **Plant-Based** | Tofu, Tempeh, Seitan, Edamame, Lentils | ~15-25g per serving |
| **Supplements** | Whey Isolate or Pea/Rice Blend | ~24-27g per scoop |

> 💡 **FitCoach Tip:** Protein timing is secondary to total daily intake. Focus on hitting your daily target first!"""

    # 2. Creatine
    elif any(k in msg for k in ["creatine", "creatine monohydrate"]):
        return """### ⚡ The Ultimate Creatine Monohydrate Guide

Creatine is the most thoroughly researched and effective sports supplement in existence for increasing strength, power output, and lean muscle mass.

#### How to Take It:
1. **Maintenance Dose (Recommended):** Take **3 to 5 grams daily** consistently at any time of day (post-workout with carbs/protein is optimal).
2. **Optional Loading Phase:** 20 grams/day (divided into 4x5g doses) for 5-7 days to saturate muscle stores faster. *Not mandatory—taking 5g daily reaches full saturation in ~3 weeks without GI distress.*
3. **Hydration:** Drink an extra 500ml–1000ml of water daily, as creatine pulls intracellular water into muscle cells (increasing cell volumization).

> ⚠️ **Key Takeaway:** You do **not** need to cycle creatine off. Creatine Monohydrate is safe, inexpensive, and proven."""

    # 3. Pre-workout / Nutrition timing
    elif any(k in msg for k in ["pre workout", "pre-workout", "eat before", "what to eat before"]):
        return """### 🍌 Pre-Workout Fueling Protocol

To maximize training intensity, pump, and endurance, follow this timing window:

#### 🕒 2 to 3 Hours Before Training (Full Meal):
* **Complex Carbohydrates:** Oats, brown rice, sweet potatoes, or whole-grain toast.
* **Lean Protein:** Chicken, turkey, egg whites, or tofu (25-30g).
* **Low Fat & Moderate Fiber:** Keep fats low to avoid sluggish digestion.

#### ⚡ 30 to 45 Minutes Before Training (Quick Fuel):
* **Fast-Digesting Glycogen Boost:** 1 banana, 2 rice cakes with 1 tbsp honey, or a handful of dates.
* **Electrolytes & Hydration:** 400-500ml of water with a pinch of Himalayan salt.
* **Caffeine (Optional):** 100-200mg coffee or pre-workout for central nervous system arousal.

> 🚫 **Avoid:** Heavy greasy foods or high-fiber beans right before working out to prevent cramps and reflux."""

    # 4. Cardio vs Weights
    elif any(k in msg for k in ["cardio before or after", "cardio", "weights or cardio"]):
        return """### 🏃‍♂️ Cardio Before or After Weights?

The verdict depends on your primary fitness objective:

* **If Goal is Muscle Growth & Strength:**
  👉 **Lift First, Cardio After (or on separate days).**
  Lifting requires maximum glycogen, ATP-CP stores, and neurological focus. Doing hard cardio first induces neuromuscular fatigue, reducing the weight and volume you can move.

* **If Goal is General Cardiovascular Endurance / Marathon Training:**
  👉 **Run/Cardio First, Weights Second.**

* **Warm-up Note:** A light 5-minute dynamic warm-up (e.g. brisk incline walk, jumping jacks, mobility) *before* lifting is perfect to elevate body temperature without causing fatigue."""

    # 5. Progressive Overload
    elif any(k in msg for k in ["progressive overload", "plateau", "stuck", "how to progress"]):
        return """### 📈 The 5 Methods of Progressive Overload

Progressive overload is the fundamental mechanical stimulus that forces muscles to adapt and grow. You can overload in 5 distinct ways:

1. **Increase Resistance (Weight):** Add 1.25kg - 2.5kg to the bar when you hit the top of your rep range.
2. **Increase Volume (Reps/Sets):** Progress from 8 reps $\\rightarrow$ 9 reps $\\rightarrow$ 10 reps with the exact same weight.
3. **Improve Execution & Technique:** Slower eccentric tempo (3-sec lowering), fuller range of motion, and paused contractions.
4. **Decrease Rest Periods:** Perform the same workload in less time (e.g., resting 90s instead of 120s).
5. **Increase Frequency:** Train the muscle group 2x per week instead of 1x to double the growth stimulus.

> 📋 **FitCoach Rule:** Log your weights and reps every single session. What gets measured gets improved!"""

    # 6. Fat loss / Weight loss tips
    elif any(k in msg for k in ["fat loss", "lose weight", "cut", "cutting", "calorie deficit"]):
        return f"""### 🔥 Science-Backed Fat Loss Blueprint

To drop body fat while preserving lean muscle mass:

1. **Calculate a Moderate Deficit:** Aim for **300 to 500 calories below maintenance (TDEE)**. This yields a steady, sustainable fat loss of ~0.5kg (1 lb) per week without metabolic slowdown.
2. **Keep Protein High:** Aim for **1.8g–2.2g per kg of bodyweight**. Protein has the highest Thermic Effect of Food (TEF) and safeguards muscle tissue.
3. **Maintain Strength Training Intensity:** Keep lifting heavy in the 6–12 rep range to signal to your body that muscle tissue is essential.
4. **Boost NEAT (Non-Exercise Activity Thermogenesis):** Hit 8,000 to 10,000 daily steps. Walking burns pure fat without spiking appetite or interfering with recovery.
5. **Sleep 7-9 Hours:** Sleep deprivation increases ghrelin (hunger hormone) and reduces insulin sensitivity."""

    # 7. Default Encouraging & Knowledgeable Response
    else:
        return f"""### 🚀 FitCoach AI Training & Nutrition Advice

Hello {name}! As your dedicated coach, here are the key pillars for your **{goal.replace('_', ' ').title()}** journey:

1. **Consistent Resistance Training:** Aim for 3 to 5 structured sessions per week focusing on compound movements (Squat, Deadlift, Bench, Rows, Overhead Press).
2. **Nutritional Precision:** Fuel your body with adequate protein ({round(weight * 1.8)}g target), quality carbohydrates for workout performance, and essential healthy fats for hormone regulation.
3. **Progressive Overload:** Always aim to beat your previous workout by 1 extra rep or slightly more weight with strict form.
4. **Hydration & Recovery:** Drink at least 3-4 liters of water daily and prioritize 7-9 hours of restorative sleep.

👉 *You can ask me specific questions like "What to eat post-workout?", "How do I fix my squat depth?", "Generate a 4-day workout plan", or use the generators in the sidebar!*"""


# ==========================================
# WORKOUT PLAN GENERATOR
# ==========================================

def generate_workout_plan(goal, experience_level, days_per_week, equipment, injury_notes="None", user_profile=None):
    """
    Generate workout plan via Gemini API or expert offline template engine.
    """
    prompt = f"""Generate a comprehensive, professional {days_per_week}-day workout routine.
Parameters:
- Goal: {goal}
- Experience Level: {experience_level}
- Days Per Week: {days_per_week}
- Available Equipment: {equipment}
- Limitations/Injuries: {injury_notes}

Format with:
1. Executive Summary & Strategy
2. Daily Workout Split (Day 1, Day 2, etc. with Warm-up, Table of Exercises [Exercise Name, Sets, Reps, Rest, Key Form Cue], and Cooldown)
3. Progressive Overload Guidelines
4. Recovery & Deload Recommendations
Use Markdown formatting."""

    ai_plan = call_gemini_api(prompt)
    if ai_plan:
        return {
            "title": f"{experience_level.title()} {goal.replace('_', ' ').title()} ({days_per_week}-Day Split)",
            "content": ai_plan,
            "structured": build_structured_workout_data(goal, experience_level, days_per_week, equipment)
        }

    # Offline high-quality generator
    return generate_offline_workout_plan(goal, experience_level, days_per_week, equipment, injury_notes)


def generate_offline_workout_plan(goal, experience_level, days_per_week, equipment, injury_notes="None"):
    days = int(days_per_week)
    title = f"{experience_level.title()} {goal.replace('_', ' ').title()} ({days}-Day Split)"
    
    # Split structure determination
    if days == 3:
        split_name = "Full Body Split (A / B / C)"
        schedule = [
            ("Day 1: Full Body Power (A)", [
                ("Barbell Back Squats (or Goblet Squats)", "3-4", "6-8", "2-3 min", "Keep chest proud, drive through mid-foot"),
                ("Flat Barbell / DB Bench Press", "3-4", "8-10", "2 min", "Retract scapula, 45-degree elbow tuck"),
                ("Barbell Bent-Over Rows", "3", "8-10", "90 sec", "Hinge at hips, pull to lower ribcage"),
                ("Romanian Deadlifts (RDLs)", "3", "10-12", "90 sec", "Soft knees, feel deep hamstring stretch"),
                ("Standing Overhead DB Press", "3", "10-12", "90 sec", "Brace core, full lockout overhead"),
                ("Hanging Leg Raises / Plank", "3", "12-15 / 60s", "60 sec", "Tilt pelvis upward, avoid swinging")
            ]),
            ("Day 2: Full Body Hypertrophy (B)", [
                ("Conventional Deadlifts / DB Deadlifts", "3", "5", "3 min", "Neutral spine, engage lats before pull"),
                ("Incline Dumbbell Press", "3-4", "10-12", "90 sec", "30-degree incline, full stretch at bottom"),
                ("Lat Pulldowns or Pull-Ups", "3-4", "8-12", "90 sec", "Drive elbows straight down to hips"),
                ("Bulgarian Split Squats", "3 per leg", "10-12", "90 sec", "Slight forward torso lean for glute bias"),
                ("Dumbbell Lateral Raises", "4", "12-15", "60 sec", "Lead with elbows, controlled 2-sec negative"),
                ("Incline DB Bicep Curls superset Tricep Dips", "3", "12-15", "60 sec", "Full range of motion, squeeze peak")
            ]),
            ("Day 3: Full Body Conditioning & Strength (C)", [
                ("Leg Press / Front Squats", "3-4", "10-12", "2 min", "Deep knee flexion, controlled eccentric"),
                ("Seated Cable / Chest-Supported DB Rows", "3-4", "10-12", "90 sec", "Squeeze shoulder blades together"),
                ("Dumbbell Overhead Shoulder Press", "3", "8-10", "90 sec", "Full extension, keep ribcage down"),
                ("Hamstring Lying / Seated Leg Curls", "3", "12-15", "60 sec", "Control the return to starting position"),
                ("Dips / Cable Tricep Pushdowns", "3", "10-12", "60 sec", "Lock out triceps with control"),
                ("Cable Woodchoppers / Ab Wheel Rollouts", "3", "12-15", "60 sec", "Engage core bracing throughout")
            ])
        ]
    elif days == 4:
        split_name = "Upper / Lower Split (4 Days)"
        schedule = [
            ("Day 1: Upper Body Power", [
                ("Barbell Bench Press", "4", "6-8", "2-3 min", "Drive through legs, tight arch"),
                ("Barbell Bent-Over Row", "4", "6-8", "2 min", "Explosive pull, controlled lower"),
                ("Overhead Barbell / DB Press", "3", "8-10", "2 min", "Brace glutes and abs"),
                ("Weighted Pull-ups / Lat Pulldown", "3", "8-10", "90 sec", "Pause 1 sec at bottom contraction"),
                ("Incline Dumbbell Bicep Curls", "3", "10-12", "60 sec", "Keep elbows pinned back"),
                ("Overhead Cable Tricep Extension", "3", "10-12", "60 sec", "Deep long-head tricep stretch")
            ]),
            ("Day 2: Lower Body Power", [
                ("Barbell Back Squat", "4", "6-8", "3 min", "Hit parallel or below, knees in line with toes"),
                ("Romanian Deadlifts (RDLs)", "3-4", "8-10", "2 min", "Push hips back to the wall behind you"),
                ("Leg Press", "3", "10-12", "90 sec", "Do not lock out knees aggressively"),
                ("Standing Calf Raises", "4", "12-15", "60 sec", "2-second pause at bottom stretch"),
                ("Hanging Knee / Leg Raises", "3", "12-15", "60 sec", "Strict form, no momentum")
            ]),
            ("Day 3: Upper Body Hypertrophy", [
                ("Incline Dumbbell Press", "4", "10-12", "90 sec", "Squeeze upper chest at top"),
                ("Seated Cable Row (Close Grip)", "4", "10-12", "90 sec", "Pull toward belly button"),
                ("Dumbbell Lateral Raises", "4", "12-15", "60 sec", "Slight forward lean, raise in scapular plane"),
                ("Chest Flyes (Cable or DB)", "3", "12-15", "60 sec", "Focus on maximum stretch"),
                ("Barbell EZ-Bar Skull Crushers", "3", "10-12", "60 sec", "Keep elbows stable"),
                ("Hammer Curls", "3", "10-12", "60 sec", "Target brachialis and forearms")
            ]),
            ("Day 4: Lower Body Hypertrophy", [
                ("Conventional Deadlift / Trap Bar Deadlift", "3", "5-8", "3 min", "Pull the slack out of the bar"),
                ("Bulgarian Split Squats", "3 per leg", "10-12", "90 sec", "Dumbbells in hand, steady balance"),
                ("Lying Leg Curls", "3", "12-15", "60 sec", "Toe point dorsiflexed"),
                ("Leg Extensions", "3", "12-15", "60 sec", "Hold peak contraction for 1 sec"),
                ("Seated Calf Raises", "4", "15-20", "45 sec", "Targets soleus muscle"),
                ("Cable Ab Crunches", "3", "15-20", "60 sec", "Flex spine downward")
            ])
        ]
    else: # 5 or 6 days - Push / Pull / Legs
        split_name = "Push / Pull / Legs (PPL) Split"
        schedule = [
            ("Day 1: Push (Chest, Shoulders, Triceps)", [
                ("Barbell Flat Bench Press", "4", "6-8", "2-3 min", "Solid leg drive, controlled descent"),
                ("Incline Dumbbell Press", "3", "8-10", "2 min", "Deep stretch at bottom"),
                ("Standing Overhead DB / Military Press", "3", "8-10", "90 sec", "Neutral grip or standard"),
                ("Cable Lateral Raises", "4", "12-15", "60 sec", "Constant tension on lateral delt"),
                ("Cable Rope Tricep Pushdowns", "3", "10-12", "60 sec", "Flare rope outward at bottom"),
                ("Incline DB Overhead Tricep Extension", "3", "12-15", "60 sec", "Long head tricep emphasis")
            ]),
            ("Day 2: Pull (Back, Rear Delts, Biceps)", [
                ("Barbell Deadlift or Rack Pulls", "3", "5", "3 min", "Keep bar close to shins"),
                ("Chest-Supported T-Bar / DB Rows", "4", "8-10", "2 min", "Full upper back contraction"),
                ("Neutral-Grip Lat Pulldown / Pull-ups", "3", "8-12", "90 sec", "Drive elbows to ribs"),
                ("Face Pulls (Cable Rope)", "4", "15-20", "60 sec", "Pull toward forehead, external rotation"),
                ("Incline Dumbbell Bicep Curls", "3", "10-12", "60 sec", "Supinate wrist at top"),
                ("Cross-Body Hammer Curls", "3", "10-12", "60 sec", "Build forearm and brachialis thickness")
            ]),
            ("Day 3: Legs & Abs (Quads, Hamstrings, Calves)", [
                ("Barbell Back Squat", "4", "6-8", "3 min", "Control descent, power up"),
                ("Romanian Deadlifts (RDL)", "3", "8-10", "2 min", "Hips high and back, flat back"),
                ("Leg Press", "3", "10-12", "90 sec", "Feet shoulder-width on platform"),
                ("Seated Hamstring Curls", "3", "12-15", "60 sec", "Lock upper thighs down"),
                ("Standing Calf Raises", "4", "12-15", "60 sec", "Full range of motion"),
                ("Hanging Leg Raises", "3", "12-15", "60 sec", "Control swinging motion")
            ]),
            ("Day 4: Push (Hypertrophy)", [
                ("Incline Barbell Bench Press", "4", "8-10", "2 min", "Upper chest focus"),
                ("Dumbbell Flat Bench Press", "3", "10-12", "90 sec", "Deep stretch and squeeze"),
                ("Seated DB Shoulder Press", "3", "10-12", "90 sec", "Keep elbows slightly in front"),
                ("Dumbbell Lateral Raises", "4", "15", "60 sec", "Light weight, strict form"),
                ("Dips (Chest/Tricep bias)", "3", "10-12", "60 sec", "Slight forward lean"),
                ("Cable Tricep Kickbacks / Pushdowns", "3", "12-15", "60 sec", "Squeeze triceps at lockout")
            ]),
            ("Day 5: Pull (Hypertrophy)", [
                ("Barbell Bent-Over Row", "4", "8-10", "2 min", "Overhand or underhand grip"),
                ("Single-Arm DB Row", "3 per arm", "10-12", "90 sec", "Pull dumbbell to hip pocket"),
                ("Wide Grip Lat Pulldown", "3", "10-12", "90 sec", "Focus on lat width"),
                ("Rear Delt Flyes (Machine or DB)", "4", "15-20", "60 sec", "Focus on rear deltoids"),
                ("EZ-Bar Preacher Curls", "3", "10-12", "60 sec", "Isolate short head of bicep"),
                ("Reverse Grip Forearm Curls", "3", "15", "45 sec", "Forearm density")
            ])
        ]

    # Build Markdown
    md = f"""## 🏋️ {title}

**Split Strategy:** {split_name}  
**Focus Goal:** {goal.replace('_', ' ').title()}  
**Experience Level:** {experience_level.title()}  
**Equipment Available:** {equipment}  
**Limitations / Notes:** {injury_notes}

---

### 📋 Warm-up Routine (Perform Before Every Session)
* 5 min brisk walk / incline treadmill / stationary bike
* Dynamic joint circles (Arm circles, Leg swings, Hip openers, World's Greatest Stretch)
* 2-3 progressive warm-up sets of the first compound movement (empty bar $\\rightarrow$ 50% $\\rightarrow$ 75% working weight)

---
"""

    structured_data = []

    for day_title, exercises in schedule:
        md += f"\n### {day_title}\n\n"
        md += "| Exercise | Sets | Reps | Rest | Key Coaching Cue |\n"
        md += "| :--- | :--- | :--- | :--- | :--- |\n"
        
        day_struct = {"day": day_title, "exercises": []}
        for ex, sets, reps, rest, cue in exercises:
            md += f"| **{ex}** | {sets} | {reps} | {rest} | {cue} |\n"
            day_struct["exercises"].append({
                "name": ex, "sets": sets, "reps": reps, "rest": rest, "cue": cue
            })
        structured_data.append(day_struct)

    md += """
---

### 📈 Progressive Overload & Execution Rules
1. **The Double Progression Method:** When you hit the top of the rep range for all prescribed sets with solid form, increase the load by 2-5% next session.
2. **RPE (Rate of Perceived Exertion):** Keep compound lifts at RPE 7-8 (2 reps left in reserve) and isolation movements at RPE 9-10 (1 or 0 reps in reserve).
3. **Deload Week:** Every 6-8 weeks of consistent training, drop volume by 40% to allow joints, tendons, and central nervous system to regenerate fully.
"""

    return {
        "title": title,
        "content": md,
        "structured": structured_data
    }


def build_structured_workout_data(goal, level, days, equipment):
    # Fallback structure for API-generated plans
    return [{"day": f"Day {i+1}", "exercises": [{"name": f"Compound Movement {i+1}", "sets": "3-4", "reps": "8-12", "rest": "90s", "cue": "Focus on controlled form"}]} for i in range(int(days))]


# ==========================================
# DIET & NUTRITION PLAN GENERATOR
# ==========================================

def generate_diet_plan(goal, diet_type, target_calories, allergies="None", meals_per_day=4, user_profile=None):
    """
    Generate customized nutrition plan via Gemini API or expert offline template engine.
    """
    prompt = f"""Generate a detailed, delicious, science-backed daily nutrition & meal plan.
Parameters:
- Goal: {goal}
- Diet Type: {diet_type}
- Daily Calorie Target: {target_calories} kcal
- Allergies / Exclusions: {allergies}
- Meals Per Day: {meals_per_day}

Format with:
1. Calorie & Macro Target Breakdown (Calories, Protein, Carbs, Fats)
2. Detailed Daily Meal Schedule (Meal 1, Meal 2, Meal 3, Snack with exact food items, portion sizes, calories & macros per meal)
3. Smart Hydration & Supplement Protocol
4. Weekly Grocery Shopping Checklist
Use Markdown formatting."""

    ai_plan = call_gemini_api(prompt)
    if ai_plan:
        return {
            "title": f"{diet_type.title()} Meal Plan ({target_calories} kcal - {goal.replace('_', ' ').title()})",
            "content": ai_plan,
            "target_calories": int(target_calories)
        }

    # Offline high-quality generator
    return generate_offline_diet_plan(goal, diet_type, target_calories, allergies, meals_per_day)


def generate_offline_diet_plan(goal, diet_type, target_calories, allergies="None", meals_per_day=4):
    cals = int(target_calories)
    
    # Calculate macro breakdown
    if diet_type == "keto":
        protein_g = round((cals * 0.25) / 4)
        carbs_g = round((cals * 0.05) / 4)
        fats_g = round((cals * 0.70) / 9)
    elif diet_type in ["vegan", "vegetarian"]:
        protein_g = round((cals * 0.28) / 4)
        carbs_g = round((cals * 0.48) / 4)
        fats_g = round((cals * 0.24) / 9)
    else: # standard / high protein
        protein_g = round((cals * 0.32) / 4)
        carbs_g = round((cals * 0.43) / 4)
        fats_g = round((cals * 0.25) / 9)

    title = f"{diet_type.replace('_', ' ').title()} Plan ({cals} kcal - {goal.replace('_', ' ').title()})"

    # Select meal templates based on diet type
    if diet_type == "vegetarian":
        m1 = ("Power Breakfast", "Oatmeal with Almond Milk, Chia Seeds, Whey/Plant Protein powder, sliced bananas & walnuts", round(cals * 0.25), "32g", "55g", "12g")
        m2 = ("High-Protein Lunch", "Paneer / Tofu Stir-Fry with quinoa, bell peppers, broccoli, edamame and olive oil", round(cals * 0.30), "38g", "60g", "16g")
        m3 = ("Pre/Post-Workout Snack", "Greek Yogurt with berries, honey, and a handful of roasted almonds", round(cals * 0.15), "22g", "25g", "8g")
        m4 = ("Nutrient-Dense Dinner", "Lentil / Chickpea Curry (Dal) with brown rice, sautéed spinach, and mixed greens salad", round(cals * 0.30), "35g", "65g", "14g")
    elif diet_type == "vegan":
        m1 = ("Superfood Vegan Breakfast", "Steel-cut oats with hemp seeds, pea protein isolate, blueberries, and peanut butter", round(cals * 0.25), "30g", "58g", "14g")
        m2 = ("Macro Power Bowl", "Crispy Tempeh & Edamame with brown rice, avocado slices, roasted zucchini, and tahini drizzle", round(cals * 0.30), "36g", "55g", "18g")
        m3 = ("High Energy Snack", "Vegan protein shake with soy milk, 1 banana, and 1 tbsp chia seeds", round(cals * 0.15), "25g", "30g", "6g")
        m4 = ("Plant-Based Dinner", "Tofu & Black Bean Burrito Bowl with sweet potato cubes, roasted peppers, and salsa", round(cals * 0.30), "34g", "68g", "15g")
    elif diet_type == "keto":
        m1 = ("Keto Keto Breakfast", "3 Whole eggs scrambled in butter with spinach, cheddar cheese, and sliced avocado", round(cals * 0.28), "30g", "4g", "42g")
        m2 = ("Keto Lunch Salad", "Grilled chicken thighs over romaine lettuce, olive oil, parmesan shavings, and bacon bits", round(cals * 0.32), "45g", "5g", "48g")
        m3 = ("Keto Fat-Fuel Snack", "Macadamia nuts, String Cheese, and Celery sticks with almond butter", round(cals * 0.15), "12g", "3g", "25g")
        m4 = ("Keto Salmon Dinner", "Pan-seared Atlantic Salmon fillet with garlic butter asparagus and cauliflower mash", round(cals * 0.25), "40g", "6g", "40g")
    else: # Standard / High Protein
        m1 = ("Champion Breakfast", "3 Whole eggs + 2 egg whites, 1 cup rolled oats cooked with water/milk, 1/2 cup blueberries", round(cals * 0.26), "35g", "52g", "14g")
        m2 = ("Performance Lunch", "Grilled chicken breast (180g), 1 cup Jasmine rice, steamed broccoli & 1 tsp extra virgin olive oil", round(cals * 0.32), "48g", "60g", "12g")
        m3 = ("Afternoon Anabolic Snack", "Low-fat Greek Yogurt (200g) with 1 scoop Whey Protein, 1 sliced apple, and 15g almonds", round(cals * 0.16), "32g", "28g", "7g")
        m4 = ("Recovery Dinner", "Baked Salmon or Lean Sirloin (170g), baked sweet potato (200g), and large mixed green salad", round(cals * 0.26), "42g", "45g", "15g")

    meals = [m1, m2, m3, m4]

    md = f"""## 🥗 {title}

### 📊 Daily Macronutrient & Calorie Blueprint
| Metric | Daily Target | % of Total Calories |
| :--- | :--- | :--- |
| **Total Energy** | **{cals} kcal** | 100% |
| **Protein** | **{protein_g}g** ({protein_g * 4} kcal) | ~{round(protein_g * 4 / cals * 100)}% |
| **Carbohydrates** | **{carbs_g}g** ({carbs_g * 4} kcal) | ~{round(carbs_g * 4 / cals * 100)}% |
| **Fats** | **{fats_g}g** ({fats_g * 9} kcal) | ~{round(fats_g * 9 / cals * 100)}% |

---

### 🍽️ Daily Meal Schedule
"""

    for i, (name, desc, m_cals, p, c, f) in enumerate(meals, 1):
        md += f"""#### 🍴 Meal {i}: {name}
* **Description:** {desc}
* **Macros:** **{m_cals} kcal** | Protein: **{p}** | Carbs: **{c}** | Fats: **{f}**

"""

    md += f"""---

### 💧 Hydration & Micronutrient Guidelines
* **Water Intake:** Drink **{round(cals/1000 * 1.5, 1)} to 3.5 Liters** of water throughout the day.
* **Electrolytes:** Add a pinch of sea salt to your pre-workout meal or water bottle.
* **Essential Supplements:**
  1. **Creatine Monohydrate:** 5g daily
  2. **Vitamin D3 + K2:** 2000-5000 IU with a meal containing fat
  3. **Omega-3 Fish Oil (or Algal Oil):** 1000mg combined EPA/DHA daily
  4. **Multivitamin / Magnesium Glycinate:** 200-400mg before bed for deep sleep & muscle recovery

---

### 🛒 Weekly Grocery Checklist
* **Proteins:** Chicken breast, Salmon/Tuna, Eggs/Egg whites, Greek Yogurt, Whey/Plant Protein
* **Carbohydrates:** Rolled oats, Jasmine/Brown rice, Sweet potatoes, Quinoa, Bananas, Berries
* **Healthy Fats:** Extra virgin olive oil, Avocado, Raw almonds/walnuts, Chia seeds
* **Veggies:** Baby spinach, Broccoli florets, Asparagus, Bell peppers, Mixed salad greens
"""

    return {
        "title": title,
        "content": md,
        "target_calories": cals,
        "protein_g": protein_g,
        "carbs_g": carbs_g,
        "fats_g": fats_g,
        "structured": [
            {"meal": m[0], "description": m[1], "calories": m[2], "protein": m[3], "carbs": m[4], "fats": m[5]}
            for m in meals
        ]
    }
