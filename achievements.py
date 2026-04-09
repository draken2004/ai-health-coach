from database import get_all_logs, get_streak

def get_achievements(logs, streak):
    achievements = []
    total_days = len(logs)

    # Logging achievements
    if total_days >= 1:
        achievements.append({"icon": "🌱", "title": "First Step", "desc": "Logged your first day", "earned": True})
    if total_days >= 3:
        achievements.append({"icon": "📅", "title": "3 Day Logger", "desc": "Logged 3 days of data", "earned": True})
    if total_days >= 7:
        achievements.append({"icon": "🗓️", "title": "Week Warrior", "desc": "Logged a full week", "earned": True})
    else:
        achievements.append({"icon": "🗓️", "title": "Week Warrior", "desc": f"Log {7 - total_days} more days to unlock", "earned": False})

    # Streak achievements
    if streak >= 3:
        achievements.append({"icon": "🔥", "title": "On Fire", "desc": "3 day logging streak", "earned": True})
    else:
        achievements.append({"icon": "🔥", "title": "On Fire", "desc": f"Log {3 - streak} more days in a row", "earned": False})

    if streak >= 7:
        achievements.append({"icon": "⚡", "title": "Unstoppable", "desc": "7 day logging streak", "earned": True})
    else:
        achievements.append({"icon": "⚡", "title": "Unstoppable", "desc": f"{7 - streak} more days for 7-day streak", "earned": False})

    # Sleep achievements
    if logs:
        sleep_vals = [l[2] for l in logs if l[2]]
        if sleep_vals:
            good_sleep_days = sum(1 for s in sleep_vals if s >= 7)
            if good_sleep_days >= 5:
                achievements.append({"icon": "😴", "title": "Sleep Champion", "desc": "5+ days of 7hrs sleep", "earned": True})
            else:
                achievements.append({"icon": "😴", "title": "Sleep Champion", "desc": f"{5 - good_sleep_days} more good sleep nights needed", "earned": False})

        # Mood achievements
        mood_vals = [l[1] for l in logs if l[1]]
        if mood_vals:
            avg_mood = sum(mood_vals) / len(mood_vals)
            if avg_mood >= 7:
                achievements.append({"icon": "😊", "title": "Good Vibes", "desc": "Average mood above 7/10", "earned": True})
            else:
                achievements.append({"icon": "😊", "title": "Good Vibes", "desc": f"Avg mood needs to reach 7 (currently {round(avg_mood,1)})", "earned": False})

        # Productivity achievements
        task_vals = [l[4] for l in logs if l[4] is not None]
        if task_vals:
            total_tasks = sum(task_vals)
            if total_tasks >= 20:
                achievements.append({"icon": "✅", "title": "Task Master", "desc": "Completed 20+ total tasks", "earned": True})
            else:
                achievements.append({"icon": "✅", "title": "Task Master", "desc": f"{20 - total_tasks} more tasks to unlock", "earned": False})

    return achievements
