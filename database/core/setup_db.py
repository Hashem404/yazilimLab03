import psycopg2
from psycopg2 import sql
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

DB_CONFIG = {
    "host": "localhost",
    "user": "postgres",
    "password": "123",
}

TARGET_DB_NAME = "universite_sinav_db"

def create_database_if_not_exists():
    conn = None
    try:
        conn = psycopg2.connect(**DB_CONFIG, database="postgres")
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cur = conn.cursor()

        cur.execute("SELECT 1 FROM pg_catalog.pg_database WHERE datname = %s", (TARGET_DB_NAME,))
        exists = cur.fetchone()

        if not exists:
            print(f"⚙️ '{TARGET_DB_NAME}' veritabanı bulunamadı, oluşturuluyor...")
            cur.execute(sql.SQL("CREATE DATABASE {}").format(
                sql.Identifier(TARGET_DB_NAME))
            )
            print(f"✅ '{TARGET_DB_NAME}' başarıyla oluşturuldu.")
        else:
            print(f"ℹ️ '{TARGET_DB_NAME}' zaten mevcut, tablo kurulumuna geçiliyor.")

        cur.close()
    except Exception as e:
        print(f"❌ Veritabanı oluşturulurken hata: {e}")
    finally:
        if conn is not None:
            conn.close()

def create_updated_at_trigger(cur):
    # Trigger fonksiyonunu oluştur
    cur.execute("""
        CREATE OR REPLACE FUNCTION update_updated_at_column()
        RETURNS TRIGGER AS $$
        BEGIN
            NEW.updated_at = CURRENT_TIMESTAMP;
            RETURN NEW;
        END;
        $$ language 'plpgsql';
    """)
    
    tables = ['faculties', 'departments', 'classrooms', 'lecturers', 'courses', 'exam_schedule', 'users', 'students', 'student_courses']
    
    for table in tables:
        # Önce trigger'ı drop et (varsa), sonra oluştur
        cur.execute(f"""
            DROP TRIGGER IF EXISTS update_{table}_updated_at ON {table};
        """)
        cur.execute(f"""
            CREATE TRIGGER update_{table}_updated_at
                BEFORE UPDATE ON {table}
                FOR EACH ROW
                EXECUTE FUNCTION update_updated_at_column();
        """)

def create_tables():
    conn = None
    commands = (
        """
        CREATE TABLE IF NOT EXISTS faculties (
            id SERIAL PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            code VARCHAR(20) UNIQUE,
            dean_name VARCHAR(100),
            is_active BOOLEAN DEFAULT TRUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS departments (
            id SERIAL PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            code VARCHAR(20) UNIQUE,
            faculty_id INTEGER REFERENCES faculties(id) ON DELETE CASCADE,
            head_name VARCHAR(100),
            is_active BOOLEAN DEFAULT TRUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS classrooms (
            id SERIAL PRIMARY KEY,
            name VARCHAR(50) NOT NULL,
            building VARCHAR(50) DEFAULT '',
            capacity INTEGER NOT NULL,
            floor INTEGER DEFAULT 0,
            exam_capacity INTEGER,
            has_projector BOOLEAN DEFAULT FALSE,
            has_computer BOOLEAN DEFAULT FALSE,
            is_active BOOLEAN DEFAULT TRUE,
            is_suitable BOOLEAN DEFAULT TRUE,
            room_type VARCHAR(20) DEFAULT 'STANDART' CHECK (room_type IN ('STANDART', 'LAB', 'OFIS', 'DEKANLIK', 'BILGISALONU', 'KONFERANS')),
            faculty_id INTEGER REFERENCES faculties(id) ON DELETE SET NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS lecturers (
            id SERIAL PRIMARY KEY,
            name VARCHAR(100),
            department_id INTEGER REFERENCES departments(id) ON DELETE SET NULL,
            first_name VARCHAR(50),
            last_name VARCHAR(50),
            title VARCHAR(50),
            email VARCHAR(100) UNIQUE,
            available_days TEXT[] DEFAULT '{Pazartesi,Salı,Çarşamba,Perşembe,Cuma}',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS courses (
            id SERIAL PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            lecturer_id INTEGER REFERENCES lecturers(id) ON DELETE SET NULL,
            student_count INTEGER NOT NULL,
            exam_duration INTEGER CHECK (exam_duration IN (30, 60, 90, 120)),
            exam_type VARCHAR(50),
            department_id INTEGER REFERENCES departments(id) ON DELETE SET NULL,
            code VARCHAR(20) UNIQUE,
            year INTEGER,
            semester INTEGER,
            period INTEGER,
            theory_hours INTEGER DEFAULT 0,
            lab_hours INTEGER DEFAULT 0,
            course_type VARCHAR(30) DEFAULT 'Zorunlu',
            description TEXT,
            lecturer_count INTEGER DEFAULT 1,
            has_exam BOOLEAN DEFAULT TRUE,
            credit INTEGER DEFAULT 3,
            required_room_type VARCHAR(20) DEFAULT 'ANY' CHECK (required_room_type IN ('STANDART', 'LAB', 'OFIS', 'DEKANLIK', 'BILGISALONU', 'KONFERANS', 'ANY')),
            is_active BOOLEAN DEFAULT TRUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS exam_schedule (
            id SERIAL PRIMARY KEY,
            course_id INTEGER REFERENCES courses(id) ON DELETE CASCADE,
            classroom_id INTEGER REFERENCES classrooms(id) ON DELETE CASCADE,
            exam_date DATE NOT NULL,
            start_time TIME NOT NULL,
            end_time TIME NOT NULL,
            exam_type VARCHAR(20) DEFAULT 'final',
            status VARCHAR(20) DEFAULT 'planned',
            notes TEXT,
            building VARCHAR(50),
            classroom_name VARCHAR(50),
            course_code VARCHAR(20),
            course_name VARCHAR(100),
            lecturer_name VARCHAR(100),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            CONSTRAINT unique_classroom_time UNIQUE (classroom_id, exam_date, start_time)
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            username VARCHAR(50) UNIQUE NOT NULL,
            password_hash VARCHAR(255) NOT NULL,
            email VARCHAR(100) UNIQUE,
            first_name VARCHAR(50),
            last_name VARCHAR(50),
            role VARCHAR(20) NOT NULL CHECK (role IN ('admin', 'bolum_yetkilisi', 'hoca', 'ogrenci', 'editor', 'viewer')),
            is_active BOOLEAN DEFAULT TRUE,
            last_login TIMESTAMP,
            department_id INTEGER REFERENCES departments(id) ON DELETE SET NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS students (
            id SERIAL PRIMARY KEY,
            student_number VARCHAR(20) UNIQUE NOT NULL,
            first_name VARCHAR(50) NOT NULL,
            last_name VARCHAR(50) NOT NULL,
            email VARCHAR(100),
            department_id INTEGER REFERENCES departments(id) ON DELETE SET NULL,
            year INTEGER NOT NULL DEFAULT 1,
            is_active BOOLEAN DEFAULT TRUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS student_courses (
            id SERIAL PRIMARY KEY,
            student_id INTEGER NOT NULL REFERENCES students(id) ON DELETE CASCADE,
            course_id INTEGER NOT NULL REFERENCES courses(id) ON DELETE CASCADE,
            semester VARCHAR(50),
            is_active BOOLEAN DEFAULT TRUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(student_id, course_id)
        )
        """
    )

    try:
        print(f"🔌 '{TARGET_DB_NAME}' veritabanına bağlanılıyor...")
        conn = psycopg2.connect(**DB_CONFIG, database=TARGET_DB_NAME)
        cur = conn.cursor()
        
        for command in commands:
            cur.execute(command)
        
        print("⚙️ updated_at trigger'ları oluşturuluyor...")
        create_updated_at_trigger(cur)
        
        print("📊 Performans için indeksler oluşturuluyor...")
        indexes = [
            "CREATE INDEX IF NOT EXISTS idx_faculties_code ON faculties(code)",
            "CREATE INDEX IF NOT EXISTS idx_departments_faculty_id ON departments(faculty_id)",
            "CREATE INDEX IF NOT EXISTS idx_classrooms_faculty_id ON classrooms(faculty_id)",
            "CREATE INDEX IF NOT EXISTS idx_classrooms_suitable ON classrooms(is_suitable)",
            "CREATE INDEX IF NOT EXISTS idx_lecturers_department_id ON lecturers(department_id)",
            "CREATE INDEX IF NOT EXISTS idx_lecturers_email ON lecturers(email)",
            "CREATE INDEX IF NOT EXISTS idx_courses_code ON courses(code)",
            "CREATE INDEX IF NOT EXISTS idx_courses_department_id ON courses(department_id)",
            "CREATE INDEX IF NOT EXISTS idx_courses_lecturer_id ON courses(lecturer_id)",
            "CREATE INDEX IF NOT EXISTS idx_courses_department_lecturer ON courses(department_id, lecturer_id)",
            "CREATE INDEX IF NOT EXISTS idx_exam_schedule_date ON exam_schedule(exam_date)",
            "CREATE INDEX IF NOT EXISTS idx_exam_schedule_course_id ON exam_schedule(course_id)",
            "CREATE INDEX IF NOT EXISTS idx_exam_schedule_classroom_id ON exam_schedule(classroom_id)",
            "CREATE INDEX IF NOT EXISTS idx_users_username ON users(username)",
            "CREATE INDEX IF NOT EXISTS idx_users_department_id ON users(department_id)",
            "CREATE INDEX IF NOT EXISTS idx_students_student_number ON students(student_number)",
            "CREATE INDEX IF NOT EXISTS idx_students_department_id ON students(department_id)",
            "CREATE INDEX IF NOT EXISTS idx_students_year ON students(year)",
            "CREATE INDEX IF NOT EXISTS idx_students_active ON students(is_active)",
            "CREATE INDEX IF NOT EXISTS idx_student_courses_student_id ON student_courses(student_id)",
            "CREATE INDEX IF NOT EXISTS idx_student_courses_course_id ON student_courses(course_id)",
            "CREATE INDEX IF NOT EXISTS idx_student_courses_active ON student_courses(is_active)"
        ]
        
        for index in indexes:
            cur.execute(index)
        
        cur.close()
        conn.commit()
        print("✅ Tüm tablolar, trigger'lar ve indeksler başarıyla oluşturuldu/kontrol edildi!")
        
    except (Exception, psycopg2.DatabaseError) as error:
        print(f"❌ Tablo oluşturulurken hata oluştu: {error}")
        if conn:
            conn.rollback()
    finally:
        if conn is not None:
            conn.close()
            print("🔒 Bağlantı kapatıldı.")

if __name__ == '__main__':
    create_database_if_not_exists()
    
    create_tables()