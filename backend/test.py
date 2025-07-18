import sqlite3

db = "backend/fantasy_board.db"

conn = sqlite3.connect(db)
conn.row_factory = sqlite3.Row 
cursor = conn.cursor()

cursor.execute("SELECT * FROM images ORDER BY RANDOM() LIMIT 1;")

random_item = cursor.fetchone()

if random_item:
    print("✅ Successfully fetched a random item:")
    for key in random_item.keys():
        print(f"  - {key}: {random_item[key]}")
else:
    print("❌ The 'images' table appears to be empty.")

conn.close()