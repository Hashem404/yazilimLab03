#!/usr/bin/env python3
"""
Varsayılan Kullanıcı Oluşturma Scripti

Bu script, sisteme giriş yapabilmeniz için varsayılan kullanıcılar oluşturur.
Tüm kullanıcıların varsayılan şifresi: admin123

Kullanım:
    python database/scripts/create_default_users.py
"""

import sys
import os

# Proje kök dizinini Python path'ine ekle
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from database.core.connection import get_connection, release_connection
import hashlib


def hash_password(password: str) -> str:
    """Şifreyi SHA256 ile hash'ler"""
    return hashlib.sha256(password.encode()).hexdigest()


def create_default_users():
    """Varsayılan kullanıcıları oluşturur"""
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()

        # Önce mevcut kullanıcıları kontrol et
        cursor.execute("SELECT username, role FROM users ORDER BY id")
        existing_users = cursor.fetchall()

        print("\n=== Mevcut Kullanıcılar ===")
        if existing_users:
            for username, role in existing_users:
                print(f"  - {username} ({role})")
        else:
            print("  (Kullanıcı bulunmuyor)")

        print("\n=== Varsayılan Kullanıcılar Oluşturuluyor ===")

        # Varsayılan kullanıcılar
        default_users = [
            {
                'username': 'admin',
                'password': 'admin123',
                'email': 'admin@universite.edu.tr',
                'first_name': 'Sistem',
                'last_name': 'Yöneticisi',
                'role': 'admin',
                'department_id': None
            },
            {
                'username': 'bolum_yetkilisi',
                'password': 'admin123',
                'email': 'yetkili@universite.edu.tr',
                'first_name': 'Bölüm',
                'last_name': 'Yetkilisi',
                'role': 'bolum_yetkilisi',
                'department_id': None  # İlk bölümü kullanacak
            },
            {
                'username': 'hoca',
                'password': 'admin123',
                'email': 'hoca@universite.edu.tr',
                'first_name': 'Öğretim',
                'last_name': 'Üyesi',
                'role': 'hoca',
                'department_id': None
            },
            {
                'username': 'ogrenci',
                'password': 'admin123',
                'email': 'ogrenci@universite.edu.tr',
                'first_name': 'Öğrenci',
                'last_name': 'Örnek',
                'role': 'ogrenci',
                'department_id': None
            },
            {
                'username': 'viewer',
                'password': 'admin123',
                'email': 'viewer@universite.edu.tr',
                'first_name': 'Sadece',
                'last_name': 'Görüntüleyen',
                'role': 'viewer',
                'department_id': None
            }
        ]

        # İlk bölüm ID'sini al (bolum_yetkilisi için)
        cursor.execute("SELECT id FROM departments LIMIT 1")
        result = cursor.fetchone()
        first_dept_id = result[0] if result else None

        created_count = 0
        skipped_count = 0

        for user_data in default_users:
            username = user_data['username']

            # Kullanıcı zaten var mı kontrol et
            cursor.execute("SELECT id FROM users WHERE username = %s", (username,))
            if cursor.fetchone():
                print(f"  ⊘ {username} - zaten mevcut, atlanıyor")
                skipped_count += 1
                continue

            # department_id ayarla
            if user_data['role'] == 'bolum_yetkilisi' and first_dept_id:
                user_data['department_id'] = first_dept_id

            # Şifreyi hash'le
            password_hash = hash_password(user_data['password'])

            # Kullanıcıyı oluştur
            cursor.execute("""
                INSERT INTO users (username, password_hash, email, first_name, last_name, role, department_id, is_active)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING id
            """, (
                user_data['username'],
                password_hash,
                user_data['email'],
                user_data['first_name'],
                user_data['last_name'],
                user_data['role'],
                user_data['department_id'],
                True
            ))

            user_id = cursor.fetchone()[0]
            print(f"  ✓ {username} - oluşturuldu (ID: {user_id})")
            created_count += 1

        conn.commit()

        print(f"\n=== İşlem Tamamlandı ===")
        print(f"Oluşturulan: {created_count} kullanıcı")
        print(f"Atlanan: {skipped_count} kullanıcı (zaten mevcut)")
        print("\n=== Varsayılan Giriş Bilgileri ===")
        print("Tüm kullanıcıların şifresi: admin123")
        print("\nKullanıcılar:")
        for user in default_users:
            print(f"  • {user['username']:15} - {user['role']:20} - {user['password']}")

        print("\n⚠️  Güvenlik Uyarısı: Şifreleri production ortamında değiştirin!")
        print("   Şifre değiştirmek için uygulamadaki profil ayarlarını kullanın.")

    except Exception as e:
        if conn:
            conn.rollback()
        print(f"\n❌ Hata: {str(e)}")
        raise
    finally:
        if conn:
            release_connection(conn)


def show_login_info():
    """Giriş bilgilerini göster"""
    print("\n" + "=" * 60)
    print("GİRİŞ BİLGİLERİ")
    print("=" * 60)
    print("\nUygulamayı başlatmak için:")
    print("  python src/main.py")
    print("\nVarsayılan kullanıcılar (Şifre: admin123):")
    print("  admin           - Tam yetkili yönetici")
    print("  bolum_yetkilisi - Bölüm yetkilisi")
    print("  hoca            - Öğretim üyesi")
    print("  ogrenci         - Öğrenci")
    print("  viewer          - Sadece görüntüleme")
    print("=" * 60)


if __name__ == "__main__":
    print("=" * 60)
    print("Varsayılan Kullanıcı Oluşturma Scripti")
    print("=" * 60)

    create_default_users()
    show_login_info()
