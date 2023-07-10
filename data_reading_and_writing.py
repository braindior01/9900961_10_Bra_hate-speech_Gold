import sqlite3

conn = sqlite3.connect('data/tmp.db', check_same_thread=False)

# *********************************************
# langkah awal import library sqlite, kemudian membuat data tmp.db dalam folder data

def create_table():
    conn.execute("""CREATE TABLE IF NOT EXISTS tweet_cleaning (id INTEGER PRIMARY KEY AUTOINCREMENT, previous_text char(1000), cleaned_text char(1000))""")
    conn.commit()

# *********************************************
# langkah selanjutnya membuat table dalam database untuk dapat di isi oleh data dari API

def insert_to_table(value_1, value_2):
    value_1 = value_1.encode('utf-8')
    value_2 = value_2.encode('utf-8')
    query = f"INSERT INTO tweet_cleaning (previous_text,cleaned_text) VALUES (?, ?);"
    cursors = conn.execute(query, (value_1, value_2))
    conn.commit()

# *********************************************
# langkah selanjutnya adalah membuat function insert to table hasil dari input text atau file oleh user dalam API

def read_table(target_index=None, target_keywords=None):
    if target_index == None and target_keywords is None:
        results = conn.execute(f'select previous_text, cleaned_text FROM tweet_cleaning;')
        results = [result for result in results]
        return results
    elif target_keywords is not None and target_index is None:
        query = f"select previous_text, cleaned_text FROM tweet_cleaning where previous_text like '%{target_keywords}%';"
        results = conn.execute(query)
        results = [result for result in results]
        return results
    elif target_keywords is None and target_index is not None:
        results = conn.execute(f'select previous_text, cleaned_text FROM tweet_cleaning WHERE id = {target_index};')
        results = [result for result in results]
        return results[0]

# *********************************************
# langkah selanjutnya adalah membuat function untuk membaca table yang sudah di input ke database (dapat membaca index, membaca keyword dan index dari keyword yg di input)