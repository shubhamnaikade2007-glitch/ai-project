"""
HealthFit AI - MySQL Connection Test
Run with: python test_mysql.py
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from dotenv import load_dotenv
load_dotenv()

from app.config_mysql import test_connection, ensure_database_exists

print("\n=== HealthFit AI - MySQL Connection Test ===\n")

result = test_connection()

if result['success']:
    print(f"✅ Connection SUCCESSFUL")
    print(f"   MySQL Version : {result['version']}")
    print(f"   Database      : {result['database']}")
    print(f"   Host          : {result['host']}")
else:
    print(f"❌ Connection FAILED")
    print(f"   Error: {result['error']}")
    print("\n📋 Troubleshooting:")
    print("   1. Make sure MySQL is running")
    print("   2. Check MYSQL_PASSWORD in your .env file")
    print("   3. Default password is: root123")
    print("   4. Run: mysql -u root -proot123 -e 'SELECT 1'")
    sys.exit(1)

print("\n=== Table Check ===\n")
import pymysql
from app.config_mysql import MYSQL_CONFIG

conn = pymysql.connect(**MYSQL_CONFIG)
with conn.cursor() as cursor:
    cursor.execute("SHOW TABLES")
    tables = [row['Tables_in_healthfit_db'] for row in cursor.fetchall()]

if tables:
    print(f"✅ Found {len(tables)} tables:")
    for t in tables:
        cursor = conn.cursor()
        cursor.execute(f"SELECT COUNT(*) as cnt FROM {t}")
        row = cursor.fetchone()
        count = row['cnt'] if row else 0
        print(f"   • {t:<30} {count} rows")
else:
    print("⚠️  No tables found. Run the schema:")
    print("   mysql -u root -proot123 < database/mysql/schema.sql")
    print("   mysql -u root -proot123 < database/mysql/sample_data.sql")

conn.close()
print("\n✅ Test complete!\n")
