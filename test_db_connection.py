import os
from supabase import create_client

# Replace these with your actual Supabase credentials
url = "https://nwwefvsfskixxwcpxixl.supabase.co"  # e.g., https://xxxxx.supabase.co
key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im53d2VmdnNmc2tpeHh3Y3B4aXhsIiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODI3MzA5MTQsImV4cCI6MjA5ODMwNjkxNH0.3935H4vkSOSOQ58pFZ4lrbJLWDeb3-6Uz7JfWlQ_t88"  # e.g., eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

client = create_client(url, key)

# Test connection
try:
    response = client.table('raw_reviews').select('count').execute()
    print(f"✅ Database connected successfully!")
    print(f"Reviews count: {response}")
except Exception as e:
    print(f"❌ Connection failed: {e}")