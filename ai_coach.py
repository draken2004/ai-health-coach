import ollama

def build_prompt(logs, summary, alerts):
    if not logs:
        return "No data yet. Greet the user warmly and encourage them to log their first day."

    log_text = ""
    for log in logs:
        date, mood, sleep_hrs, energy, tasks_done, notes = log
        log_text += f"\n- {date}: Mood={mood}/10, Sleep={sleep_hrs}hrs, Energy={energy}/10, Tasks={tasks_done}, Notes: {notes or 'none'}"

    alert_text = ""
    if alerts:
        alert_text = "\nCurrent alerts:\n" + "\n".join([f"- {a[0]}: {a[1]}" for a in alerts])

    summary_text = ""
    if summary:
        summary_text = f"\nWeek summary: Avg mood={summary['avg_mood']}, Avg sleep={summary['avg_sleep']}hrs, Avg energy={summary['avg_energy']}, Total tasks={summary['total_tasks']}, Best day={summary['best_day']}, Worst day={summary['worst_day']}"

    prompt = f"""You are a warm, smart personal health and productivity coach.
Here is your client's recent data:{log_text}
{summary_text}
{alert_text}

Give them:
1. A 2-sentence encouraging summary of their recent performance
2. The most important pattern you notice (positive or negative)
3. Exactly 3 specific actionable tips for TODAY based on their numbers
4. A mood prediction for tomorrow based on their trend
5. One motivational closing line

Be conversational, specific, and human. Reference their actual numbers."""

    return prompt


def get_coaching_stream(logs, summary=None, alerts=None):
    """Returns a streaming generator for live text output."""
    prompt = build_prompt(logs, summary, alerts)
    try:
        stream = ollama.chat(
            model='mistral',
            messages=[{'role': 'user', 'content': prompt}],
            stream=True
        )
        for chunk in stream:
            yield chunk['message']['content']
    except Exception as e:
        yield f"⚠️ Could not connect to Ollama. Make sure it's running.\n\nOpen a new CMD window and run: ollama serve\n\nError: {str(e)}"


def get_coaching(logs, summary=None, alerts=None):
    """Non-streaming version (kept for compatibility)."""
    prompt = build_prompt(logs, summary, alerts)
    try:
        response = ollama.chat(
            model='mistral',
            messages=[{'role': 'user', 'content': prompt}]
        )
        return response['message']['content']
    except Exception as e:
        return f"⚠️ Could not connect to Ollama.\n\nRun: ollama serve\n\nError: {str(e)}"


def chat_with_coach(user_message, logs, chat_history):
    """Custom chat mode — user can ask anything."""
    log_text = ""
    if logs:
        for log in logs[:7]:
            date, mood, sleep_hrs, energy, tasks_done, notes = log
            log_text += f"\n- {date}: Mood={mood}/10, Sleep={sleep_hrs}hrs, Energy={energy}/10, Tasks={tasks_done}, Notes: {notes or 'none'}"

    system_context = f"""You are a friendly personal health and productivity coach.
You have access to the user's recent health data:{log_text if log_text else ' No data logged yet.'}

Answer their questions with empathy and specificity.
If they ask about their data, reference the actual numbers.
Keep responses concise — 3 to 5 sentences max unless they ask for more.
Never give generic advice — always tie it back to their specific situation."""

    messages = [{'role': 'user', 'content': system_context + "\n\nUser: " + user_message}]

    if chat_history:
        history_text = "\n".join([f"{m['role'].capitalize()}: {m['content']}" for m in chat_history[-6:]])
        messages = [{'role': 'user', 'content': system_context + f"\n\nConversation so far:\n{history_text}\n\nUser: {user_message}"}]

    try:
        stream = ollama.chat(
            model='mistral',
            messages=messages,
            stream=True
        )
        for chunk in stream:
            yield chunk['message']['content']
    except Exception as e:
        yield f"⚠️ Ollama not running. Open a new CMD window and run: ollama serve"


def predict_mood(logs):
    """Simple mood prediction based on recent trend."""
    if len(logs) < 3:
        return None
    recent_moods = [l[1] for l in logs[:5] if l[1]]
    recent_sleep = [l[2] for l in logs[:3] if l[2]]
    recent_energy = [l[3] for l in logs[:3] if l[3]]
    if not recent_moods:
        return None
    avg_mood = sum(recent_moods) / len(recent_moods)
    trend = recent_moods[0] - recent_moods[-1]
    avg_sleep = sum(recent_sleep) / len(recent_sleep) if recent_sleep else 7
    sleep_factor = 1 if avg_sleep >= 7 else -1 if avg_sleep < 5.5 else 0
    predicted = round(min(10, max(1, avg_mood + (trend * 0.2) + sleep_factor)), 1)
    if trend > 1:
        direction = "📈 improving"
    elif trend < -1:
        direction = "📉 declining"
    else:
        direction = "➡️ stable"
    return {"predicted": predicted, "direction": direction, "avg_mood": round(avg_mood, 1)}
