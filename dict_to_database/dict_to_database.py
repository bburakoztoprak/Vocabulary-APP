import sqlite3
import json

# JSON dosyasını oku
with open('sozluk.json', 'r', encoding='utf-8') as f:
    json_data = json.load(f)

# Veritabanı bağlantısı
conn = sqlite3.connect('dictionary.db')
cursor = conn.cursor()


cursor.execute('''
    CREATE TABLE IF NOT EXISTS word_sets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL ,
    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
          )''')
# Tablo oluştur
cursor.execute('''
CREATE TABLE IF NOT EXISTS words (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    set_id INTEGER,
    
    turkish TEXT NOT NULL,
    english TEXT NOT NULL,
    UNIQUE(set_id, english),
    FOREIGN KEY (set_id) REFERENCES word_sets (id) ON DELETE CASCADE
)
''')

# Verileri aktar
successed = 0
for set_id, words in json_data.items():
    try:
        cursor.execute('INSERT INTO word_sets (name) VALUES (?)', (set_id,))
        set_id = cursor.lastrowid
    except sqlite3.IntegrityError:
        cursor.execute('SELECT id FROM word_sets WHERE name = ?', (set_id,))
        set_id = cursor.fetchone()[0]
    for english, turkish in words.items():
        try:
            cursor.execute('''
            INSERT INTO words (set_id,  english, turkish)
            VALUES ( ?,  ?, ?)
            ''', (set_id,  english.strip(), turkish))
            successed += 1
        except sqlite3.IntegrityError:
            print(f"Uyarı: '{english}' kelimesi zaten {set_id}'de mevcut")

conn.commit()

# İstatistikler
cursor.execute('SELECT COUNT(*) FROM words')
toplam = cursor.fetchone()[0]

print(f"\n✓ {successed} kelime başarıyla eklendi")
print(f"✓ Toplam {toplam} kelime veritabanında")

conn.close()