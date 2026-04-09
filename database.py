import sqlite3
from datetime import datetime, date, timedelta

DB_PATH = "health_coach.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS daily_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            mood INTEGER,
            sleep_hrs REAL,
            energy INTEGER,
            tasks_done INTEGER,
            notes TEXT,
            created_at TEXT
        )
    ''')
    conn.commit()
    conn.close()

def save_log(date, mood, sleep_hrs, energy, tasks_done, notes):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT id FROM daily_logs WHERE date = ?", (date,))
    existing = c.fetchone()
    if existing:
        c.execute('''
            UPDATE daily_logs SET mood=?, sleep_hrs=?, energy=?, tasks_done=?, notes=?, created_at=?
            WHERE date=?
        ''', (mood, sleep_hrs, energy, tasks_done, notes, datetime.now().isoformat(), date))
    else:
        c.execute('''
            INSERT INTO daily_logs (date, mood, sleep_hrs, energy, tasks_done, notes, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (date, mood, sleep_hrs, energy, tasks_done, notes, datetime.now().isoformat()))
    conn.commit()
    conn.close()

def get_last_7_days():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        SELECT date, mood, sleep_hrs, energy, tasks_done, notes
        FROM daily_logs ORDER BY date DESC LIMIT 7
    ''')
    rows = c.fetchall()
    conn.close()
    return rows

def get_all_logs():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT date, mood, sleep_hrs, energy, tasks_done, notes FROM daily_logs ORDER BY date DESC')
    rows = c.fetchall()
    conn.close()
    return rows

def get_streak():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT date FROM daily_logs ORDER BY date DESC')
    dates = [row[0] for row in c.fetchall()]
    conn.close()
    if not dates:
        return 0
    streak = 0
    check = date.today()
    for d in dates:
        log_date = datetime.strptime(d, "%Y-%m-%d").date()
        if log_date == check:
            streak += 1
            check -= timedelta(days=1)
        elif log_date == check + timedelta(days=1):
            # allow yesterday if today not logged yet
            streak += 1
            check = log_date - timedelta(days=1)
        else:
            break
    return streak

def get_weekly_summary():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        SELECT date, mood, sleep_hrs, energy, tasks_done
        FROM daily_logs ORDER BY date DESC LIMIT 7
    ''')
    rows = c.fetchall()
    conn.close()
    if not rows:
        return None
    moods = [r[1] for r in rows if r[1]]
    sleeps = [r[2] for r in rows if r[2]]
    energies = [r[3] for r in rows if r[3]]
    tasks = [r[4] for r in rows if r[4] is not None]
    best_day = max(rows, key=lambda x: (x[1] or 0) + (x[3] or 0))
    worst_day = min(rows, key=lambda x: (x[1] or 10) + (x[3] or 10))
    return {
        "avg_mood": round(sum(moods)/len(moods), 1) if moods else 0,
        "avg_sleep": round(sum(sleeps)/len(sleeps), 1) if sleeps else 0,
        "avg_energy": round(sum(energies)/len(energies), 1) if energies else 0,
        "total_tasks": sum(tasks),
        "best_day": best_day[0],
        "worst_day": worst_day[0],
        "days_logged": len(rows)
    }

def get_alerts():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        SELECT date, mood, sleep_hrs, energy
        FROM daily_logs ORDER BY date DESC LIMIT 5
    ''')
    rows = c.fetchall()
    conn.close()
    alerts = []
    if len(rows) >= 3:
        recent_sleep = [r[2] for r in rows[:3] if r[2]]
        if recent_sleep and all(s < 6 for s in recent_sleep):
            alerts.append(("⚠️ Sleep Alert", "You've slept less than 6 hours for 3 days in a row. Prioritise rest tonight."))
        recent_mood = [r[1] for r in rows[:3] if r[1]]
        if recent_mood and all(m <= 4 for m in recent_mood):
            alerts.append(("😟 Mood Alert", "Your mood has been low for 3 consecutive days. Consider a short walk or talking to someone."))
        recent_energy = [r[3] for r in rows[:3] if r[3]]
        if recent_energy and all(e <= 3 for e in recent_energy):
            alerts.append(("⚡ Energy Alert", "Energy has been very low for 3 days. Check your sleep, hydration and meal timing."))
    if len(rows) >= 3:
        recent_mood = [r[1] for r in rows[:3] if r[1]]
        if recent_mood and all(m >= 8 for m in recent_mood):
            alerts.append(("🌟 Great Streak!", "You've had a high mood for 3 days in a row. Keep doing what you're doing!"))
    return alerts
