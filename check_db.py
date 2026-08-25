import sqlite3
conn = sqlite3.connect('Processed_Assets/my_rag_data.db')
cursor = conn.cursor()
cursor.execute('SELECT name FROM sqlite_master WHERE type="table"')
tables = cursor.fetchall()
print('Tables:', tables)
for table in tables:
    t = table[0]
    cursor.execute(f'SELECT COUNT(*) FROM {t}')
    count = cursor.fetchone()[0]
    print(f'{t}: {count} rows')
conn.close()