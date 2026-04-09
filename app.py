import streamlit as st
import pandas as pd
from datetime import date
from database import init_db, save_log, get_last_7_days, get_all_logs, get_streak, get_weekly_summary, get_alerts
from ai_coach import get_coaching_stream, chat_with_coach, predict_mood

init_db()

st.set_page_config(page_title="AI Health Coach", page_icon="🧠", layout="wide")

# Init chat history in session state
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

st.sidebar.title("🧠 AI Health Coach")

streak = get_streak()
if streak > 0:
    st.sidebar.markdown(f"### 🔥 {streak} day streak!")
else:
    st.sidebar.markdown("### Log today to start a streak!")

page = st.sidebar.radio("Navigate", ["📝 Log Today", "📊 Dashboard", "🤖 Daily Brief", "💬 Chat with Coach"])
st.sidebar.markdown("---")
st.sidebar.caption("All data stored locally on your PC")

# ── PAGE 1: Log Today ──────────────────────────────────
if page == "📝 Log Today":
    st.title("📝 Log Your Day")
    st.caption("Takes less than 2 minutes. Your data never leaves your computer.")

    alerts = get_alerts()
    for alert in alerts:
        if "Alert" in alert[0]:
            st.warning(f"**{alert[0]}** — {alert[1]}")
        else:
            st.success(f"**{alert[0]}** — {alert[1]}")

    with st.form("daily_log"):
        col1, col2 = st.columns(2)
        with col1:
            log_date = st.date_input("Date", value=date.today())
            mood = st.slider("😊 Mood", 1, 10, 5, help="1 = terrible, 10 = amazing")
            energy = st.slider("⚡ Energy level", 1, 10, 5)
        with col2:
            sleep_hrs = st.number_input("😴 Hours of sleep", min_value=0.0, max_value=24.0, value=7.0, step=0.5)
            tasks_done = st.number_input("✅ Tasks completed today", min_value=0, max_value=50, value=3)
        notes = st.text_area("📓 Notes (optional)", placeholder="How did you feel? Stress levels? Anything unusual?", height=100)
        submitted = st.form_submit_button("💾 Save Log", use_container_width=True, type="primary")
        if submitted:
            save_log(str(log_date), mood, sleep_hrs, energy, tasks_done, notes)
            st.success(f"✅ Log saved for {log_date}!")
            st.balloons()

    st.markdown("---")
    st.subheader("Recent entries")
    rows = get_last_7_days()
    if rows:
        df = pd.DataFrame(rows, columns=["Date", "Mood", "Sleep (hrs)", "Energy", "Tasks Done", "Notes"])
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.info("No entries yet. Log your first day above!")

# ── PAGE 2: Dashboard ─────────────────────────────────
elif page == "📊 Dashboard":
    st.title("📊 Your Dashboard")
    rows = get_all_logs()

    if not rows:
        st.warning("No data yet! Go to 'Log Today' to add your first entry.")
    else:
        df = pd.DataFrame(rows, columns=["Date", "Mood", "Sleep", "Energy", "Tasks", "Notes"])
        df["Date"] = pd.to_datetime(df["Date"])
        df = df.sort_values("Date")

        summary = get_weekly_summary()
        if summary:
            st.subheader("📋 This week's summary")
            col1, col2, col3, col4, col5 = st.columns(5)
            col1.metric("Avg Mood", f"{summary['avg_mood']}/10")
            col2.metric("Avg Sleep", f"{summary['avg_sleep']} hrs")
            col3.metric("Avg Energy", f"{summary['avg_energy']}/10")
            col4.metric("Tasks Done", summary['total_tasks'])
            col5.metric("Days Logged", f"{summary['days_logged']}/7")
            col_a, col_b = st.columns(2)
            col_a.success(f"🌟 Best day: **{summary['best_day']}**")
            col_b.error(f"📉 Toughest day: **{summary['worst_day']}**")

        # Mood prediction
        logs = get_last_7_days()
        prediction = predict_mood(logs)
        if prediction:
            st.markdown("---")
            st.subheader("🔮 Tomorrow's mood prediction")
            col1, col2, col3 = st.columns(3)
            col1.metric("Predicted mood", f"{prediction['predicted']}/10")
            col2.metric("Your trend", prediction['direction'])
            col3.metric("Recent avg", f"{prediction['avg_mood']}/10")

        alerts = get_alerts()
        if alerts:
            st.markdown("---")
            st.subheader("🚨 Pattern Alerts")
            for alert in alerts:
                if "Alert" in alert[0]:
                    st.warning(f"**{alert[0]}** — {alert[1]}")
                else:
                    st.success(f"**{alert[0]}** — {alert[1]}")

        st.markdown("---")
        import plotly.express as px
        col_a, col_b = st.columns(2)
        with col_a:
            fig1 = px.line(df, x="Date", y="Mood", title="Mood over time", markers=True, color_discrete_sequence=["#7F77DD"])
            fig1.update_layout(height=280, margin=dict(t=40, b=20))
            st.plotly_chart(fig1, use_container_width=True)
        with col_b:
            fig2 = px.line(df, x="Date", y="Sleep", title="Sleep over time", markers=True, color_discrete_sequence=["#1D9E75"])
            fig2.update_layout(height=280, margin=dict(t=40, b=20))
            st.plotly_chart(fig2, use_container_width=True)
        col_c, col_d = st.columns(2)
        with col_c:
            fig3 = px.bar(df, x="Date", y="Energy", title="Energy levels", color="Energy",
                          color_continuous_scale=["#3B8BD4", "#EF9F27", "#D85A30"])
            fig3.update_layout(height=280, margin=dict(t=40, b=20))
            st.plotly_chart(fig3, use_container_width=True)
        with col_d:
            fig4 = px.bar(df, x="Date", y="Tasks", title="Tasks completed", color_discrete_sequence=["#D85A30"])
            fig4.update_layout(height=280, margin=dict(t=40, b=20))
            st.plotly_chart(fig4, use_container_width=True)

# ── PAGE 3: Daily Brief (Streaming) ───────────────────
elif page == "🤖 Daily Brief":
    st.title("🤖 Your Daily Brief")
    st.caption("Powered by Mistral AI — runs locally, data stays on your PC.")

    rows = get_last_7_days()
    summary = get_weekly_summary()
    alerts = get_alerts()

    if not rows:
        st.warning("Log at least one day of data first!")
    else:
        if alerts:
            st.subheader("Your coach will address these alerts:")
            for alert in alerts:
                if "Alert" in alert[0]:
                    st.warning(f"**{alert[0]}** — {alert[1]}")
                else:
                    st.success(f"**{alert[0]}** — {alert[1]}")
            st.markdown("---")

        if st.button("🧠 Generate My Daily Brief", type="primary", use_container_width=True):
            st.markdown("---")
            with st.chat_message("assistant"):
                response_placeholder = st.empty()
                full_response = ""
                for chunk in get_coaching_stream(rows, summary, alerts):
                    full_response += chunk
                    response_placeholder.markdown(full_response + "▌")
                response_placeholder.markdown(full_response)
            st.markdown("---")
            st.caption("💡 Analysis based on your logged data only.")

# ── PAGE 4: Chat with Coach ────────────────────────────
elif page == "💬 Chat with Coach":
    st.title("💬 Chat with Your Coach")
    st.caption("Ask anything about your health, habits, or productivity.")

    rows = get_last_7_days()

    # Display chat history
    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # Suggested questions
    if not st.session_state.chat_history:
        st.markdown("**Try asking:**")
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("Why is my energy low?"):
                st.session_state.pending_question = "Why has my energy been low recently?"
        with col2:
            if st.button("How can I sleep better?"):
                st.session_state.pending_question = "What can I do to improve my sleep?"
        with col3:
            if st.button("Am I being productive?"):
                st.session_state.pending_question = "Am I being productive based on my data?"

    # Handle suggested question clicks
    if "pending_question" in st.session_state:
        question = st.session_state.pop("pending_question")
        st.session_state.chat_history.append({"role": "user", "content": question})
        with st.chat_message("user"):
            st.markdown(question)
        with st.chat_message("assistant"):
            response_placeholder = st.empty()
            full_response = ""
            for chunk in chat_with_coach(question, rows, st.session_state.chat_history):
                full_response += chunk
                response_placeholder.markdown(full_response + "▌")
            response_placeholder.markdown(full_response)
        st.session_state.chat_history.append({"role": "assistant", "content": full_response})
        st.rerun()

    # Chat input
    if user_input := st.chat_input("Ask your coach anything..."):
        st.session_state.chat_history.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.markdown(user_input)
        with st.chat_message("assistant"):
            response_placeholder = st.empty()
            full_response = ""
            for chunk in chat_with_coach(user_input, rows, st.session_state.chat_history):
                full_response += chunk
                response_placeholder.markdown(full_response + "▌")
            response_placeholder.markdown(full_response)
        st.session_state.chat_history.append({"role": "assistant", "content": full_response})

    if st.session_state.chat_history:
        if st.button("🗑️ Clear chat"):
            st.session_state.chat_history = []
            st.rerun()
