#!/usr/bin/env python3
"""
EasyEvents Server Runner
Starts Flask server and seeds test data
"""

import subprocess
import time
import os
import json
import http.client

os.chdir('c:\\Users\\halle\\Downloads\\EHH\\EesyEvents')

print("=" * 70)
print("STARTING EASYEVENTS")
print("=" * 70)

# הפעל Flask
print("\n[STARTING] Flask server...")
process = subprocess.Popen(
    ['python', 'backend/app.py'],
    stdout=subprocess.PIPE,
    stderr=subprocess.STDOUT,
    text=True
)

# חכה שה-server יתחיל
time.sleep(4)

# הוסף נתוני בדיקה
print("[SEEDING] Adding test venues...")
try:
    conn = http.client.HTTPConnection('localhost', 5000, timeout=5)
    conn.request('POST', '/api/dev/seed-venues', '')
    response = conn.getresponse()
    data = json.loads(response.read().decode('utf-8'))
    print(f"         Status: {response.status} - {data.get('message', '')}")
    conn.close()
except Exception as e:
    print(f"         ERROR: {str(e)}")

print("[SEEDING] Adding test suppliers...")
try:
    conn = http.client.HTTPConnection('localhost', 5000, timeout=5)
    conn.request('POST', '/api/dev/seed-suppliers', '')
    response = conn.getresponse()
    data = json.loads(response.read().decode('utf-8'))
    print(f"         Status: {response.status} - {data.get('message', '')}")
    conn.close()
except Exception as e:
    print(f"         ERROR: {str(e)}")

print("\n[CHECK] Database stats...")
try:
    conn = http.client.HTTPConnection('localhost', 5000, timeout=5)
    conn.request('GET', '/api/stats')
    response = conn.getresponse()
    data = json.loads(response.read().decode('utf-8'))
    stats = data.get('stats', {})
    print(f"         Venues: {stats.get('total_venues', 0)}")
    print(f"         Suppliers: {stats.get('total_suppliers', 0)}")
    print(f"         Users: {stats.get('total_users', 0)}")
    conn.close()
except Exception as e:
    print(f"         ERROR: {str(e)}")

print("\n" + "=" * 70)
print("SERVER IS RUNNING!")
print("=" * 70)
print("""
[OPEN BROWSER] http://localhost:5000

[TEST IT]
1. Click "תכנון אירוע" (Plan Event)
2. Fill the form
3. Click "שליחה" (Submit)
4. See venues + suppliers from database!

[KEEP RUNNING] Server is active in background
Press Ctrl+C to stop
""")

# Keep running
try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("\n[STOP] Shutting down...")
    process.terminate()
    process.wait()
    print("[STOP] Done!")
