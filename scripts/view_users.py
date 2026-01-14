"""
Script to view all users in the database
"""
import sqlite3

conn = sqlite3.connect('easyevents.db')
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

users = cursor.execute('SELECT * FROM users').fetchall()

print(f"\n📊 Total Users: {len(users)}\n")
print("="*80)

for user in users:
    print(f"ID: {user['id']}")
    print(f"Name: {user['first_name']} {user['last_name']}")
    print(f"Email: {user['email']}")
    print(f"Phone: {user['phone']}")
    print(f"Created: {user['created_at']}")
    print(f"Newsletter: {'Yes' if user['newsletter'] else 'No'}")
    print("-"*80)

conn.close()
