"""Supabase connector: reusable function to get Supabase client instance"""

from supabase import create_client, Client
import os
from dotenv import load_dotenv

load_dotenv()

def get_supabase_client() -> Client:
    """
    Fungsi reusable untuk membuat koneksi ke Supabase.
    Script manapun yang butuh akses DB, tinggal panggil fungsi ini.
    """
    url: str = os.environ.get("SUPABASE_URL")
    key: str = os.environ.get("SUPABASE_KEY")

    if not url or not key:
        raise ValueError("Error: SUPABASE_URL or SUPABASE_KEY has not been filled in the .env file")

    return create_client(url, key)
