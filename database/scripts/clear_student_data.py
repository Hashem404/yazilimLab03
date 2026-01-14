#!/usr/bin/env python3
"""
Öğrenci Verilerini Temizleme Scripti

Bu script SADECE students ve student_courses tablolarındaki verileri temizler.
Diğer tablolardaki (faculties, departments, classrooms, lecturers, courses, users)
gerçek veriler korunur.

Kullanım:
    python database/scripts/clear_student_data.py
"""

import sys
import os

# Proje kök dizinini Python path'ine ekle
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from database.core.connection import get_connection, release_connection


def clear_student_data():
    """
    Students ve student_courses tablolarını temizler.
    CASCADE delete ile student_courses tablosu da otomatik temizlenir.
    """
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()

        # Önce kaç kayıt olduğunu kontrol et
        cursor.execute("SELECT COUNT(*) FROM students")
        students_count = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM student_courses")
        courses_count = cursor.fetchone()[0]

        print(f"=== Mevcut Durum ===")
        print(f"students tablosunda {students_count} kayıt var.")
        print(f"student_courses tablosunda {courses_count} kayıt var.")
        print()

        # Onay al
        if students_count > 0 or courses_count > 0:
            response = input("Bu tabloları temizlemek istediğinize emin misiniz? (e/h): ")
            if response.lower() not in ['e', 'evet', 'y', 'yes']:
                print("İptal edildi.")
                return

        print("\n=== Temizleme Başlıyor ===")

        # Önce student_courses tablosunu temizle
        cursor.execute("DELETE FROM student_courses")
        deleted_courses = cursor.rowcount
        print(f"✓ student_courses tablosundan {deleted_courses} kayıt silindi.")

        # Sonra students tablosunu temizle
        cursor.execute("DELETE FROM students")
        deleted_students = cursor.rowcount
        print(f"✓ students tablosundan {deleted_students} kayıt silindi.")

        # ID sequence'leri sıfırla
        cursor.execute("ALTER SEQUENCE students_id_seq RESTART WITH 1")
        print(f"✓ students_id_seq sequence sıfırlandı.")

        cursor.execute("ALTER SEQUENCE student_courses_id_seq RESTART WITH 1")
        print(f"✓ student_courses_id_seq sequence sıfırlandı.")

        conn.commit()

        print("\n=== İşlem Başarılı ===")
        print("Students ve student_courses tabloları temizlendi.")
        print("Diğer tablolar (faculties, departments, classrooms, lecturers, courses, users) korunmuştur.")

    except Exception as e:
        if conn:
            conn.rollback()
        print(f"\n❌ Hata: {str(e)}")
        raise
    finally:
        if conn:
            release_connection(conn)


def show_table_counts():
    """Tüm tablolardaki kayıt sayılarını göster"""
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()

        tables = [
            'faculties', 'departments', 'classrooms', 'lecturers',
            'courses', 'users', 'students', 'student_courses'
        ]

        print("\n=== Tüm Tablolardaki Kayıt Sayıları ===")
        for table in tables:
            try:
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                count = cursor.fetchone()[0]
                print(f"  {table:20} : {count}")
            except Exception as e:
                print(f"  {table:20} : Hata ({str(e)})")

    finally:
        if conn:
            release_connection(conn)


if __name__ == "__main__":
    print("=" * 50)
    print("Öğrenci Verisi Temizleme Scripti")
    print("=" * 50)
    print()

    # Önce mevcut durumu göster
    show_table_counts()
    print()

    # Temizleme işlemi
    clear_student_data()
    print()

    # Son durumu göster
    show_table_counts()
