"""
Test Supabase response time
"""
import time
import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv('DATABASE_URL')

print("🔍 Testing Supabase Response Time...")
print("=" * 50)

# Test 5 queries
times = []
for i in range(5):
    start = time.time()
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        cursor.fetchone()
        cursor.close()
        conn.close()
        elapsed = (time.time() - start) * 1000  # Convert to ms
        times.append(elapsed)
        print(f"Query {i+1}: {elapsed:.2f}ms")
    except Exception as e:
        print(f"Query {i+1}: Error - {e}")

if times:
    avg = sum(times) / len(times)
    print("=" * 50)
    print(f"Average: {avg:.2f}ms")
    print("\n📊 Performance Rating:")
    if avg < 100:
        print("✅ Excellent - Very fast connection!")
    elif avg < 200:
        print("✅ Good - Normal cloud database speed")
    elif avg < 300:
        print("⚠️  Fair - Acceptable but could be better")
    else:
        print("❌ Slow - May want to check connection")
