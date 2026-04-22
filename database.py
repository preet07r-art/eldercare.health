# ElderCare Database Engine - Final Stable Version
import sqlite3
from datetime import datetime

def get_connection():
    return sqlite3.connect("eldercare.db", check_same_thread=False)

def migrate_database():
    conn = get_connection(); c = conn.cursor()
    # 1. Base Table Creation
    c.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, name TEXT)")
    c.execute("CREATE TABLE IF NOT EXISTS vitals (id INTEGER PRIMARY KEY, date TEXT)")
    c.execute("CREATE TABLE IF NOT EXISTS medications (id INTEGER PRIMARY KEY, name TEXT)")
    c.execute("CREATE TABLE IF NOT EXISTS medication_logs (id INTEGER PRIMARY KEY, medication_id INTEGER, date TEXT, status TEXT, slot TEXT)")
    c.execute("CREATE TABLE IF NOT EXISTS vitals_goals (id INTEGER PRIMARY KEY)")
    
    # 2. Advanced Auto-Migration (Adds any missing columns automatically)
    all_cols = {
        "users": ["date_of_birth", "age", "gender", "blood_group", "height", "weight", "known_conditions", "allergies", "caretaker_name", "caretaker_phone"],
        "vitals": ["time", "bp_systolic", "bp_diastolic", "heart_rate", "weight", "user_id", "blood_sugar_before_meal", "blood_sugar_after_meal"],
        "medications": ["dosage", "frequency", "start_date", "end_date", "user_id"],
        "vitals_goals": ["sys_min", "sys_max", "dia_min", "dia_max", "sug_min", "sug_max", "hr_min", "hr_max", "w_min", "w_max"]
    }
    
    for table, columns in all_cols.items():
        existing = [x[1] for x in c.execute(f"PRAGMA table_info({table})").fetchall()]
        for col in columns:
            if col not in existing:
                col_type = "REAL" if col in ['weight', 'height', 'w_min', 'w_max'] else "TEXT"
                c.execute(f"ALTER TABLE {table} ADD COLUMN {col} {col_type}")
    
    # 3. Seed Default Data
    if not c.execute("SELECT id FROM users WHERE id = 1").fetchone():
        c.execute("INSERT INTO users (id, name) VALUES (1, 'Elder User')")
    if c.execute("SELECT COUNT(*) FROM vitals_goals").fetchone()[0] == 0:
        c.execute("INSERT INTO vitals_goals (id, sys_min, sys_max, dia_min, dia_max, sug_min, sug_max, hr_min, hr_max, w_min, w_max) VALUES (1, 90, 120, 60, 80, 70, 140, 60, 100, 50, 90)")
    
    conn.commit(); conn.close()

def get_user():
    try:
        conn = get_connection(); conn.row_factory = sqlite3.Row
        c = conn.cursor()
        row = c.execute("SELECT * FROM users WHERE id = 1").fetchone()
        conn.close()
        return dict(row) if row else {}
    except: return {}

def update_user_profile(**kwargs):
    try:
        conn = get_connection(); c = conn.cursor()
        fields = []
        values = []
        for k, v in kwargs.items():
            col = "date_of_birth" if k == "dob" else k
            fields.append(f"{col}=?")
            values.append(v)
        
        if fields:
            query = f"UPDATE users SET {', '.join(fields)} WHERE id=1"
            c.execute(query, tuple(values))
            conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"DATABASE ERROR in update_user_profile: {e}")
        return False

def add_vitals(sys, dia, hr, weight, s_b=0, s_a=0):
    conn = get_connection(); c = conn.cursor()
    c.execute("INSERT INTO vitals (date, time, bp_systolic, bp_diastolic, heart_rate, weight, user_id, blood_sugar_before_meal, blood_sugar_after_meal) VALUES (?,?,?,?,?,?,?,?,?)", 
              (datetime.now().strftime("%Y-%m-%d"), datetime.now().strftime("%H:%M"), sys, dia, hr, weight, 1, s_b, s_a))
    conn.commit(); conn.close()

def get_vitals():
    conn = get_connection(); conn.row_factory = sqlite3.Row
    c = conn.cursor()
    rows = c.execute("SELECT * FROM vitals WHERE user_id = 1 ORDER BY date DESC, time DESC").fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_vitals_goals():
    conn = get_connection(); conn.row_factory = sqlite3.Row
    c = conn.cursor()
    row = c.execute("SELECT * FROM vitals_goals WHERE id = 1").fetchone()
    conn.close()
    return dict(row) if row else {}

def update_vitals_goals(**kwargs):
    conn = get_connection(); c = conn.cursor()
    for k, v in kwargs.items():
        c.execute(f"UPDATE vitals_goals SET {k}=? WHERE id=1", (v,))
    conn.commit(); conn.close()

def add_medication(name, dosage, freq, start, end):
    conn = get_connection(); c = conn.cursor()
    c.execute("INSERT INTO medications (name, dosage, frequency, start_date, end_date, user_id) VALUES (?,?,?,?,?,?)", (name, dosage, freq, start, end, 1))
    conn.commit(); conn.close()

def get_medications():
    conn = get_connection(); conn.row_factory = sqlite3.Row
    c = conn.cursor()
    rows = c.execute("SELECT * FROM medications WHERE user_id = 1").fetchall()
    conn.close()
    return [dict(r) for r in rows]

def delete_medication(mid):
    conn = get_connection(); c = conn.cursor()
    c.execute("DELETE FROM medications WHERE id = ?", (mid,))
    conn.commit(); conn.close()

def log_medication(mid, date, status, slot):
    conn = get_connection(); c = conn.cursor()
    c.execute("DELETE FROM medication_logs WHERE medication_id=? AND date=? AND slot=?", (mid, date, slot))
    c.execute("INSERT INTO medication_logs (medication_id, date, status, slot) VALUES (?,?,?,?)", (mid, date, status, slot))
    conn.commit(); conn.close()

def get_logs(date):
    conn = get_connection(); c = conn.cursor()
    c.execute("SELECT medication_id, slot, status FROM medication_logs WHERE date=?", (date,))
    rows = c.fetchall(); conn.close()
    return {(r[0], r[1]): r[2] for r in rows}
