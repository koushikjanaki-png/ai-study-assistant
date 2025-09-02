# app.py - Study Assistant (Streamlit)
import streamlit as st
import pandas as pd
import os
import random

st.set_page_config(page_title="AI Study Assistant", layout="centered")
st.title("📘 AI Study Assistant")
st.write("Simple study planner and recommender. (Works online via Streamlit Cloud)")

# -------------------------
# Load subjects.csv if exists, otherwise use default data
# -------------------------
@st.cache_data
def load_topics():
    if os.path.exists("subjects.csv"):
        return pd.read_csv("subjects.csv")
    data = {
        "subject": ["Math","Math","Science","Science","English","English"],
        "topic": ["Algebra","Trigonometry","Physics","Chemistry","Grammar","Essay Writing"],
        "difficulty": ["Medium","Hard","Medium","Easy","Easy","Hard"]
    }
    return pd.DataFrame(data)

df = load_topics()

# -------------------------
# Helper functions
# -------------------------
def recommend_topics(subject=None, n=3):
    pool = df.copy()
    if subject and subject != "All":
        pool = pool[pool["subject"] == subject]
    if pool.empty:
        return pd.DataFrame(columns=df.columns)
    return pool.sample(n=min(n, len(pool)), replace=False).reset_index(drop=True)

def make_study_plan(hours_per_day, days_left):
    total = days_left * hours_per_day
    pool = df.copy()
    # allow repeats if total > len(pool)
    sampled = pool.sample(n=total, replace=True).reset_index(drop=True)
    plan = {}
    idx = 0
    for day in range(1, days_left+1):
        plan[day] = sampled.iloc[idx:idx+hours_per_day]["topic"].tolist()
        idx += hours_per_day
    return plan

def adaptive_recommend(progress):
    weak = [t for t,s in progress.items() if s=="weak"]
    return weak if weak else ["All topics look good 👍"]

# -------------------------
# Session state for progress
# -------------------------
if "progress" not in st.session_state:
    st.session_state.progress = {}

# -------------------------
# UI: show topics
# -------------------------
st.subheader("📚 Subjects & Topics")
st.dataframe(df, use_container_width=True)

# -------------------------
# UI: Recommendation
# -------------------------
st.subheader("🎯 Get Topic Recommendations")
subject_choice = st.selectbox("Choose subject:", ["All"] + sorted(df["subject"].unique().tolist()))
num = st.slider("How many topics to recommend?", 1, 5, 2)
if st.button("Recommend"):
    recs = recommend_topics(subject_choice, n=num)
    st.table(recs)

# -------------------------
# UI: Study Plan
# -------------------------
st.subheader("🗓️ Generate Study Plan")
hours = st.number_input("Hours per day:", min_value=1, max_value=6, value=2)
days = st.number_input("Days left:", min_value=1, max_value=60, value=5)
if st.button("Generate Study Plan"):
    plan = make_study_plan(int(hours), int(days))
    for d, topics in plan.items():
        st.write(f"**Day {d}:** {topics}")

# -------------------------
# UI: Mark Progress (Adaptive)
# -------------------------
st.subheader("📌 Mark Your Progress (so AI adapts)")
col1, col2 = st.columns(2)
with col1:
    topic_pick = st.selectbox("Pick topic:", df["topic"].unique())
with col2:
    status = st.selectbox("Set status:", ["weak","ok","good"])
if st.button("Save progress"):
    st.session_state.progress[topic_pick] = status
    st.success(f"Saved: {topic_pick} = {status}")

if st.button("Show Weak Topics"):
    st.write(adaptive_recommend(st.session_state.progress))
    st.write("Current progress:", st.session_state.progress)
  
