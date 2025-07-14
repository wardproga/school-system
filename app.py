import streamlit as st
import pandas as pd

# إعداد الصفحة
st.set_page_config(page_title="📘 نظام إدارة المدرسة", layout="centered")
st.title("🏫 نظام إدارة المدرسة")

# ----------------------------
# تخزين بيانات الطلاب مؤقتًا
if "students" not in st.session_state:
    st.session_state.students = pd.DataFrame(columns=["student_id", "name", "email"])

# تخزين بيانات المعلمين مؤقتًا
if "teachers" not in st.session_state:
    st.session_state.teachers = pd.DataFrame(columns=["teacher_id", "name", "email"])

# ----------------------------
# تبويبات رئيسية
tab1, tab2 = st.tabs(["👨‍🎓 الطلاب", "👨‍🏫 المعلمون"])

# ----------------------------
# واجهة الطلاب
with tab1:
    st.subheader("➕ إضافة طالب جديد")
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
# واجهة المعلمين
with tab2:
    st.subheader("➕ إضافة معلم جديد")
    with st.form("teacher_form"):
        teacher_id = st.text_input("🔢 رقم المعلم")
        teacher_name = st.text_input("👨‍🏫 اسم المعلم")
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
