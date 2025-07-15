import sqlite3

# الاتصال أو إنشاء قاعدة بيانات
conn = sqlite3.connect("school.db")
cursor = conn.cursor()

# إنشاء جدول الطلاب
cursor.execute("""
CREATE TABLE IF NOT EXISTS students (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    gender TEXT,
    birth_date TEXT,
    class_name TEXT,
    parent_contact TEXT
)
""")

# إنشاء جدول المعلمين
cursor.execute("""
CREATE TABLE IF NOT EXISTS teachers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    subject TEXT
)
""")

# إنشاء جدول العلامات
cursor.execute("""
CREATE TABLE IF NOT EXISTS grades (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER,
    subject TEXT,
    grade REAL,
    FOREIGN KEY(student_id) REFERENCES students(id)
)
""")

# إنشاء جدول أولياء الأمور
cursor.execute("""
CREATE TABLE IF NOT EXISTS parents (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT
)
""")

# إنشاء جدول الربط بين أولياء الأمور والطلاب
cursor.execute("""
CREATE TABLE IF NOT EXISTS parent_student (
    parent_id INTEGER,
    student_id INTEGER,
    PRIMARY KEY (parent_id, student_id),
    FOREIGN KEY(parent_id) REFERENCES parents(id),
    FOREIGN KEY(student_id) REFERENCES students(id)
)
""")

# إنشاء جدول الصفوف
cursor.execute("""
CREATE TABLE IF NOT EXISTS classes (
    class_id TEXT PRIMARY KEY,
    class_name TEXT,
    grade_level TEXT
)
""")

# إنشاء جدول جدول الحصص
cursor.execute("""
CREATE TABLE IF NOT EXISTS timetable (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    day TEXT,
    period TEXT,
    subject TEXT,
    class_name TEXT,
    teacher TEXT
)
""")

conn.commit()
conn.close()

print("✅ تم إنشاء قاعدة البيانات بنجاح.")
