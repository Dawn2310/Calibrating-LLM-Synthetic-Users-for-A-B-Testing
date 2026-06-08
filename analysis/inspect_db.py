import sqlite3
import pandas as pd

conn = sqlite3.connect('data/experiment.db')
cursor = conn.cursor()
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = [row[0] for row in cursor.fetchall()]
print('Tables:', tables)
for t in tables:
    try:
        df = pd.read_sql_query(f'SELECT * FROM {t} LIMIT 1', conn)
        print(f'\nTable {t} columns:', df.columns.tolist())
    except Exception as e:
        print(e)
