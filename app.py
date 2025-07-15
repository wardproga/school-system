import streamlit as st import pandas as pd import sqlite3 import io from fpdf import FPDF

إعداد الاتصال بقاعدة البيانات

conn = sqlite3.connect("school.db", check_same_thread=False) cursor = conn.cursor()

def create_tables(): cursor.execute(""" CREATE TABLE IF NOT EXISTS students ( student_id TEXT PRIMARY KEY, name TEXT, email TEXT, class_name TEXT ) """) cursor.execute(""" CREATE TABLE IF NOT EXISTS teachers ( teacher_id TEXT PRIMARY KEY, name TEXT, subject TEXT ) """) cursor.execute(""" CREATE TABLE IF NOT EXISTS grades ( id INTEGER PRIMARY KEY AUTOINCREMENT, student_id TEXT, subject TEXT, grade REAL ) """) cursor.execute(""" CREATE TABLE IF NOT EXISTS classes ( class_id TEXT PRIMARY KEY, class_name TEXT, grade_level TEXT ) """) cursor.execute(""" CREATE TABLE IF NOT EXISTS timetable ( id INTEGER PRIMARY KEY AUTOINCREMENT, day TEXT, period TEXT, subject TEXT, class_name TEXT, teacher TEXT ) """) cursor.execute(""" CREATE TABLE IF NOT EXISTS parents ( parent_id TEXT PRIMARY KEY, name TEXT, email TEXT ) """) cursor.execute(""" CREATE TABLE IF NOT EXISTS parent_student ( parent_id TEXT, student_id TEXT, PRIMARY KEY (parent_id, student_id) ) """) conn.commit()

create_tables()

st.set_page_config(page_title="نظام إدارة المدرسة", layout="wide") st.sidebar.title("📚 قائمة الصفحات") page = st.sidebar.selectbox("اختر الصفحة", ["👨‍🎓 الطلاب", "👨‍🏫 المعلمون", "📝 العلامات", "📚 الصفوف", "📅 جدول الحصص", "👨‍👩‍👧‍👦 أولياء الأمور"])

---- دوال ----

def get_students(): return pd.read_sql_query("SELECT * FROM students", conn)

def add_student(student_id, name, email, class_name): cursor.execute("INSERT OR IGNORE INTO students (student_id, name, email, class_name) VALUES (?, ?, ?, ?)", (student_id, name, email, class_name)) conn.commit()

def get_teachers(): return pd.read_sql_query("SELECT * FROM teachers", conn)

def add_teacher(teacher_id, name, subject): cursor.execute("INSERT OR IGNORE INTO teachers (teacher_id, name, subject) VALUES (?, ?, ?)", (teacher_id, name, subject)) conn.commit()

def get_grades(): return pd.read_sql_query("SELECT * FROM grades", conn)

def add_grade(student_id, subject, grade): cursor.execute("INSERT INTO grades (student_id, subject, grade) VALUES (?, ?, ?)", (student_id, subject, grade)) conn.commit()

def get_classes(): return pd.read_sql_query("SELECT * FROM classes", conn)

def add_class(class_id, class_name, grade_level): cursor.execute("INSERT OR IGNORE INTO classes (class_id, class_name, grade_level) VALUES (?, ?, ?)", (class_id, class_name, grade_level)) conn.commit()

def get_timetable(): return pd.read_sql_query("SELECT * FROM timetable", conn)

def add_schedule(day, period, subject, class_name, teacher): cursor.execute("INSERT INTO timetable (day, period, subject, class_name, teacher) VALUES (?, ?, ?, ?, ?)", (day, period, subject, class_name, teacher)) conn.commit()

def get_parents(): return pd.read_sql_query("SELECT * FROM parents", conn)

def add_parent(parent_id, name, email): cursor.execute("INSERT OR IGNORE INTO parents (parent_id, name, email) VALUES (?, ?, ?)", (parent_id, name, email)) conn.commit()

def link_parent_student(parent_id, student_id): cursor.execute("INSERT OR IGNORE INTO parent_student (parent_id, student_id) VALUES (?, ?)", (parent_id, student_id)) conn.commit()

def get_children(parent_id): return pd.read_sql_query(f"SELECT s.* FROM students s JOIN parent_student ps ON s.student_id = ps.student_id WHERE ps.parent_id = '{parent_id}'", conn)

def get_student_grades(student_id): return pd.read_sql_query(f"SELECT * FROM grades WHERE student_id = '{student_id}'", conn)

---- صفحات ----

if page == "👨‍🎓 الطلاب": # الطلاب (كما هو سابقًا) pass

elif page == "👨‍🏫 المعلمون": # المعلمون (كما هو سابقًا) pass

elif page == "📝 العلامات": # العلامات (كما هو سابقًا) pass

elif page == "📚 الصفوف": # الصفوف (كما هو سابقًا) pass

elif page == "📅 جدول الحصص": # جدول الحصص (كما هو سابقًا) pass

elif page == "👨‍👩‍👧‍👦 أولياء الأمور": st.title("👨‍👩‍👧‍👦 إدارة أولياء الأمور")

with st.form("parent_form"):
    parent_id = st.text_input("🆔 رقم ولي الأمر")
    parent_name = st.text_input("👤 اسم ولي الأمر")
    parent_email = st.text_input("📧 البريد الإلكتروني")
    submit_parent = st.form_submit_button("📥 حفظ")

    if submit_parent and parent_id and parent_name:
        add_parent(parent_id, parent_name, parent_email)
        st.success("✅ تم حفظ ولي الأمر")

st.subheader("🔗 ربط ولي الأمر بطالب")
parents_df = get_parents()
students_df = get_students()
parent_list = parents_df["parent_id"].tolist()
student_list = students_df["student_id"].tolist()

with st.form("link_form"):
    selected_parent = st.selectbox("👨‍👩‍👧‍👦 اختر ولي أمر", parent_list)
    selected_student = st.selectbox("👨‍🎓 اختر طالب", student_list)
    submit_link = st.form_submit_button("🔗 ربط")

    if submit_link:
        link_parent_student(selected_parent, selected_student)
        st.success("✅ تم الربط")

st.subheader("📄 عرض معلومات ولي الأمر")
selected_parent_view = st.selectbox("👤 اختر ولي أمر لعرض أطفاله", parent_list)
children_df = get_children(selected_parent_view)
st.write("🧒 الأبناء المسجلون:")
st.dataframe(children_df)

for i, row in children_df.iterrows():
    st.markdown(f"### 📝 علامات الطالب: {row['name']}")
    student_grades = get_student_grades(row['student_id'])
    st.dataframe(student_grades)

