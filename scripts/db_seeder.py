"""DB Seeder: seed Angkot route JSON into Supabase"""

import json
import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.utils.db_connector import get_supabase_client

def seed_angkot_data():
    # 1. Panggil koneksi (Pinjam Kunci)
    try:
        supabase = get_supabase_client()
        print("Koneksi ke Supabase berhasil.")
    except Exception as e:
        print(e)
        return

    # 2. Lokasi file JSON hasil DeepSeek Anda
    json_path = "data/02_baseknowladge/angkot_routes.json" 
    
    if not os.path.exists(json_path):
        print(f"File tidak ditemukan di: {json_path}")
        return

    # 3. Baca JSON
    print(f"Membaca file: {json_path}")
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # 4. Upload ke Tabel
    print(f"Sedang mengupload {len(data)} rute...")
    try:
        # 'angkot_routes' adalah nama tabel yang Anda buat di SQL Editor sebelumnya
        response = supabase.table("angkot_routes").insert(data).execute()
        print("SUKSES! Data rute angkot sudah masuk ke database Cloud.")
    except Exception as e:
        print(f"Gagal upload: {e}")

if __name__ == "__main__":
    seed_angkot_data()