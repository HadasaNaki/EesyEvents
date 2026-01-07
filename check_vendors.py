import sqlite3

conn = sqlite3.connect('database/easyevents.db')
cursor = conn.cursor()

# Check event_vendors table
cursor.execute('SELECT COUNT(*) FROM event_vendors')
count = cursor.fetchone()[0]
print(f'מספר שורות ב-event_vendors: {count}')

if count > 0:
    cursor.execute('SELECT * FROM event_vendors LIMIT 5')
    print('\nדוגמאות ספקים:')
    for row in cursor.fetchall():
        print(f'  ID: {row[0]}, Event: {row[1]}, Type: {row[2]}, VendorID: {row[3]}')
        print(f'  Name: {row[4]}, Price: {row[5]}, Created: {row[6]}')
        print('  ---')
else:
    print('אין ספקים באירועים!')

# Check events table
cursor.execute('SELECT id, user_id, event_type FROM events')
events = cursor.fetchall()
print(f'\nמספר אירועים: {len(events)}')
for event in events:
    print(f'  Event ID: {event[0]}, User: {event[1]}, Type: {event[2]}')

conn.close()
