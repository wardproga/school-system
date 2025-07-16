import streamlit as st
import sqlite3
import pandas as pd
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import io
import base64
from datetime import datetime

# الاتصال بقاعدة البيانات
conn = sqlite3.connect("school.db")
cursor = conn.cursor()

# إعداد الصفحة
st.set_page_config(page_title="نظام إدارة المدرسة", page_icon="🏫", layout="wide")

# --- واجهة ترحيبية وشريط تنقل علوي ---
st.markdown(
    """
    <style>
    .main-title {
        font-size: 38px;
        color: #0e4b75;
        font-weight: bold;
        text-align: center;
        margin-bottom: 15px;
    }
    .nav-bar {
        display: flex;
        justify-content: center;
        margin-bottom: 25px;
        gap: 20px;
    }
    .nav-button {
        background-color: #0e4b75;
        color: white;
        padding: 8px 20px;
        border-radius: 8px;
        text-decoration: none;
        font-weight: bold;
    }
    .nav-button:hover {
        background-color: #1267a0;
    }
    </style>

    <div class="main-title">📘 نظام إدارة المدرسة</div>
    <div class="nav-bar">
        <a href="#📥-إضافة-طالب" class="nav-button">الطلاب</a>
        <a href="#👩‍🏫-إدارة-المعلمين" class="nav-button">المعلمون</a>
        <a href="#📊-إدارة-العلامات" class="nav-button">العلامات</a>
        <a href="#🗓️-جدول-الحصص" class="nav-button">الحصص</a>
        <a href="#✉️-إرسال-إشعار" class="nav-button">الإشعارات</a>
        <a href="#📤-تحميل-التقارير" class="nav-button">التقارير</a>
        <a href="#ℹ️-حول" class="nav-button">حول</a>
    </div>
    """,
    unsafe_allow_html=True
)

# التحقق من الدخول
cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    password TEXT NOT NULL
)
""")
cursor.execute("INSERT OR IGNORE INTO users (username, password) VALUES (?, ?)", ("admin", "admin123"))
conn.commit()

if "logged_in" not in st.session_state:
    st.title("🔐 تسجيل الدخول")
    username = st.text_input("اسم المستخدم")
    password = st.text_input("كلمة المرور", type="password")
    if st.button("تسجيل الدخول"):
        cursor.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password))
        user = cursor.fetchone()
        if user:
            st.session_state.logged_in = True
            st.experimental_rerun()
        else:
            st.error("❌ اسم المستخدم أو كلمة المرور غير صحيحة")
    st.stop()

# --- إضافة طالب ---
with st.expander("📥 إضافة طالب"):
    name = st.text_input("اسم الطالب")
    gender = st.selectbox("الجنس", ["ذكر", "أنثى"])
    birth_date = st.date_input("تاريخ الميلاد")
    class_name = st.text_input("الصف")
    parent_contact = st.text_input("بريد ولي الأمر")
    if st.button("📥 إضافة الطالب"):
        cursor.execute("INSERT INTO students (name, gender, birth_date, class_name, parent_contact) VALUES (?, ?, ?, ?, ?)",
                       (name, gender, birth_date.strftime("%Y-%m-%d"), class_name, parent_contact))
        conn.commit()
        st.success("✅ تم الإضافة")

# --- إدارة المعلمين ---
with st.expander("👩‍🏫 إدارة المعلمين"):
    teacher_name = st.text_input("اسم المعلم")
    subject = st.text_input("المادة الدراسية")
    if st.button("➕ إضافة معلم"):
        cursor.execute("INSERT INTO teachers (name, subject) VALUES (?, ?)", (teacher_name, subject))
        conn.commit()
        st.success("✅ تم إضافة المعلم")
    teachers_df = pd.read_sql("SELECT * FROM teachers", conn)
    st.dataframe(teachers_df, use_container_width=True)

# --- إدارة العلامات ---
with st.expander("📊 إدارة العلامات"):
    students = pd.read_sql("SELECT id, name FROM students", conn)
    subjects = ["رياضيات", "علوم", "لغة عربية", "لغة إنجليزية"]
    student_selected = st.selectbox("اختر الطالب", students["name"])
    subject = st.selectbox("اختر المادة", subjects)
    grade = st.number_input("أدخل العلامة", min_value=0.0, max_value=100.0)
    student_id = students[students["name"] == student_selected]["id"].values[0]
    if st.button("➕ حفظ العلامة"):
        cursor.execute("INSERT INTO grades (student_id, subject, grade) VALUES (?, ?, ?)", (student_id, subject, grade))
        conn.commit()
        st.success("✅ تم حفظ العلامة")
    df_grades = pd.read_sql("SELECT * FROM grades", conn)
    st.dataframe(df_grades)

# --- إدارة جدول الحصص ---
with st.expander("🗓️ جدول الحصص"):
    class_name = st.text_input("الصف الدراسي")
    day = st.selectbox("اليوم", ["الأحد", "الاثنين", "الثلاثاء", "الأربعاء", "الخميس"])
    subject = st.text_input("المادة")
    time = st.text_input("الوقت (مثال: 09:00-10:00)")
    if st.button("➕ إضافة الحصة"):
        cursor.execute("INSERT INTO timetable (class_id, day, subject, time) VALUES ((SELECT id FROM classes WHERE class_name = ?), ?, ?, ?)", (class_name, day, subject, time))
        conn.commit()
        st.success("✅ تم إضافة الحصة")
    timetable_df = pd.read_sql("SELECT * FROM timetable", conn)
    st.dataframe(timetable_df)

# --- تحميل التقارير ---
with st.expander("📤 تحميل التقارير"):
    df = pd.read_sql("SELECT * FROM students", conn)
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()
    href = f'<a href="data:file/csv;base64,{b64}" download="students_{datetime.today().date()}.csv">📥 تحميل تقرير الطلاب بصيغة CSV</a>'
    st.markdown(href, unsafe_allow_html=True)

# --- إرسال إشعار بالبريد ---
with st.expander("✉️ إرسال إشعار"):
    students_df = pd.read_sql("SELECT name, parent_contact FROM students", conn)
    selected_student = st.selectbox("اختر الطالب", students_df["name"])
    parent_email = students_df[students_df["name"] == selected_student]["parent_contact"].values[0]
    subject = st.text_input("الموضوع")
    message = st.text_area("محتوى الرسالة")
    sender_email = st.text_input("بريد المُرسل (Gmail)")
    sender_pass = st.text_input("كلمة المرور أو App Password", type="password")
    if st.button("📤 إرسال الإشعار"):
        try:
            msg = MIMEMultipart()
            msg["From"] = sender_email
            msg["To"] = parent_email
            msg["Subject"] = subject
            msg.attach(MIMEText(message, "plain"))
            server = smtplib.SMTP("smtp.gmail.com", 587)
            server.starttls()
            server.login(sender_email, sender_pass)
            server.sendmail(sender_email, parent_email, msg.as_string())
            server.quit()
            st.success("✅ تم إرسال الإشعار")
        except Exception as e:
            st.error(f"❌ خطأ: {e}")

# --- صفحة حول النظام ---
with st.expander("ℹ️ حول"):
    st.markdown("""
    **📘 نظام إدارة المدرسة** هو نظام تفاعلي تم تطويره باستخدام Streamlit وSQLite.
    - يدعم إدارة الطلاب والمعلمين والمواد.
    - إرسال الإشعارات لأولياء الأمور.
    - تحميل التقارير وتحليل البيانات.
    - تصميم متجاوب لجميع الشاشات.

    تم تطويره بواسطة: `معاذ محمود` 🧑‍💻
    """)

conn.close()
