import streamlit as st
import pandas as pd
from fpdf import FPDF
import io

# إعداد الصفحة
st.set_page_config(page_title="📊 نظام إدارة المدرسة", layout="wide")

# ---- تسجيل الدخول ----
def login():
    st.title("🔐 تسجيل الدخول")

    with st.form("login_form"):
        username = st.text_input("👤 اسم المستخدم")
        password = st.text_input("🔑 كلمة المرور", type="password")
        role = st.selectbox("🧾 اختر الدور", ["مدير", "معلم"])
        submit = st.form_submit_button("🔓 دخول")

        if submit:
            if (username == "admin" and password == "1234" and role == "مدير") or \
               (username == "teacher" and password == "0000" and role == "معلم"):
                st.session_state.logged_in = True
                st.session_state.role = role
                st.success(f"✅ تم تسجيل الدخول كـ {role}")
            else:
                st.error("❌ اسم المستخدم أو كلمة المرور غير صحيحة.")

# التحقق من حالة الجلسة
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "role" not in st.session_state:
    st.session_state.role = ""

if not st.session_state.logged_in:
    login()
    st.stop()

# ---- تهيئة البيانات ----
if "students" not in st.session_state:
    st.session_state.students = pd.DataFrame(columns=["student_id", "name", "email", "class_name"])
if "teachers" not in st.session_state:
    st.session_state.teachers = pd.DataFrame(columns=["teacher_id", "name", "subject"])
if "grades" not in st.session_state:
    st.session_state.grades = pd.DataFrame(columns=["student_id", "subject", "grade"])
if "classes" not in st.session_state:
    st.session_state.classes = pd.DataFrame(columns=["class_id", "class_name", "grade_level"])
if "timetable" not in st.session_state:
    st.session_state.timetable = pd.DataFrame(columns=["day", "period", "subject", "class_name", "teacher"])

# ---- اختيار الصفحة ----
if st.session_state.role == "مدير":
    page = st.sidebar.radio("📘 انتقل إلى:", ["👨‍🎓 الطلاب", "👨‍🏫 المعلمون", "📝 العلامات", "📚 الصفوف", "📅 جدول الحصص"])
else:
    page = st.sidebar.radio("📘 انتقل إلى:", ["📝 العلامات", "📅 جدول الحصص"])

# ---- 👨‍🎓 الطلاب ----
if page == "👨‍🎓 الطلاب":
    st.title("👨‍🎓 إدارة الطلاب")

    with st.form("student_form"):
        student_id = st.text_input("🆔 رقم الطالب")
        student_name = st.text_input("👤 اسم الطالب")
        student_email = st.text_input("📧 البريد الإلكتروني")
        class_options = st.session_state.classes["class_name"].tolist() if not st.session_state.classes.empty else []
        student_class = st.selectbox("📘 اختر الصف", class_options if class_options else ["لا توجد صفوف"])
        submit_student = st.form_submit_button("📥 حفظ الطالب")

        if submit_student and student_id and student_name:
            new_student = {"student_id": student_id, "name": student_name, "email": student_email, "class_name": student_class}
            st.session_state.students = pd.concat([st.session_state.students, pd.DataFrame([new_student])], ignore_index=True)
            st.success("✅ تم حفظ الطالب!")

    st.subheader("📋 قائمة الطلاب")
    st.dataframe(st.session_state.students, use_container_width=True)

    if not st.session_state.students.empty:
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

        pdf_bytes = generate_pdf(st.session_state.students)
        st.download_button("⬇️ تحميل معلومات الطلاب PDF", data=pdf_bytes, file_name="students_list.pdf", mime="application/pdf")

# ---- 👨‍🏫 المعلمون ----
elif page == "👨‍🏫 المعلمون":
    st.title("👨‍🏫 إدارة المعلمين")

    with st.form("teacher_form"):
        teacher_id = st.text_input("🆔 رقم المعلم")
        teacher_name = st.text_input("👨‍🏫 اسم المعلم")
        subject = st.text_input("📘 المادة")
        submit_teacher = st.form_submit_button("📥 حفظ المعلم")

        if submit_teacher and teacher_id and teacher_name:
            new_teacher = {"teacher_id": teacher_id, "name": teacher_name, "subject": subject}
            st.session_state.teachers = pd.concat([st.session_state.teachers, pd.DataFrame([new_teacher])], ignore_index=True)
            st.success("✅ تم حفظ المعلم!")

    st.subheader("📋 قائمة المعلمين")
    st.dataframe(st.session_state.teachers, use_container_width=True)

# ---- 📝 العلامات ----
elif page == "📝 العلامات":
    st.title("📝 تسجيل العلامات")

    with st.form("grades_form"):
        student_id = st.selectbox("👨‍🎓 اختر الطالب", st.session_state.students["student_id"] if not st.session_state.students.empty else [])
        subject = st.text_input("📘 المادة")
        grade = st.number_input("🔢 العلامة", min_value=0.0, max_value=100.0)
        submit_grade = st.form_submit_button("📥 حفظ العلامة")

        if submit_grade and student_id and subject:
            new_grade = {"student_id": student_id, "subject": subject, "grade": grade}
            st.session_state.grades = pd.concat([st.session_state.grades, pd.DataFrame([new_grade])], ignore_index=True)
            st.success("✅ تم حفظ العلامة!")

    st.subheader("📋 جدول العلامات")
    st.dataframe(st.session_state.grades, use_container_width=True)

    if not st.session_state.grades.empty:
        st.download_button(
            "⬇️ تحميل العلامات Excel",
            data=st.session_state.grades.to_excel(index=False, engine="openpyxl"),
            file_name="grades.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

# ---- 📚 الصفوف ----
elif page == "📚 الصفوف":
    st.title("📚 إدارة الصفوف")

    with st.form("class_form"):
        class_id = st.text_input("🆔 رقم الصف")
        class_name = st.text_input("🏷️ اسم الصف")
        grade_level = st.selectbox("📘 المرحلة", ["رياض أطفال", "ابتدائي", "إعدادي", "ثانوي"])
        submit_class = st.form_submit_button("📥 حفظ الصف")

        if submit_class and class_id and class_name:
            new_class = {"class_id": class_id, "class_name": class_name, "grade_level": grade_level}
            st.session_state.classes = pd.concat([st.session_state.classes, pd.DataFrame([new_class])], ignore_index=True)
            st.success("✅ تم حفظ الصف!")

    st.subheader("📋 قائمة الصفوف")
    st.dataframe(st.session_state.classes, use_container_width=True)

# ---- 📅 جدول الحصص ----
elif page == "📅 جدول الحصص":
    st.title("📅 إدارة جدول الحصص")

    with st.form("timetable_form"):
        day = st.selectbox("📆 اليوم", ["الأحد", "الاثنين", "الثلاثاء", "الأربعاء", "الخميس"])
        period = st.selectbox("⏰ الحصة", [f"الحصة {i}" for i in range(1, 9)])
        subject = st.text_input("📘 المادة")
        class_name = st.selectbox("🏷️ الصف", st.session_state.classes["class_name"] if not st.session_state.classes.empty else ["لا توجد"])
        teacher = st.selectbox("👨‍🏫 المعلم", st.session_state.teachers["name"] if not st.session_state.teachers.empty else ["لا يوجد"])
        submit_tt = st.form_submit_button("📥 حفظ الحصة")

        if submit_tt and subject:
            new_tt = {"day": day, "period": period, "subject": subject, "class_name": class_name, "teacher": teacher}
            st.session_state.timetable = pd.concat([st.session_state.timetable, pd.DataFrame([new_tt])], ignore_index=True)
            st.success("✅ تم حفظ الحصة!")

    st.subheader("📋 جدول الحصص")
    st.dataframe(st.session_state.timetable, use_container_width=True)

    if not st.session_state.timetable.empty:
        st.download_button(
            "⬇️ تحميل جدول الحصص Excel",
            data=st.session_state.timetable.to_excel(index=False, engine="openpyxl"),
            file_name="timetable.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
