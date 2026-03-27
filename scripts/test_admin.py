import sys
import os
sys.path.insert(0, 'backend/flask-backend')
os.chdir('backend/flask-backend')

from dotenv import load_dotenv
load_dotenv()

from app.config_mysql import MYSQL_CONFIG
import pymysql

conn = pymysql.connect(**MYSQL_CONFIG)
cursor = conn.cursor(pymysql.cursors.DictCursor)
cursor.execute("SELECT id, email, password_hash FROM users WHERE email = 'admin@healthfit.com'")
user = cursor.fetchone()
if user:
    print(f"Admin: {user['email']}")
    print(f"Hash: {user['password_hash'][:20]}...")
else:
    print("No admin")

conn.close()

