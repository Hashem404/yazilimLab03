"""
Veritabanını tamamen silip yeniden oluşturur.
DİKKAT: Mevcut tüm veriler silinecektir!
"""
import psycopg2
from psycopg2 import sql
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

DB_CONFIG = {
    "host": "localhost",
    "user": "postgres",
    "password": "123",
}

TARGET_DB_NAME = "universite_sinav_db"

def recreate_database():
    """Veritabanını silip yeniden oluşturur"""
    conn = None
    try:
        conn = psycopg2.connect(**DB_CONFIG, database="postgres")
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cur = conn.cursor()

        # Önce mevcut bağlantıları sonlandır
        cur.execute(f"""
            SELECT pg_terminate_backend(pid)
            FROM pg_stat_activity
            WHERE datname = '{TARGET_DB_NAME}'
            AND pid <> pg_backend_pid();
        """)

        # Veritabanını sil
        cur.execute(f"DROP DATABASE IF EXISTS {TARGET_DB_NAME}")
        print(f"🗑️ '{TARGET_DB_NAME}' veritabanı silindi.")

        # Yeniden oluştur
        cur.execute(sql.SQL("CREATE DATABASE {}").format(
            sql.Identifier(TARGET_DB_NAME))
        )
        print(f"✅ '{TARGET_DB_NAME}' başarıyla yeniden oluşturuldu.")

        cur.close()
    except Exception as e:
        print(f"❌ Veritabanı silinirken hata: {e}")
    finally:
        if conn is not None:
            conn.close()

if __name__ == '__main__':
    print("=" * 60)
    print("⚠️ UYARI: Veritabanı tamamen silinecek ve yeniden oluşturulacak!")
    print("=" * 60)
    
    onay = input("Devam etmek istiyor musunuz? (e/h): ")
    if onay.lower() == 'e':
        recreate_database()
        print("\nŞimdi 'python database/core/setup_db.py' komutunu çalıştırın.")
    else:
        print("İptal edildi.")
