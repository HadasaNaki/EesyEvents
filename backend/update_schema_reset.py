import sqlite3
import os

# Calculate DB path assuming this script is in backend/ and db is in database/
current_dir = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(current_dir, '..', 'database', 'easyevents.db')

# Validate path
if not os.path.exists(db_path):
    print(f"Error: Database not found at {db_path}")
    # Try alternate location if running from root without backend prefix? 
    # But __file__ handles that.
else:
    print(f"Connecting to: {db_path}")
    conn = sqlite3.connect(db_path)
    c = conn.cursor()

    try:
        c.execute("ALTER TABLE users ADD COLUMN reset_token TEXT")
        print("Success: Added reset_token column")
    except sqlite3.OperationalError as e:
        print(f"Info: reset_token column availability check: {e}")

    try:
        c.execute("ALTER TABLE users ADD COLUMN reset_token_expiry TIMESTAMP")
        print("Success: Added reset_token_expiry column")
    except sqlite3.OperationalError as e:
        print(f"Info: reset_token_expiry column availability check: {e}")

    conn.commit()
    conn.close()
