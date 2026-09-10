import sqlite3
import json
from datetime import datetime
from config import Config

def get_db_connection():
    conn = sqlite3.connect(Config.DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()

    # User Profile table (single default user or multi-profile support)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_profile (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT DEFAULT 'Athlete',
            age INTEGER DEFAULT 25,
            gender TEXT DEFAULT 'male',
            height REAL DEFAULT 175,
            weight REAL DEFAULT 70,
            activity_level TEXT DEFAULT 'moderate',
            fitness_goal TEXT DEFAULT 'muscle_gain',
            dietary_preference TEXT DEFAULT 'standard',
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Chat Messages table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS chat_messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT DEFAULT 'default',
            role TEXT NOT NULL,
            content TEXT NOT NULL,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Workout Plans table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS workout_plans (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            goal TEXT,
            experience_level TEXT,
            days_per_week INTEGER,
            equipment TEXT,
            plan_content TEXT NOT NULL,
            structured_data TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Diet Plans table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS diet_plans (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            goal TEXT,
            diet_type TEXT,
            target_calories INTEGER,
            protein_g INTEGER,
            carbs_g INTEGER,
            fats_g INTEGER,
            plan_content TEXT NOT NULL,
            structured_data TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Progress Tracking table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS progress_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            log_date DATE NOT NULL,
            weight REAL NOT NULL,
            body_fat REAL,
            chest REAL,
            waist REAL,
            arms REAL,
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Settings table (for API keys or user preferences)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS app_settings (
            key TEXT PRIMARY KEY,
            value TEXT
        )
    """)

    # Insert default profile if none exists
    cursor.execute("SELECT COUNT(*) as count FROM user_profile")
    if cursor.fetchone()["count"] == 0:
        cursor.execute("""
            INSERT INTO user_profile (name, age, gender, height, weight, activity_level, fitness_goal, dietary_preference)
            VALUES ('Fitness Champion', 25, 'male', 175.0, 72.0, 'moderate', 'muscle_gain', 'high_protein')
        """)

    # Seed sample progress logs if empty for initial rich dashboard display
    cursor.execute("SELECT COUNT(*) as count FROM progress_logs")
    if cursor.fetchone()["count"] == 0:
        sample_logs = [
            ('2025-01-01', 75.5, 18.5, 'Starting fresh for the new year.'),
            ('2025-01-15', 74.8, 18.0, 'Consistent 4-day workout split and clean eating.'),
            ('2025-02-01', 73.9, 17.2, 'Strength increasing on bench and squat.'),
            ('2025-02-15', 73.0, 16.5, 'Visible core definition, hitting protein goals.'),
            ('2025-03-01', 72.2, 15.8, 'Energy levels great, recovery is on point.')
        ]
        for log in sample_logs:
            cursor.execute("""
                INSERT INTO progress_logs (log_date, weight, body_fat, notes)
                VALUES (?, ?, ?, ?)
            """, log)

    conn.commit()
    conn.close()

# User Profile CRUD
def get_user_profile():
    conn = get_db_connection()
    profile = conn.execute("SELECT * FROM user_profile ORDER BY id ASC LIMIT 1").fetchone()
    conn.close()
    return dict(profile) if profile else None

def update_user_profile(data):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE user_profile
        SET name = ?, age = ?, gender = ?, height = ?, weight = ?,
            activity_level = ?, fitness_goal = ?, dietary_preference = ?, updated_at = CURRENT_TIMESTAMP
        WHERE id = (SELECT id FROM user_profile ORDER BY id ASC LIMIT 1)
    """, (
        data.get('name', 'Athlete'),
        int(data.get('age', 25)),
        data.get('gender', 'male'),
        float(data.get('height', 175)),
        float(data.get('weight', 70)),
        data.get('activity_level', 'moderate'),
        data.get('fitness_goal', 'muscle_gain'),
        data.get('dietary_preference', 'standard')
    ))
    conn.commit()
    conn.close()
    return get_user_profile()

# Chat CRUD
def get_chat_history(session_id='default', limit=50):
    conn = get_db_connection()
    rows = conn.execute("""
        SELECT id, role, content, timestamp FROM chat_messages
        WHERE session_id = ?
        ORDER BY id ASC LIMIT ?
    """, (session_id, limit)).fetchall()
    conn.close()
    return [dict(row) for row in rows]

def save_chat_message(role, content, session_id='default'):
    conn = get_db_connection()
    conn.execute("""
        INSERT INTO chat_messages (session_id, role, content)
        VALUES (?, ?, ?)
    """, (session_id, role, content))
    conn.commit()
    conn.close()

def clear_chat_history(session_id='default'):
    conn = get_db_connection()
    conn.execute("DELETE FROM chat_messages WHERE session_id = ?", (session_id,))
    conn.commit()
    conn.close()

# Workout Plans CRUD
def save_workout_plan(title, goal, experience_level, days_per_week, equipment, plan_content, structured_data=None):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO workout_plans (title, goal, experience_level, days_per_week, equipment, plan_content, structured_data)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        title,
        goal,
        experience_level,
        days_per_week,
        equipment,
        plan_content,
        json.dumps(structured_data) if structured_data else None
    ))
    plan_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return plan_id

def get_workout_plans(limit=20):
    conn = get_db_connection()
    rows = conn.execute("SELECT * FROM workout_plans ORDER BY id DESC LIMIT ?", (limit,)).fetchall()
    conn.close()
    return [dict(row) for row in rows]

def get_workout_plan_by_id(plan_id):
    conn = get_db_connection()
    row = conn.execute("SELECT * FROM workout_plans WHERE id = ?", (plan_id,)).fetchone()
    conn.close()
    return dict(row) if row else None

def delete_workout_plan(plan_id):
    conn = get_db_connection()
    conn.execute("DELETE FROM workout_plans WHERE id = ?", (plan_id,))
    conn.commit()
    conn.close()

# Diet Plans CRUD
def save_diet_plan(title, goal, diet_type, target_calories, protein_g, carbs_g, fats_g, plan_content, structured_data=None):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO diet_plans (title, goal, diet_type, target_calories, protein_g, carbs_g, fats_g, plan_content, structured_data)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        title,
        goal,
        diet_type,
        target_calories,
        protein_g,
        carbs_g,
        fats_g,
        plan_content,
        json.dumps(structured_data) if structured_data else None
    ))
    plan_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return plan_id

def get_diet_plans(limit=20):
    conn = get_db_connection()
    rows = conn.execute("SELECT * FROM diet_plans ORDER BY id DESC LIMIT ?", (limit,)).fetchall()
    conn.close()
    return [dict(row) for row in rows]

def get_diet_plan_by_id(plan_id):
    conn = get_db_connection()
    row = conn.execute("SELECT * FROM diet_plans WHERE id = ?", (plan_id,)).fetchone()
    conn.close()
    return dict(row) if row else None

def delete_diet_plan(plan_id):
    conn = get_db_connection()
    conn.execute("DELETE FROM diet_plans WHERE id = ?", (plan_id,))
    conn.commit()
    conn.close()

# Progress CRUD
def add_progress_log(log_date, weight, body_fat=None, chest=None, waist=None, arms=None, notes=None):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO progress_logs (log_date, weight, body_fat, chest, waist, arms, notes)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (log_date, weight, body_fat, chest, waist, arms, notes))
    log_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return log_id

def get_progress_logs(limit=50):
    conn = get_db_connection()
    rows = conn.execute("SELECT * FROM progress_logs ORDER BY log_date ASC, id ASC LIMIT ?", (limit,)).fetchall()
    conn.close()
    return [dict(row) for row in rows]

def delete_progress_log(log_id):
    conn = get_db_connection()
    conn.execute("DELETE FROM progress_logs WHERE id = ?", (log_id,))
    conn.commit()
    conn.close()

# Settings CRUD
def get_setting(key, default=None):
    conn = get_db_connection()
    row = conn.execute("SELECT value FROM app_settings WHERE key = ?", (key,)).fetchone()
    conn.close()
    return row["value"] if row else default

def set_setting(key, value):
    conn = get_db_connection()
    conn.execute("""
        INSERT INTO app_settings (key, value) VALUES (?, ?)
        ON CONFLICT(key) DO UPDATE SET value = excluded.value
    """, (key, str(value)))
    conn.commit()
    conn.close()
