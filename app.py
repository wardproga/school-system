import streamlit as st import pandas as pd import sqlite3 import io from fpdf import FPDF

إعداد الاتصال بقاعدة البيانات

conn = sqlite3.connect("school.db", check_same_thread=False) cursor = conn.cursor()

def create_tables(): cursor.execute(""" CREATE TABLE IF NOT EXISTS students ( student_id TEXT PRIMARY KEY, name TEXT, email TEXT, class_name TEXT ) """) cursor.execute(""" CREATE TABLE IF NOT EXISTS teachers ( teacher_id TEXT PRIMARY KEY, name TEXT, subject TEXT ) """) cursor.execute(""" CREATE TABLE IF NOT EXISTS grades ( id INTEGER PRIMARY KEY AUTOINCREMENT, student_id TEXT, subject TEXT, grade REAL ) """) cursor.execute(""" CREATE TABLE IF NOT EXISTS classes ( class_id TEXT PRIMARY KEY, class_name TEXT, grade_level TEXT ) """) cursor.execute(""" CREATE TABLE IF NOT EXISTS timetable ( id INTEGER PRIMARY KEY AUTOINCREMENT, day TEXT, period TEXT, subject TEXT, class_name TEXT, teacher TEXT ) """) conn.commit()

create_tables()

st.set_page_config(page_title="نظام إدارة المدرسة", layout="wide") st.sidebar.title("📚 قائمة الصفحات") page = st.sidebar.selectbox("اختر الصفحة", ["👨‍🎓 الطلاب", "👨‍🏫 المعلمون", "📝 العلامات", "📚 الصفوف", "📅 جدول الحصص"])

---- دوال الطلاب ----

def get_students(): return pd.read_sql_query("SELECT * FROM students", conn)

def add_student(student_id, name, email, class_name): cursor.execute( "INSERT OR IGNORE INTO students (student_id, name, email, class_name) VALUES (?, ?, ?, ?)", (student_id, name, email, class_name) ) conn.commit()

---- دوال المعلمين ----

def get_teachers(): return pd.read_sql_query("SELECT * FROM teachers", conn)

def add_teacher(teacher_id, name, subject): cursor.execute( "INSERT OR IGNORE INTO teachers (teacher_id, name, subject) VALUES (?, ?, ?)", (teacher_id, name, subject) ) conn.commit()

---- دوال العلامات ----

def get_grades(): return pd.read_sql_query("SELECT * FROM grades", conn)

def add_grade(student_id, subject, grade): cursor.execute( "INSERT INTO grades (student_id, subject, grade) VALUES (?, ?, ?)", (student_id, subject, grade) ) conn.commit()

---- دوال الصفوف ----

def get_classes(): return pd.read_sql_query("SELECT * FROM classes", conn)

def add_class(class_id, class_name, grade_level): cursor.execute( "INSERT OR IGNORE INTO classes (class_id, class_name, grade_level) VALUES (?, ?, ?)", (class_id, class_name, grade_level) ) conn.commit()

---- دوال جدول الحصص ----

def get_timetable(): return pd.read_sql_query("SELECT * FROM timetable", conn)

def add_schedule(day, period, subject, class_name, teacher): cursor.execute( "INSERT INTO timetable (day, period, subject, class_name, teacher) VALUES (?, ?, ?, ?, ?)", (day, period, subject, class_name, teacher) ) conn.commit()

---- 👨‍🎓 الطلاب ----

if page == "👨‍🎓 الطلاب": st.title("👨‍🎓 إدارة الطلاب")

with st.form("student_form"):
    student_id = st.text_input("🆔 رقم الطالب")
    student_name = st.text_input("👤 اسم الطالب")
    student_email = st.text_input("📧 البريد الإلكتروني")
    class_df = get_classes()
    class_options = class_df["class_name"].tolist() if not class_df.empty else []
    student_class = st.selectbox("📘 اختر الصف", class_options if class_options else ["لا توجد صفوف"])
    submit_student = st.form_submit_button("📥 حفظ الطالب")

    if submit_student and student_id and student_name:
        add_student(student_id, student_name, student_email, student_class)
        st.success("✅ تم حفظ الطالب!")

st.subheader("📋 قائمة الطلاب")
students_df = get_students()
st.dataframe(students_df, use_container_width=True)

if not students_df.empty:
    def generate_pdf(dataframe):
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        pdf.cell(200, 10, txt="قائمة الطلاب", ln=True, align="C")
        pdf.ln(10)
        pdf.multi_cell(0, 10, " | ".join(dataframe.columns.tolist()))
        for _, row in dataframe.iterrows():
            pdf.multi_cell(0, 10, " | ".join(str(val) for val in row.values))
        output = io.BytesIO()
        pdf.output(output)
        return output.getvalue()

    pdf_bytes = generate_pdf(students_df)
    st.download_button("⬇️ تحميل معلومات الطلاب PDF", data=pdf_bytes, file_name="students_list.pdf", mime="application/pdf")

---- 👨‍🏫 المعلمون ----

elif page == "👨‍🏫 المعلمون": st.title("👨‍🏫 إدارة المعلمين")

with st.form("teacher_form"):
    teacher_id = st.text_input("🆔 رقم المعلم")
    teacher_name = st.text_input("👤 اسم المعلم")
    teacher_subject = st.text_input("📘 المادة")
    submit_teacher = st.form_submit_button("📥 حفظ المعلم")

    if submit_teacher and teacher_id and teacher_name:
        add_teacher(teacher_id, teacher_name, teacher_subject)
        st.success("✅ تم حفظ المعلم!")

st.subheader("📋 قائمة المعلمين")
teachers_df = get_teachers()
st.dataframe(teachers_df, use_container_width=True)

---- 📝 العلامات ----

elif page == "📝 العلامات": st.title("📝 إدارة العلامات")

student_df = get_students()
student_ids = student_df["student_id"].tolist()

with st.form("grade_form"):
    student_id = st.selectbox("👤 اختر الطالب", student_ids)
    subject = st.text_input("📘 المادة")
    grade = st.number_input("🧮 العلامة", min_value=0.0, max_value=100.0, step=0.5)
    submit_grade = st.form_submit_button("📥 حفظ العلامة")

    if submit_grade and student_id and subject:
        add_grade(student_id, subject, grade)
        st.success("✅ تم حفظ العلامة!")

st.subheader("📊 جميع العلامات")
grades_df = get_grades()
st.dataframe(grades_df, use_container_width=True)

---- 📚 الصفوف ----

elif page == "📚 الصفوف": st.title("📚 إدارة الصفوف")

with st.form("class_form"):
    class_id = st.text_input("🆔 رقم الصف")
    class_name = st.text_input("📘 اسم الصف")
    grade_level = st.text_input("📏 المرحلة الدراسية")
    submit_class = st.form_submit_button("📥 حفظ الصف")

    if submit_class and class_id and class_name:
        add_class(class_id, class_name, grade_level)
        st.success("✅ تم حفظ الصف!")

st.subheader("📋 قائمة الصفوف")
classes_df = get_classes()
st.dataframe(classes_df, use_container_width=True)

---- 📅 جدول الحصص ----

elif page == "📅 جدول الحصص": st.title("📅 جدول الحصص")

class_df = get_classes()
class_names = class_df["class_name"].tolist()
teacher_df = get_teachers()
teacher_names = teacher_df["name"].tolist()

with st.form("timetable_form"):
    day = st.selectbox("🗓️ اليوم", ["الأحد", "الإثنين", "الثلاثاء", "الأربعاء", "الخميس"])
    period = st.selectbox("⏰ الحصة", [f"الحصة {i}" for i in range(1, 8)])
    subject = st.text_input("📘 المادة")
    class_name = st.selectbox("📚 الصف", class_names if class_names else ["لا توجد صفوف"])
    teacher = st.selectbox("👨‍🏫 المعلم", teacher_names if teacher_names else ["لا يوجد معلمين"])
    submit_tt = st.form_submit_button("📥 حفظ الجدول")

    if submit_tt:
        add_schedule(day, period, subject, class_name, teacher)
        st.success("✅ تم حفظ الجدول!")

st.subheader("📋 جدول الحصص")
timetable_df = get_timetable()
st.dataframe(timetable_df, use_container_width=True)

