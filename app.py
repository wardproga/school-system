
import streamlit as st
import sqlite3
import pandas as pd
import datetime

st.set_page_config(page_title="School Management System", layout="wide")
st.title("🎓 School Management System")

# --- تسجيل الدخول ---
if "username" not in st.session_state:
    with st.form("login"):
        st.subheader("🔐 Login")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Login")
        if submitted:
            st.session_state["username"] = username
            st.success(f"Welcome, {username}!")
    st.stop()

username = st.session_state["username"]
role = "teacher" if username.startswith("Mr.") else "student"

# --- إشعارات ---
st.sidebar.subheader("🔔 Notifications")
conn = sqlite3.connect("school.db")
cursor = conn.cursor()
cursor.execute("SELECT id, message, sender, date, is_read FROM notifications WHERE recipient = ? ORDER BY id DESC", (username,))
notifications = cursor.fetchall()
conn.close()

for notif_id, msg, sender, date, is_read in notifications:
    status = "🆕" if is_read == 0 else "✅"
    with st.sidebar.expander(f"{status} {msg}"):
        st.write(f"📅 {date} | 👤 {sender}")
        if is_read == 0:
            if st.button(f"📖 Mark as Read {notif_id}", key=f"notif_{notif_id}"):
                conn = sqlite3.connect("school.db")
                cursor = conn.cursor()
                cursor.execute("UPDATE notifications SET is_read = 1 WHERE id = ?", (notif_id,))
                conn.commit()
                conn.close()
                st.experimental_rerun()

# --- واجهة المعلم ---
if role == "teacher":
    st.header("🧑‍🏫 Teacher Panel")

    st.subheader("📝 Create Quiz")
    quiz_title = st.text_input("Quiz Title")
    subject = st.selectbox("Subject", ["Math", "Science", "English"])
    if st.button("Create Quiz") and quiz_title:
        conn = sqlite3.connect("school.db")
        cursor = conn.cursor()
        cursor.execute("INSERT INTO quizzes (title, subject, created_by, created_at) VALUES (?, ?, ?, ?)",
                       (quiz_title, subject, username, str(datetime.date.today())))
        quiz_id = cursor.lastrowid
        conn.commit()
        conn.close()
        st.success("✅ Quiz Created")
        st.session_state["current_quiz_id"] = quiz_id

    quiz_id = st.session_state.get("current_quiz_id")
    if quiz_id:
        st.markdown("### ➕ Add Question")
        q_text = st.text_area("Question")
        q_type = st.radio("Type", ["Multiple Choice", "Text"])
        if q_type == "Multiple Choice":
            a = st.text_input("Option A")
            b = st.text_input("Option B")
            c = st.text_input("Option C")
            d = st.text_input("Option D")
            correct = st.selectbox("Correct Answer", ["A", "B", "C", "D"])
            if st.button("Save Question"):
                conn = sqlite3.connect("school.db")
                cursor = conn.cursor()
                cursor.execute("INSERT INTO quiz_questions (quiz_id, question, option_a, option_b, option_c, option_d, correct_option, is_multiple_choice) VALUES (?, ?, ?, ?, ?, ?, ?, 1)",
                               (quiz_id, q_text, a, b, c, d, correct))
                conn.commit()
                conn.close()
                st.success("✅ MCQ Saved")
        else:
            if st.button("Save Text Question"):
                conn = sqlite3.connect("school.db")
                cursor = conn.cursor()
                cursor.execute("INSERT INTO quiz_questions (quiz_id, question, is_multiple_choice) VALUES (?, ?, 0)",
                               (quiz_id, q_text))
                conn.commit()
                conn.close()
                st.success("✅ Text Question Saved")

    st.subheader("🧾 Daily Behavior Report")
    student = st.text_input("Student Name")
    subject = st.selectbox("Subject for Behavior", ["Math", "Science", "English"], key="beh_subj")
    report = st.text_area("Report")
    date = st.date_input("Date", value=datetime.date.today())
    if st.button("Save Behavior Report"):
        conn = sqlite3.connect("school.db")
        cursor = conn.cursor()
        cursor.execute("INSERT INTO daily_behavior_reports (student, subject, report, teacher, date) VALUES (?, ?, ?, ?, ?)",
                       (student, subject, report, username, str(date)))
        conn.commit()
        conn.close()
        st.success("✅ Behavior Report Saved")

# --- واجهة الطالب ---
if role == "student":
    st.header("🧑‍🎓 Student Panel")

    st.subheader("🧪 Take Quiz")
    conn = sqlite3.connect("school.db")
    cursor = conn.cursor()
    cursor.execute("SELECT id, title FROM quizzes")
    quiz_list = cursor.fetchall()
    quiz_dict = {title: qid for qid, title in quiz_list}
    quiz_choice = st.selectbox("Select Quiz", list(quiz_dict.keys()))
    selected_id = quiz_dict.get(quiz_choice)

    cursor.execute("SELECT id, question, option_a, option_b, option_c, option_d, correct_option, is_multiple_choice FROM quiz_questions WHERE quiz_id = ?", (selected_id,))
    questions = cursor.fetchall()
    conn.close()

    total_score = 0
    for qid, qtext, a, b, c, d, correct, is_mc in questions:
        st.markdown(f"**{qtext}**")
        if is_mc:
            ans = st.radio("Choose", ["A", "B", "C", "D"], key=qid)
            score = 1 if ans == correct else 0
        else:
            ans = st.text_area("Answer", key=qid)
            score = 0
        if st.button(f"Submit Q{qid}"):
            conn = sqlite3.connect("school.db")
            cursor = conn.cursor()
            cursor.execute("INSERT INTO quiz_answers (quiz_id, question_id, student, answer, score, answered_at) VALUES (?, ?, ?, ?, ?, ?)",
                           (selected_id, qid, username, ans, score, str(datetime.date.today())))
            conn.commit()
            conn.close()
            st.success("✅ Answer Submitted")
            if is_mc: total_score += score

    if total_score:
        st.success(f"Your Score: {total_score}")

# --- تحليل أداء الصف ---
st.header("📊 Class Performance")
conn = sqlite3.connect("school.db")
cursor = conn.cursor()
cursor.execute("SELECT student, COUNT(*) AS total_evaluations, ROUND(AVG(score), 2) AS avg_score FROM quiz_answers GROUP BY student")
grades_data = cursor.fetchall()
cursor.execute("SELECT student, COUNT(*) AS total_homework FROM assignment_uploads GROUP BY student")
homework_data = dict(cursor.fetchall())
conn.close()

df = pd.DataFrame(grades_data, columns=["Student", "Total Evaluations", "Average Score"])
df["Total Homework"] = df["Student"].map(homework_data).fillna(0).astype(int)
st.dataframe(df)
