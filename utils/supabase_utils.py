from supabase import create_client
import os
import requests

from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_KEY")  # service key required for storage access

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def get_document_record(chapter_name: str):
    chapter_name = chapter_name.strip()

    # response = supabase.table("documents").select("*").eq("chapter_name", chapter_name).execute()
    response = supabase.table("documents").select("*").ilike("chapter_name", chapter_name).execute()

    if response.data and len(response.data) > 0:
        return response.data[0]
    all_chapters = supabase.table("documents").select("chapter_name").execute()
    print("Available chapters in Supabase DB:", [c['chapter_name'] for c in all_chapters.data])
    return None

def download_pdf_from_supabase(bucket_name: str, file_name: str, local_path: str) -> bool:
    try:
        res = supabase.storage.from_(bucket_name).download(file_name)
        os.makedirs(os.path.dirname(local_path), exist_ok=True)
        with open(local_path, "wb") as f:
            f.write(res)
        return True
    except Exception as e:
        print(f"Download error: {e}")
        return False
