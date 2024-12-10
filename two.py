import mysql.connector
from datetime import datetime

# MySQL veritabanına bağlanmak için fonksiyon
def get_db_connection():
    return mysql.connector.connect(
        host='94.73.151.142',       # MySQL sunucu adresi
        user='u2056822_atolye',     # MySQL kullanıcı adı
        password='UfkTakimi@7803-',  # MySQL şifresi
        database='u2056822_atolye'  # Veritabanı adı
    )

# Kullanıcıları MySQL veritabanından çek
def get_users_from_db():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)  # dictionary=True ile her satır bir dict olarak gelir

    # Kullanıcıları sorgula
    cursor.execute("SELECT id, name, rfid, email, is_inside FROM usersatolye")
    users = cursor.fetchall()

    # Bağlantıyı kapat
    cursor.close()
    conn.close()

    return users

# Kullanıcının RFID'sini bul ve is_inside durumunu değiştir
def toggle_user_status(rfid):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # Kullanıcıyı sorgula
    cursor.execute("SELECT id, name, rfid, email, is_inside FROM usersatolye WHERE rfid = %s", (rfid,))
    user = cursor.fetchone()

    if user:
        # Kullanıcının is_inside durumunu tersine çevir
        new_status = not user["is_inside"]
        cursor.execute("""
            UPDATE usersatolye
            SET is_inside = %s
            WHERE rfid = %s
        """, (new_status, rfid))

        # Değişiklikleri kaydet
        conn.commit()

        # Kullanıcı bilgilerini güncelle
        user["is_inside"] = new_status
        cursor.close()
        conn.close()

        return user
    else:
        cursor.close()
        conn.close()
        return None

# Logları veritabanına yaz
def log_activity_to_db(user, action):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    status = "içeride" if user["is_inside"] else "dışarıda"

    # Veritabanı bağlantısını al
    conn = get_db_connection()
    cursor = conn.cursor()

    # Log verisini veritabanına ekle
    cursor.execute("""
        INSERT INTO logs (user_id, user_name, rfid, action, status, timestamp)
        VALUES (%s, %s, %s, %s, %s, %s)
    """, (user["id"], user["name"], user["rfid"], action, status, timestamp))

    # Değişiklikleri kaydet ve bağlantıyı kapat
    conn.commit()
    cursor.close()
    conn.close()
    

# Ana program
def main():
    print("RFID Giriş Sistemi\nÇıkmak için 'exit' yazabilirsiniz.")

    while True:
        rfid = input("RFID kodunu girin: ").strip()
        if rfid.lower() == "exit":
            break

        user = toggle_user_status(rfid)
        if user:
            action = "giriş yaptı" if user["is_inside"] else "çıkış yaptı"
            print(f"{user['name']} artık {action}.")
            
            # Aktiviteyi veritabanına kaydet
            log_activity_to_db(user, action)
        else:
            print("Bu RFID ile eşleşen bir kullanıcı bulunamadı.")

if _name_ == "_main_":
    main()