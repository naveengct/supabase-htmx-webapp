import os
from dotenv import load_dotenv
from supabase import create_client, Client as cl

dotenv_path = '.env'
load_dotenv(dotenv_path)


url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")
supabase: cl = create_client(url, key)
