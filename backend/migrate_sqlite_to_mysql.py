"""
Migrate data from SQLite to MySQL
"""
import sqlite3
import pymysql
from datetime import datetime

# Connect to SQLite
sqlite_conn = sqlite3.connect('instance/cineforge_ai_test.db')
sqlite_conn.row_factory = sqlite3.Row
sqlite_cursor = sqlite_conn.cursor()

# Connect to MySQL
mysql_conn = pymysql.connect(
    host='localhost',
    user='root',
    password='',
    database='cineforge_ai',
    charset='utf8mb4'
)
mysql_cursor = mysql_conn.cursor()

# Get all tables from SQLite
sqlite_cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = [row[0] for row in sqlite_cursor.fetchall()]

print(f"Found {len(tables)} tables in SQLite database")
print(f"Tables: {', '.join(tables)}")

migrated_count = 0

for table in tables:
    try:
        # Get data from SQLite
        sqlite_cursor.execute(f"SELECT * FROM {table}")
        rows = sqlite_cursor.fetchall()
        
        if not rows:
            print(f"  {table}: No data to migrate")
            continue
            
        # Get column names
        columns = [description[0] for description in sqlite_cursor.description]
        
        # Insert data into MySQL
        placeholders = ', '.join(['%s'] * len(columns))
        column_names = ', '.join(columns)
        insert_query = f"INSERT INTO {table} ({column_names}) VALUES ({placeholders})"
        
        for row in rows:
            try:
                mysql_cursor.execute(insert_query, tuple(row))
            except Exception as e:
                print(f"  Error inserting row into {table}: {e}")
        
        mysql_conn.commit()
        print(f"✓ {table}: Migrated {len(rows)} rows")
        migrated_count += len(rows)
        
    except Exception as e:
        print(f"✗ {table}: Error - {e}")

print(f"\nMigration complete! Total rows migrated: {migrated_count}")

# Close connections
sqlite_conn.close()
mysql_conn.close()
