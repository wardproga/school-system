
import streamlit as st
import pandas as pd
import sqlite3
import matplotlib.pyplot as plt
import smtplib
from email.mime.text import MIMEText

# إعداد الصفحة
st.set_page_config(page_title="نظام إدارة المدرسة", layout="centered")

# الاتصال بقاعدة البيانات
def get_connection():
    return sqlite3.connect("school.db")

# تسجيل الدخول
def login():
    st.sidebar.header("🔐 تسجيل الدخول")
    email = st.sidebar.text_input("📧 البريد الإلكتروني")
    password = st.sidebar.text_input("🔑 كلمة المرور", type="password")
    if st.sidebar.button("تسجيل الدخول"):
        conn = get_connection()
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE email=? AND password=?", (email, password))
        user = c.fetchone()
        conn.close()
        if user:
            st.session_state.logged_in = True
            st.session_state.user_type = user[3]
            st.success("تم تسجيل الدخول بنجاح")
        else:
            st.error("بيانات الدخول غير صحيحة")

# صفحة المعلم
def teacher_page():
    st.title("👨‍🏫 صفحة المعلم")

    st.subheader("✉️ إرسال إشعار لولي الأمر")
    recipient = st.text_input("📩 بريد ولي الأمر")
    message = st.text_area("💬 نص الرسالة")
    if st.button("إرسال البريد"):
        try:
            send_email(recipient, message)
            st.success("تم إرسال البريد بنجاح")
        except Exception as e:
            st.error(f"فشل الإرسال: {e}")

# إرسال البريد
def send_email(to_email, content):
    from_email = st.secrets["EMAIL"]
    password = st.secrets["PASSWORD"]
    msg = MIMEText(content)
    msg["Subject"] = "📣 إشعار من المدرسة"
    msg["From"] = from_email
    msg["To"] = to_email

    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.starttls()
    server.login(from_email, password)
    server.send_message(msg)
    server.quit()

# لوحة التحكم
def dashboard_page():
    st.title("📊 لوحة التحكم الإحصائية")

    conn = get_connection()
    c = conn.cursor()

    c.execute("SELECT COUNT(*) FROM students")
    student_count = c.fetchone()[0]

    c.execute("SELECT COUNT(*) FROM teachers")
    teacher_count = c.fetchone()[0]

    c.execute("SELECT COUNT(DISTINCT class) FROM students")
    class_count = c.fetchone()[0]

    c.execute("SELECT AVG(grade) FROM grades")
    avg_grade = c.fetchone()[0]

    c.execute("SELECT COUNT(*) FROM attendance WHERE status = 'غائب'")
    absence_count = c.fetchone()[0]

    st.metric("👩‍🎓 عدد الطلاب", student_count)
    st.metric("👨‍🏫 عدد المعلمين", teacher_count)
    st.metric("🏫 عدد الصفوف", class_count)
    st.metric("📈 معدل العلامات", round(avg_grade if avg_grade else 0, 2))
    st.metric("🚫 عدد الغيابات", absence_count)

    st.markdown("---")

    attendance_df = pd.read_sql_query("SELECT status, COUNT(*) as count FROM attendance GROUP BY status", conn)
    participation_df = pd.read_sql_query("SELECT level, COUNT(*) as count FROM participation GROUP BY level", conn)

    fig1, ax1 = plt.subplots()
    ax1.pie(attendance_df['count'], labels=attendance_df['status'], autopct='%1.1f%%')
    ax1.set_title("نسبة الحضور")

    fig2, ax2 = plt.subplots()
    ax2.bar(participation_df['level'], participation_df['count'])
    ax2.set_title("مستويات المشاركة")
    ax2.set_ylabel("عدد الطلاب")

    st.pyplot(fig1)
    st.pyplot(fig2)

    conn.close()

# بدء التطبيق
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    login()
else:
    st.sidebar.success("✅ تم تسجيل الدخول")
    menu = st.sidebar.radio("اختر الصفحة", ["📊 لوحة التحكم", "👨‍🏫 المعلم"])
    if menu == "📊 لوحة التحكم":
        dashboard_page()
    elif menu == "👨‍🏫 المعلم":
        teacher_page()
