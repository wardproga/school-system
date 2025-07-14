import streamlit as st
import pandas as pd

# إعداد الصفحة
st.set_page_config(page_title="📘 نظام إدارة المدرسة", layout="centered")

# ----------------------------
# تهيئة البيانات في session_state
if "students" not in st.session_state:
    st.session_state.students = pd.DataFrame(columns=["student_id", "name", "email"])

if "teachers" not in st.session_state:
    st.session_state.teachers = pd.DataFrame(columns=["teacher_id", "name", "email"])

if "grades" not in st.session_state:
    st.session_state.grades = pd.DataFrame(columns=["student", "subject", "grade", "term"])

# ----------------------------
# الشريط الجانبي للتنقل
st.sidebar.title("📘 القائمة")
page = st.sidebar.radio("انتقل إلى:", ["👨‍🎓 الطلاب", "👨‍🏫 المعلمون", "📝 العلامات"])

# ----------------------------
# 👨‍🎓 تبويب الطلاب
if page == "👨‍🎓 الطلاب":
    st.title("👨‍🎓 إدارة الطلاب")

    with st.form("student_form"):
        student_id = st.text_input("🔢 رقم الطالب")
        student_name = st.text_input("👤 اسم الطالب")
        student_email = st.text_input("📧 البريد الإلكتروني")

        submit_student = st.form_submit_button("📥 حفظ الطالب")
        if submit_student:
            if student_id and student_name and student_email:
                new_student = {"student_id": student_id, "name": student_name, "email": student_email}
                st.session_state.students = pd.concat(
                    [st.session_state.students, pd.DataFrame([new_student])],
                    ignore_index=True
                )
                st.success("✅ تم حفظ الطالب!")
            else:
                st.warning("⚠️ الرجاء تعبئة جميع الحقول.")

    st.subheader("📋 قائمة الطلاب")
    st.dataframe(st.session_state.students, use_container_width=True)

# ----------------------------
# 👨‍🏫 تبويب المعلمين
elif page == "👨‍🏫 المعلمون":
    st.title("👨‍🏫 إدارة المعلمين")

    with st.form("teacher_form"):
        teacher_id = st.text_input("🔢 رقم المعلم")
        teacher_name = st.text_input("👤 اسم المعلم")
        teacher_email = st.text_input("📧 البريد الإلكتروني")

        submit_teacher = st.form_submit_button("📥 حفظ المعلم")
        if submit_teacher:
            if teacher_id and teacher_name and teacher_email:
                new_teacher = {"teacher_id": teacher_id, "name": teacher_name, "email": teacher_email}
                st.session_state.teachers = pd.concat(
                    [st.session_state.teachers, pd.DataFrame([new_teacher])],
                    ignore_index=True
                )
                st.success("✅ تم حفظ المعلم!")
            else:
                st.warning("⚠️ الرجاء تعبئة جميع الحقول.")

    st.subheader("📋 قائمة المعلمين")
    st.dataframe(st.session_state.teachers, use_container_width=True)

# ----------------------------
# 📝 تبويب تسجيل العلامات
elif page == "📝 العلامات":
    st.title("📝 تسجيل العلامات")

    if st.session_state.students.empty:
        st.warning("⚠️ لا يوجد طلاب مسجلين بعد.")
    else:
        student_names = st.session_state.students["name"].tolist()

        with st.form("grade_form"):
            student = st.selectbox("👨‍🎓 اختر الطالب", student_names)
            subject = st.text_input("📚 اسم المادة")
            grade = st.number_input("💯 العلامة", min_value=0.0, max_value=100.0, step=0.5)
            term = st.selectbox("📆 الفصل الدراسي", ["الأول", "الثاني"])

            submit_grade = st.form_submit_button("📥 حفظ العلامة")
            if submit_grade:
                new_grade = {
                    "student": student,
                    "subject": subject,
                    "grade": grade,
                    "term": term
                }
                st.session_state.grades = pd.concat(
                    [st.session_state.grades, pd.DataFrame([new_grade])],
                    ignore_index=True
                )
                st.success("✅ تم تسجيل العلامة!")

        st.subheader("📊 جدول العلامات")
        st.dataframe(st.session_state.grades, use_container_width=True)
