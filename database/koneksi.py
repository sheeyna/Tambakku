from supabase import create_client, Client
from database.config import API_URL, API_KEY

def buat_koneksi() -> Client:
    """
    Membuat koneksi ke Supabase dan mengembalikan objek Client.
    """
    try:
        koneksi = create_client(API_URL, API_KEY)
        print("✅ Koneksi ke Supabase berhasil.")
        return koneksi
    except Exception as e:
        print("❌ Gagal membuat koneksi ke Supabase:", e)
        return None

if __name__ == "__main__":
    koneksi = buat_koneksi()
    if koneksi:
        hasil = koneksi.table("kolam").select("*").execute()
        print("Data kolam yang ada:")
        print(hasil.data)
