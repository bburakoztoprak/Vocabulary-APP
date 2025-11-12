import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import sqlite3
import random
from datetime import datetime

class VocabApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Vocabulary APP")
        self.root.geometry("930x930")
        self.root.configure(bg="#f0f0f0")
        
        # Veritabanı bağlantısı
        self.conn = sqlite3.connect('dictionary.db')
        self.cursor = self.conn.cursor()
        self.init_database()
        
        self.current_set_id = None
        self.show_main_menu()
    
    def init_database(self):
        # Kelime setleri tablosu
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS word_sets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                created_date TEXT
            )
        ''')
        
        # Kelimeler tablosu
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS words (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                set_id INTEGER,
                turkish TEXT NOT NULL,
                english TEXT NOT NULL,
                FOREIGN KEY (set_id) REFERENCES word_sets (id) ON DELETE CASCADE
            )
        ''')
        self.conn.commit()
    
    def clear_window(self):
        # Remove any global key bindings set by specific screens (e.g., flashcard)
        # so handlers from previous screens don't run in new screens.
        try:
            self.root.unbind("<space>")
            self.root.unbind("<Return>")
        except Exception:
            # If unbind isn't available for some reason, ignore and continue
            pass

        for widget in self.root.winfo_children():
            widget.destroy()
    
    def show_main_menu(self):
        self.clear_window()
        
        # Başlık
        title_frame = tk.Frame(self.root, bg="#2c3e50", height=80)
        title_frame.pack(fill=tk.X)
        title_frame.pack_propagate(False)
        
        tk.Label(title_frame, text="Vocabulary APP", 
                font=("Arial", 24, "bold"), bg="#2c3e50", fg="white").pack(expand=True)
        
        # Ana menü frame
        menu_frame = tk.Frame(self.root, bg="#f0f0f0")
        menu_frame.pack(expand=True, pady=50)
        
        buttons = [
            ("📝 Yeni Kelime Seti Ekleme", self.show_add_set_screen),
            ("🎴 Flashcard ile Öğren", self.show_flashcard_menu),
            ("✍️ Yazarak Pratik Yapma", self.show_writing_practice),
            ("📋 Çoktan Seçmeli Test", self.show_multiple_choice),
            ("🔗 Eşleştirme Testi", self.show_matching_test),
            ("📚 Kelime Setleri", self.show_word_sets)
        ]
        
        for text, command in buttons:
            btn = tk.Button(menu_frame, text=text, command=command,
                          font=("Arial", 14), width=30, height=2,
                          bg="#3498db", fg="white", cursor="hand2",
                          relief=tk.RAISED, bd=3)
            btn.pack(pady=10)
            btn.bind("<Enter>", lambda e, b=btn: b.config(bg="#2980b9"))
            btn.bind("<Leave>", lambda e, b=btn: b.config(bg="#3498db"))
    
    def show_flashcard_menu(self):
        """Flashcard alt menüsü"""
        self.clear_window()

        tk.Label(self.root, text="Flashcard ile Öğren", 
                font=("Arial", 20, "bold"), bg="#f0f0f0").pack(pady=20)
        
        tk.Label(self.root, text="Hangi yönde çalışmak istersiniz?", 
                font=("Arial", 12), bg="#f0f0f0", fg="#7f8c8d").pack(pady=10)
        
        menu_frame = tk.Frame(self.root, bg="#f0f0f0")
        menu_frame.pack(expand=True, pady=30)
        
        buttons = [
            ("🇹🇷 → 🇬🇧 Türkçe'den İngilizce'ye", lambda: self.start_flashcard("tr_to_en")),
            ("🇬🇧 → 🇹🇷 İngilizce'den Türkçe'ye", lambda: self.start_flashcard("en_to_tr")),
            ("🔀 Karışık Mod", lambda: self.start_flashcard("mixed"))
        ]
        
        for text, command in buttons:
            btn = tk.Button(menu_frame, text=text, command=command,
                          font=("Arial", 14), width=35, height=2,
                          bg="#9b59b6", fg="white", cursor="hand2",
                          relief=tk.RAISED, bd=3)
            btn.pack(pady=10)
            btn.bind("<Enter>", lambda e, b=btn: b.config(bg="#8e44ad"))
            btn.bind("<Leave>", lambda e, b=btn: b.config(bg="#9b59b6"))
       

        tk.Button(self.root, text="🔙 Ana Menü", command=self.show_main_menu,
                 font=("Arial", 11), bg="#95a5a6", fg="white", width=15).pack(pady=20)
    
    def start_flashcard(self, mode):
        """Flashcard çalışmasını başlat"""
        set_id = self.select_set_for_practice("flashcard")
        if not set_id:
            return
        
        self.cursor.execute('SELECT id, turkish, english FROM words WHERE set_id = ?', (set_id,))
        words = self.cursor.fetchall()
        random.shuffle(words)
        
        self.show_flashcard(words, mode)
    
    def show_flashcard(self, words, mode):
        """Flashcard ekranı"""
        if not words:
            messagebox.showinfo("Tamamlandı", "Tüm kartları gözden geçirdiniz!")
            # No cards to show — return to main menu. No need to touch any
            # local counters here because they are created per-session.
            self.show_main_menu()
            return
        
        self.clear_window()
        
        current_index = [0]
        is_flipped = [False]
        
        
        def display_card():
            
            if current_index[0] >= len(words):
                messagebox.showinfo("Tebrikler!", 
                    f"Tüm {len(words)} kelimeyi gözden geçirdiniz!\n\n"
                    "Öğrenmeye devam edin! 💪")
                
                self.show_main_menu()
                return 
            
            word_id, turkish, english = words[current_index[0]]
            is_flipped[0] = False
            
            # Modu belirle (karışık modda rastgele seç)
            if mode == "mixed":
                current_mode = random.choice(["tr_to_en", "en_to_tr"])
            else:
                current_mode = mode
            
            # Gösterilecek kelimeleri belirle
            if current_mode == "tr_to_en":
                front_text = turkish
                back_text = english
                front_lang = "🇹🇷 Türkçe"
                back_lang = "🇬🇧 İngilizce"
            else:
                front_text = english
                back_text = turkish
                front_lang = "🇬🇧 İngilizce"
                back_lang = "🇹🇷 Türkçe"
            
            # Başlık ve ilerleme
            header_frame = tk.Frame(self.root, bg="#f0f0f0")
            header_frame.pack(pady=20)
            
            tk.Label(header_frame, text="🎴 Flashcard Çalışması", 
                    font=("Arial", 20, "bold"), bg="#f0f0f0", fg="#9b59b6").pack()
            
            tk.Label(header_frame, text=f"Kart {current_index[0] + 1} / {len(words)}", 
                    font=("Arial", 12), bg="#f0f0f0", fg="#7f8c8d").pack(pady=5)
            
            # Kart frame
            card_frame = tk.Frame(self.root, bg="white", relief=tk.RAISED, bd=5,
                                 width=500, height=300)
            card_frame.pack(pady=30, padx=50)
            card_frame.pack_propagate(False)
            
            # Dil etiketi
            lang_label = tk.Label(card_frame, text=front_lang, 
                                 font=("Arial", 11, "italic"), bg="white", fg="#7f8c8d")
            lang_label.pack(pady=15)
            
            # Kelime metni
            word_label = tk.Label(card_frame, text=front_text, 
                                 font=("Arial", 32, "bold"), bg="white", fg="#2c3e50",
                                 wraplength=450)
            word_label.pack(expand=True)
            
            # Çevir ipucu
            hint_label = tk.Label(card_frame, text="↓ Kartı çevirmek için tıklayın ↓", 
                                 font=("Arial", 10, "italic"), bg="white", fg="#95a5a6")
            hint_label.pack(pady=10)
            
            def flip_card(event=None):
                if not is_flipped[0]:
                    # Kartı çevir
                    lang_label.config(text=back_lang)
                    word_label.config(text=back_text, fg="#27ae60")
                    hint_label.config(text="")
                    is_flipped[0] = True
                    
                    # Butonları aktif et
                    for btn in button_frame.winfo_children():
                        btn.config(state="normal")
            
            # Karta tıklama
            card_frame.bind("<Button-1>", flip_card)
            for widget in card_frame.winfo_children():
                widget.bind("<Button-1>", flip_card)
            
            # Alt butonlar
            button_frame = tk.Frame(self.root, bg="#f0f0f0")
            button_frame.pack(pady=20)
            
            def next_card():
                current_index[0] += 1
                self.clear_window()
                display_card()
            
            def know_it():
                messagebox.showinfo("Harika! 🎉", "Kelimenizi biliyorsunuz, mükemmel!")
                next_card()
            
            def dont_know():
                messagebox.showinfo("Sorun Değil 💪", 
                    f"Kelimenizi öğrendiniz:\n\n{turkish} = {english}\n\nTekrar ederek öğreneceksiniz!")
                next_card()
            
            # Butonlar (başlangıçta devre dışı)
            btn_know = tk.Button(button_frame, text="✅ Biliyorum", command=know_it,
                               font=("Arial", 12, "bold"), bg="#27ae60", fg="white", 
                               width=15, height=2, state="disabled")
            btn_know.pack(side=tk.LEFT, padx=10)
            
            btn_dont_know = tk.Button(button_frame, text="❌ Bilmiyorum", command=dont_know,
                                     font=("Arial", 12, "bold"), bg="#e74c3c", fg="white", 
                                     width=15, height=2, state="disabled")
            btn_dont_know.pack(side=tk.LEFT, padx=10)
            
            btn_skip = tk.Button(button_frame, text="⏭️ Atla", command=next_card,
                               font=("Arial", 12), bg="#95a5a6", fg="white", 
                               width=12, height=2)
            btn_skip.pack(side=tk.LEFT, padx=10)
            
            # Çıkış butonu
            tk.Button(self.root, text="🔙 Ana Menü", command=self.show_main_menu,
                     font=("Arial", 11), bg="#34495e", fg="white", width=15).pack(pady=10)
            
            # Klavye kısayolları
            self.root.bind("<space>", flip_card)
            self.root.bind("<Return>", lambda e: next_card() if is_flipped[0] else flip_card())
        
        display_card()
    
    def show_add_set_screen(self):
        self.clear_window()
        
        # Başlık
        tk.Label(self.root, text="Yeni Kelime Seti Oluştur", 
                font=("Arial", 20, "bold"), bg="#f0f0f0").pack(pady=20)
        
        # Set adı
        name_frame = tk.Frame(self.root, bg="#f0f0f0")
        name_frame.pack(pady=10)
        tk.Label(name_frame, text="Set Adı:", font=("Arial", 12), bg="#f0f0f0").pack(side=tk.LEFT, padx=5)
        set_name_entry = tk.Entry(name_frame, font=("Arial", 12), width=30)
        set_name_entry.pack(side=tk.LEFT)
        
        # Kelime listesi frame
        list_frame = tk.Frame(self.root, bg="white", relief=tk.RIDGE, bd=2)
        list_frame.pack(pady=20, padx=50, fill=tk.BOTH, expand=True)
        
        # Başlıklar
        header_frame = tk.Frame(list_frame, bg="#ecf0f1")
        header_frame.pack(fill=tk.X)
        tk.Label(header_frame, text="Türkçe", font=("Arial", 12, "bold"), 
                bg="#ecf0f1", width=25).pack(side=tk.LEFT, padx=5, pady=5)
        tk.Label(header_frame, text="İngilizce", font=("Arial", 12, "bold"), 
                bg="#ecf0f1", width=25).pack(side=tk.LEFT, padx=5, pady=5)
        
        # Kaydırılabilir alan
        canvas = tk.Canvas(list_frame, bg="white")
        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg="white")
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        word_entries = []
        
        def add_word_row():
            row_frame = tk.Frame(scrollable_frame, bg="white")
            row_frame.pack(fill=tk.X, pady=2)
            
            turkish_entry = tk.Entry(row_frame, font=("Arial", 11), width=28)
            turkish_entry.pack(side=tk.LEFT, padx=5)
            
            english_entry = tk.Entry(row_frame, font=("Arial", 11), width=28)
            english_entry.pack(side=tk.LEFT, padx=5)
            
            delete_btn = tk.Button(row_frame, text="❌", command=lambda: row_frame.destroy(),
                                  bg="#e74c3c", fg="white", width=3)
            delete_btn.pack(side=tk.LEFT, padx=5)

            word_entries.append((turkish_entry, english_entry))

        # İlk satırları ekle
        for _ in range(5):
            add_word_row()
        
        # Butonlar
        button_frame = tk.Frame(self.root, bg="#f0f0f0")
        button_frame.pack(pady=10)
        
        tk.Button(button_frame, text="➕ Satır Ekle", command=add_word_row,
                 font=("Arial", 11), bg="#27ae60", fg="white", width=15).pack(side=tk.LEFT, padx=5)
        
        def save_set():
            set_name = set_name_entry.get().strip()
            if not set_name:
                messagebox.showerror("Hata", "Lütfen set adı girin!")
                return
            
            words = [(tr.get().strip(), en.get().strip()) 
                    for tr, en in word_entries 
                    if tr.get().strip() and en.get().strip()]
            
            if not words:
                messagebox.showerror("Hata", "Lütfen en az bir kelime ekleyin!")
                return
            
            # Veritabanına kaydet
            self.cursor.execute('INSERT INTO word_sets (name, created_date) VALUES (?, ?)',
                              (set_name, datetime.now().strftime("%Y-%m-%d %H:%M")))
            set_id = self.cursor.lastrowid
            
            for turkish, english in words:
                self.cursor.execute('INSERT INTO words (set_id, turkish, english) VALUES (?, ?, ?)',
                                  (set_id, turkish, english))
            
            self.conn.commit()
            messagebox.showinfo("Başarılı", f"{len(words)} kelime ile '{set_name}' seti oluşturuldu!")
            self.show_main_menu()
        
        tk.Button(button_frame, text="💾 Kaydet", command=save_set,
                 font=("Arial", 11), bg="#2ecc71", fg="white", width=15).pack(side=tk.LEFT, padx=5)
        
        tk.Button(button_frame, text="🔙 Geri", command=self.show_main_menu,
                 font=("Arial", 11), bg="#95a5a6", fg="white", width=15).pack(side=tk.LEFT, padx=5)
    
    def show_word_sets(self):
        self.clear_window()
        
        tk.Label(self.root, text="Kelime Setleri", 
                font=("Arial", 20, "bold"), bg="#f0f0f0").pack(pady=20)
        
        # Set listesi
        list_frame = tk.Frame(self.root, bg="white", relief=tk.RIDGE, bd=2)
        list_frame.pack(pady=20, padx=50, fill=tk.BOTH, expand=True)

        canvas = tk.Canvas(list_frame, bg="white")
        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg="white")

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        list_frame = scrollable_frame

        
        self.cursor.execute('SELECT id, name, created_date FROM word_sets ORDER BY created_date DESC')
        sets = self.cursor.fetchall()
        
        if not sets:
            tk.Label(list_frame, text="Henüz kelime seti eklenmemiş", 
                    font=("Arial", 14), bg="white").pack(expand=True)
        else:
            for set_id, name, date in sets:
                self.cursor.execute('SELECT COUNT(*) FROM words WHERE set_id = ?', (set_id,))
                word_count = self.cursor.fetchone()[0]
                
                set_frame = tk.Frame(list_frame, bg="#ecf0f1", relief=tk.RAISED, bd=2)
                set_frame.pack(fill=tk.X, padx=10, pady=5)
                
                info_frame = tk.Frame(set_frame, bg="#ecf0f1")
                info_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
                
                tk.Label(info_frame, text=name, font=("Arial", 14, "bold"), 
                        bg="#ecf0f1", anchor="w").pack(fill=tk.X)
                tk.Label(info_frame, text=f"{word_count} kelime • {date}", 
                        font=("Arial", 10), bg="#ecf0f1", fg="#7f8c8d", anchor="w").pack(fill=tk.X)
                
                btn_frame = tk.Frame(set_frame, bg="#ecf0f1")
                btn_frame.pack(side=tk.RIGHT, padx=5)
                
                tk.Button(btn_frame, text="✏️ Düzenle", 
                         command=lambda sid=set_id: self.edit_set(sid),
                         bg="#3498db", fg="white", width=10).pack(side=tk.LEFT, padx=2)
                
                tk.Button(btn_frame, text="🗑️ Sil", 
                         command=lambda sid=set_id, n=name: self.delete_set(sid, n),
                         bg="#e74c3c", fg="white", width=10).pack(side=tk.LEFT, padx=2)
        
        tk.Button(self.root, text="🔙 Ana Menü", command=self.show_main_menu,
                 font=("Arial", 12), bg="#95a5a6", fg="white", width=20).pack(pady=10)
    
    def edit_set(self, set_id):
        self.clear_window()
        
        # Set bilgilerini al
        self.cursor.execute('SELECT name FROM word_sets WHERE id = ?', (set_id,))
        set_name = self.cursor.fetchone()[0]
        
        tk.Label(self.root, text=f"'{set_name}' Düzenleniyor", 
                font=("Arial", 20, "bold"), bg="#f0f0f0").pack(pady=20)
        
        # Set adı düzenleme
        name_frame = tk.Frame(self.root, bg="#f0f0f0")
        name_frame.pack(pady=10)
        tk.Label(name_frame, text="Set Adı:", font=("Arial", 12), bg="#f0f0f0").pack(side=tk.LEFT, padx=5)
        set_name_entry = tk.Entry(name_frame, font=("Arial", 12), width=30)
        set_name_entry.insert(0, set_name)
        set_name_entry.pack(side=tk.LEFT)
        
        # Kelime listesi
        list_frame = tk.Frame(self.root, bg="white", relief=tk.RIDGE, bd=2)
        list_frame.pack(pady=20, padx=50, fill=tk.BOTH, expand=True)
        
        header_frame = tk.Frame(list_frame, bg="#ecf0f1")
        header_frame.pack(fill=tk.X)
        tk.Label(header_frame, text="Türkçe", font=("Arial", 12, "bold"), 
                bg="#ecf0f1", width=25).pack(side=tk.LEFT, padx=5, pady=5)
        tk.Label(header_frame, text="İngilizce", font=("Arial", 12, "bold"), 
                bg="#ecf0f1", width=25).pack(side=tk.LEFT, padx=5, pady=5)
        
        canvas = tk.Canvas(list_frame, bg="white")
        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg="white")
        
        scrollable_frame.bind("<Configure>", 
            lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        word_entries = []
        
        def add_word_row(turkish="", english="", word_id=None):
            row_frame = tk.Frame(scrollable_frame, bg="white")
            row_frame.pack(fill=tk.X, pady=2)
            
            turkish_entry = tk.Entry(row_frame, font=("Arial", 11), width=28)
            turkish_entry.insert(0, turkish)
            turkish_entry.pack(side=tk.LEFT, padx=5)
            
            english_entry = tk.Entry(row_frame, font=("Arial", 11), width=28)
            english_entry.insert(0, english)
            english_entry.pack(side=tk.LEFT, padx=5)
            
            delete_btn = tk.Button(row_frame, text="❌", command=lambda: row_frame.destroy(),
                                  bg="#e74c3c", fg="white", width=3)
            delete_btn.pack(side=tk.LEFT, padx=5)
            
            word_entries.append((turkish_entry, english_entry, word_id))
        
        # Mevcut kelimeleri yükle
        self.cursor.execute('SELECT id, turkish, english FROM words WHERE set_id = ?', (set_id,))
        existing_words = self.cursor.fetchall()
        for word_id, turkish, english in existing_words:
            add_word_row(turkish, english, word_id)
        
        button_frame = tk.Frame(self.root, bg="#f0f0f0")
        button_frame.pack(pady=10)
        
        tk.Button(button_frame, text="➕ Satır Ekle", command=lambda: add_word_row(),
                 font=("Arial", 11), bg="#27ae60", fg="white", width=15).pack(side=tk.LEFT, padx=5)
        
        def save_changes():
            new_name = set_name_entry.get().strip()
            if not new_name:
                messagebox.showerror("Hata", "Lütfen set adı girin!")
                return
            
            # Set adını güncelle
            self.cursor.execute('UPDATE word_sets SET name = ? WHERE id = ?', (new_name, set_id))
            
            # Tüm eski kelimeleri sil
            self.cursor.execute('DELETE FROM words WHERE set_id = ?', (set_id,))
            
            # Yeni kelimeleri ekle
            words = [(tr.get().strip(), en.get().strip()) 
                    for tr, en, _ in word_entries 
                    if tr.get().strip() and en.get().strip()]
            
            if not words:
                messagebox.showerror("Hata", "Lütfen en az bir kelime ekleyin!")
                return
            
            for turkish, english in words:
                self.cursor.execute('INSERT INTO words (set_id, turkish, english) VALUES (?, ?, ?)',
                                  (set_id, turkish, english))
            
            self.conn.commit()
            messagebox.showinfo("Başarılı", "Değişiklikler kaydedildi!")
            self.show_word_sets()
        
        tk.Button(button_frame, text="💾 Kaydet", command=save_changes,
                 font=("Arial", 11), bg="#2ecc71", fg="white", width=15).pack(side=tk.LEFT, padx=5)
        
        tk.Button(button_frame, text="🔙 Geri", command=self.show_word_sets,
                 font=("Arial", 11), bg="#95a5a6", fg="white", width=15).pack(side=tk.LEFT, padx=5)
    
    def delete_set(self, set_id, set_name):
        if messagebox.askyesno("Silme Onayı", f"'{set_name}' setini silmek istediğinize emin misiniz?"):
            self.cursor.execute('DELETE FROM words WHERE set_id = ?', (set_id,))
            self.cursor.execute('DELETE FROM word_sets WHERE id = ?', (set_id,))
            self.conn.commit()
            messagebox.showinfo("Başarılı", "Set silindi!")
            self.show_word_sets()
    
    def show_writing_practice(self):
        self.clear_window()

        tk.Label(self.root, text="Yazarak Pratik Yapma", 
                font=("Arial", 20, "bold"), bg="#f0f0f0").pack(pady=20)
        menu_frame = tk.Frame(self.root, bg="#f0f0f0")
        menu_frame.pack(expand=True, pady=50)
        
        buttons = [
            ("✍️ İngilizce Yazarak Pratik Yapma", self.show_writing_practice_english),
            ("✍️ Türkçe Yazarak Pratik Yapma", self.show_writing_practice_turkish)
        ]
        
        for text, command in buttons:
            btn = tk.Button(menu_frame, text=text, command=command,
                          font=("Arial", 14), width=30, height=2,
                          bg="#3498db", fg="white", cursor="hand2",
                          relief=tk.RAISED, bd=3)
            btn.pack(pady=10)
            btn.bind("<Enter>", lambda e, b=btn: b.config(bg="#2980b9"))
            btn.bind("<Leave>", lambda e, b=btn: b.config(bg="#3498db"))
        tk.Button(self.root, text="🔙 Ana Menü", command=self.show_main_menu,
                     font=("Arial", 11), bg="#95a5a6", fg="white", width=15).pack(pady=10)

    def show_writing_practice_english(self):
        set_id = self.select_set_for_practice("writing")
        if not set_id:
            return
        
        self.cursor.execute('SELECT id, turkish, english FROM words WHERE set_id = ?', (set_id,))
        words = self.cursor.fetchall()
        random.shuffle(words)
        
        self.clear_window()
        
        current_index = [0]
        correct_count = [0]
        
        def show_word():
            if current_index[0] >= len(words):
                self.show_results(correct_count[0], len(words), "Yazma Pratiği")
                return
            
            self.clear_window()
            
            word_id, turkish, english = words[current_index[0]]
            
            # Başlık
            tk.Label(self.root, text=f"Soru {current_index[0] + 1} / {len(words)}", 
                    font=("Arial", 14), bg="#f0f0f0", fg="#7f8c8d").pack(pady=10)
            
            # Türkçe kelime
            tk.Label(self.root, text=turkish, 
                    font=("Arial", 28, "bold"), bg="#f0f0f0", fg="#2c3e50").pack(pady=40)
            
            # Cevap girişi
            tk.Label(self.root, text="İngilizce karşılığını yazın:", 
                    font=("Arial", 12), bg="#f0f0f0").pack()
            
            answer_entry = tk.Entry(self.root, font=("Arial", 16), width=30, justify="center")
            answer_entry.pack(pady=10)
            answer_entry.focus()
            
            result_label = tk.Label(self.root, text="", font=("Arial", 12, "bold"), bg="#f0f0f0")
            result_label.pack(pady=10)
            
            def check_answer():
                user_answer = answer_entry.get().strip().lower()
                correct_answer = english.lower()
                
                if user_answer == correct_answer:
                    result_label.config(text="✅ Doğru!", fg="#27ae60")
                    correct_count[0] += 1
                else:
                    result_label.config(text=f"❌ Yanlış! Doğru cevap: {english}", fg="#e74c3c")
                
                answer_entry.config(state="disabled")
                check_btn.config(state="disabled")
                next_btn.config(state="normal")
            
            def next_word():
                current_index[0] += 1
                show_word()
            
            button_frame = tk.Frame(self.root, bg="#f0f0f0")
            button_frame.pack(pady=20)
            
            check_btn = tk.Button(button_frame, text="Kontrol Et", command=check_answer,
                                 font=("Arial", 12), bg="#3498db", fg="white", width=15)
            check_btn.pack(side=tk.LEFT, padx=5)
            
            next_btn = tk.Button(button_frame, text="Sonraki ➡️", command=next_word,
                                font=("Arial", 12), bg="#2ecc71", fg="white", width=15, state="disabled")
            next_btn.pack(side=tk.LEFT, padx=5)
            
            answer_entry.bind("<Return>", lambda e: check_answer() if check_btn["state"] == "normal" else next_word())
            
            tk.Button(self.root, text="🔙 Çıkış", command=self.show_main_menu,
                     font=("Arial", 11), bg="#95a5a6", fg="white", width=15).pack(pady=10)
        
        show_word()

    def show_writing_practice_turkish(self):
        set_id = self.select_set_for_practice("writing")
        if not set_id:
            return
        
        self.cursor.execute('SELECT id, english, turkish FROM words WHERE set_id = ?', (set_id,))
        words = self.cursor.fetchall()
        random.shuffle(words)

        self.clear_window()
        
        current_index = [0]
        correct_count = [0]
        
        def show_word():
            if current_index[0] >= len(words):
                self.show_results(correct_count[0], len(words), "Yazma Pratiği")
                return
            
            self.clear_window()
            
            word_id, turkish, english = words[current_index[0]]
            
            # Başlık
            tk.Label(self.root, text=f"Soru {current_index[0] + 1} / {len(words)}", 
                    font=("Arial", 14), bg="#f0f0f0", fg="#7f8c8d").pack(pady=10)
            
            # İngilizce kelime
            tk.Label(self.root, text=turkish, 
                    font=("Arial", 28, "bold"), bg="#f0f0f0", fg="#2c3e50").pack(pady=40)
            
            # Cevap girişi
            tk.Label(self.root, text="Türkçe karşılığını yazın:", 
                    font=("Arial", 12), bg="#f0f0f0").pack()
            
            answer_entry = tk.Entry(self.root, font=("Arial", 16), width=30, justify="center")
            answer_entry.pack(pady=10)
            answer_entry.focus()
            
            result_label = tk.Label(self.root, text="", font=("Arial", 12, "bold"), bg="#f0f0f0")
            result_label.pack(pady=10)
            
            def check_answer():
                user_answer = answer_entry.get().strip().lower()
                correct_answer = english.lower()
                
                if user_answer == correct_answer:
                    result_label.config(text="✅ Doğru!", fg="#27ae60")
                    correct_count[0] += 1
                else:
                    result_label.config(text=f"❌ Yanlış! Doğru cevap: {english}", fg="#e74c3c")
                
                answer_entry.config(state="disabled")
                check_btn.config(state="disabled")
                next_btn.config(state="normal")
            
            def next_word():
                current_index[0] += 1
                show_word()
            
            button_frame = tk.Frame(self.root, bg="#f0f0f0")
            button_frame.pack(pady=20)
            
            check_btn = tk.Button(button_frame, text="Kontrol Et", command=check_answer,
                                 font=("Arial", 12), bg="#3498db", fg="white", width=15)
            check_btn.pack(side=tk.LEFT, padx=5)
            
            next_btn = tk.Button(button_frame, text="Sonraki ➡️", command=next_word,
                                font=("Arial", 12), bg="#2ecc71", fg="white", width=15, state="disabled")
            next_btn.pack(side=tk.LEFT, padx=5)
            
            answer_entry.bind("<Return>", lambda e: check_answer() if check_btn["state"] == "normal" else next_word())
            
            tk.Button(self.root, text="🔙 Çıkış", command=self.show_main_menu,
                     font=("Arial", 11), bg="#95a5a6", fg="white", width=15).pack(pady=10)
        
        show_word()

    def select_set_for_practice(self, practice_type):
        self.cursor.execute('SELECT id, name FROM word_sets')
        sets = self.cursor.fetchall()
        
        if not sets:
            messagebox.showwarning("Uyarı", "Henüz kelime seti yok! Önce bir set oluşturun.")
            return None
        
        dialog = tk.Toplevel(self.root)
        dialog.title("Set Seçin")
        dialog.geometry("400x300")
        dialog.transient(self.root)
        dialog.grab_set()

        ## scrollable frame ##
        canvas = tk.Canvas(dialog)
        scollbar = tk.Scrollbar(dialog, orient = 'vertical', command=canvas.yview)
        scrollable_frame = tk.Frame(canvas)
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(
                scrollregion=canvas.bbox("all")
            )
        )
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scollbar.set)

        selected_set = tk.IntVar()
        
        for set_id, name in sets:
            self.cursor.execute('SELECT COUNT(*) FROM words WHERE set_id = ?', (set_id,))
            word_count = self.cursor.fetchone()[0]
            tk.Radiobutton(scrollable_frame, text=f"{name} ({word_count} kelime)", 
                          variable=selected_set, value=set_id,
                          font=("Arial", 11)).pack(anchor=tk.W, padx=40, pady=5)
        
        canvas.pack(side="left", fill="both", expand=True)
        scollbar.pack(side="right", fill="y")
        #####################
        result = [None]
        
        def confirm():
            if selected_set.get():
                result[0] = selected_set.get()
                dialog.destroy()
            else:
                messagebox.showwarning("Uyarı", "Lütfen bir set seçin!")
        
        tk.Button(scrollable_frame, text="Başla", command=confirm, 
                 font=("Arial", 11), bg="#2ecc71", fg="white", width=15).pack(pady=20)
        
        self.root.wait_window(scrollable_frame)
        return result[0]

    def show_multiple_choice(self):
        set_id = self.select_set_for_practice("multiple_choice")
        if not set_id:
            return
        
        self.cursor.execute('SELECT id, turkish, english FROM words WHERE set_id = ?', (set_id,))
        words = self.cursor.fetchall()
        
        if len(words) < 4:
            messagebox.showwarning("Uyarı", "Bu test için en az 4 kelime gerekli!")
            return
        
        random.shuffle(words)
        
        self.clear_window()
        
        current_index = [0]
        correct_count = [0]
        user_answers = []  # Kullanıcının cevaplarını sakla
        
        def show_question():
            if current_index[0] >= len(words):
                self.show_results(correct_count[0], len(words), "Çoktan Seçmeli Test")
                return
            
            self.clear_window()
            
            word_id, turkish, english = words[current_index[0]]
            
            # Yanlış seçenekler oluştur
            other_words = [w for w in words if w[0] != word_id]
            wrong_choices = random.sample(other_words, min(3, len(other_words)))
            
            choices = [english] + [w[2] for w in wrong_choices]
            random.shuffle(choices)
            
            # Başlık
            tk.Label(self.root, text=f"Soru {current_index[0] + 1} / {len(words)}", 
                    font=("Arial", 14), bg="#f0f0f0", fg="#7f8c8d").pack(pady=10)
            
            # Türkçe kelime
            tk.Label(self.root, text=turkish, 
                    font=("Arial", 28, "bold"), bg="#f0f0f0", fg="#2c3e50").pack(pady=40)
            
            tk.Label(self.root, text="Doğru İngilizce karşılığını seçin ve Enter'a basın:", 
                    font=("Arial", 12), bg="#f0f0f0").pack(pady=10)
            
            selected = tk.StringVar()
            
            def next_question(event=None):
                if not selected.get():
                    messagebox.showwarning("Uyarı", "Lütfen bir seçenek seçin!")
                    return
                
                # Cevabı kontrol et ve kaydet
                if selected.get() == english:
                    correct_count[0] += 1
                
                user_answers.append((turkish, english, selected.get()))
                
                current_index[0] += 1
                show_question()
            
            choice_frame = tk.Frame(self.root, bg="#f0f0f0")
            choice_frame.pack(pady=20)
            
            for choice in choices:
                rb = tk.Radiobutton(choice_frame, text=choice, variable=selected, value=choice,
                                   font=("Arial", 14), bg="#f0f0f0", cursor="hand2")
                rb.pack(anchor=tk.W, padx=100, pady=8)
            
            # Enter tuşu ile sonraki soruya geç
            self.root.bind("<Return>", next_question)
            
            button_frame = tk.Frame(self.root, bg="#f0f0f0")
            button_frame.pack(pady=20)
            
            next_btn = tk.Button(button_frame, text="Sonraki ➡️", command=next_question,
                                font=("Arial", 12), bg="#2ecc71", fg="white", width=15)
            next_btn.pack(side=tk.LEFT, padx=5)
            
            tk.Button(self.root, text="🔙 Çıkış", command=self.show_main_menu,
                     font=("Arial", 11), bg="#95a5a6", fg="white", width=15).pack(pady=10)
        
        show_question()
    
    def show_matching_test(self):
        set_id = self.select_set_for_practice("matching")
        if not set_id:
            return
        
        # TÜM kelimeleri al
        self.cursor.execute('SELECT id, turkish, english FROM words WHERE set_id = ?', (set_id,))
        all_words = self.cursor.fetchall()
        
        if len(all_words) < 3:
            messagebox.showwarning("Uyarı", "Bu test için en az 3 kelime gerekli!")
            return
        
        # Kelimeleri karıştır
        random.shuffle(all_words)
        
        # 10'ar kelimelik gruplara böl
        word_groups = [all_words[i:i+10] for i in range(0, len(all_words), 10)]
        
        current_group_index = [0]
        total_correct = [0]
    
        def show_group():
            if current_group_index[0] >= len(word_groups):
                # Tüm gruplar tamamlandı
                self.show_results(total_correct[0], len(all_words), "Eşleştirme Testi")
                return
            
            words = word_groups[current_group_index[0]]
            
            self.clear_window()
            
            # Başlık ve ilerleme bilgisi
            tk.Label(self.root, text="Eşleştirme Testi", 
                    font=("Arial", 20, "bold"), bg="#f0f0f0").pack(pady=10)
            
            progress_text = f"Grup {current_group_index[0] + 1} / {len(word_groups)} ({len(words)} kelime)"
            tk.Label(self.root, text=progress_text, 
                    font=("Arial", 12, "bold"), bg="#f0f0f0", fg="#3498db").pack(pady=5)
            
            tk.Label(self.root, text="Sol taraftaki Türkçe kelimelere tıklayın, ardından eşleşen İngilizce kelimeye tıklayın", 
                    font=("Arial", 11), bg="#f0f0f0", fg="#7f8c8d").pack(pady=5)
            
            # Kelimeleri karıştır
            turkish_words = [(w[0], w[1]) for w in words]
            english_words = [(w[0], w[2]) for w in words]
            random.shuffle(english_words)
            
            # Eşleştirme frame'i
            matching_frame = tk.Frame(self.root, bg="#f0f0f0")
            matching_frame.pack(expand=True, pady=20)
            
            left_frame = tk.Frame(matching_frame, bg="#f0f0f0")
            left_frame.pack(side=tk.LEFT, padx=50)
            
            tk.Label(left_frame, text="Türkçe", font=("Arial", 14, "bold"), bg="#f0f0f0").pack(pady=10)
            
            right_frame = tk.Frame(matching_frame, bg="#f0f0f0")
            right_frame.pack(side=tk.RIGHT, padx=50)
            
            tk.Label(right_frame, text="İngilizce", font=("Arial", 14, "bold"), bg="#f0f0f0").pack(pady=10)
            
            selected_turkish = [None]
            matched_pairs = []
            turkish_buttons = {}
            english_buttons = {}
            
            def on_turkish_click(word_id, btn):
                if word_id in [m[0] for m in matched_pairs]:
                    return
                
                # Önceki seçimi temizle
                if selected_turkish[0]:
                    prev_id, prev_btn = selected_turkish[0]
                    if prev_id not in [m[0] for m in matched_pairs]:
                        prev_btn.config(bg="#3498db")
                
                selected_turkish[0] = (word_id, btn)
                btn.config(bg="#f39c12")
            
            def on_english_click(word_id, btn):
                if word_id in [m[1] for m in matched_pairs]:
                    return
                
                if not selected_turkish[0]:
                    messagebox.showinfo("Bilgi", "Önce sol taraftan bir Türkçe kelime seçin!")
                    return
                
                turkish_id, turkish_btn = selected_turkish[0]
                
                if turkish_id == word_id:
                    # Doğru eşleştirme
                    turkish_btn.config(bg="#27ae60", state="disabled")
                    btn.config(bg="#27ae60", state="disabled")
                    matched_pairs.append((turkish_id, word_id))
                    total_correct[0] += 1
                    selected_turkish[0] = None
                    
                    # Bu grup tamamlandı mı kontrol et
                    if len(matched_pairs) == len(words):
                        current_group_index[0] += 1
                        
                        if current_group_index[0] < len(word_groups):
                            # Sonraki gruba geç
                            messagebox.showinfo("Tebrikler!", 
                                            f"Bu grubu tamamladınız! ({len(words)}/{len(words)} doğru)\n\n"
                                            f"Şimdi sonraki {min(10, len(all_words) - current_group_index[0] * 10)} kelimeye geçiyoruz...")
                            show_group()
                        else:
                            # Tüm test tamamlandı
                            messagebox.showinfo("Tebrikler!", 
                                            f"Tüm kelimeleri tamamladınız! ({total_correct[0]}/{len(all_words)} doğru)")
                            show_group()  # Sonuç ekranını göster
                else:
                    # Yanlış eşleştirme
                    turkish_btn.config(bg="#e74c3c")
                    btn.config(bg="#e74c3c")
                    self.root.after(500, lambda: [
                        turkish_btn.config(bg="#3498db"),
                        btn.config(bg="#3498db")
                    ])
                    selected_turkish[0] = None
            
            for word_id, turkish in turkish_words:
                btn = tk.Button(left_frame, text=turkish, font=("Arial", 12),
                            bg="#3498db", fg="white", width=20, height=2,
                            command=lambda wid=word_id, b=None: on_turkish_click(wid, turkish_buttons[wid]))
                btn.pack(pady=5)
                turkish_buttons[word_id] = btn
                btn.config(command=lambda wid=word_id, b=btn: on_turkish_click(wid, b))
            
            for word_id, english in english_words:
                btn = tk.Button(right_frame, text=english, font=("Arial", 12),
                            bg="#3498db", fg="white", width=20, height=2,
                            command=lambda wid=word_id, b=None: on_english_click(wid, english_buttons[wid]))
                btn.pack(pady=5)
                english_buttons[word_id] = btn
                btn.config(command=lambda wid=word_id, b=btn: on_english_click(wid, b))
            
            tk.Button(self.root, text="🔙 Ana Menü", command=self.show_main_menu,
                    font=("Arial", 11), bg="#95a5a6", fg="white", width=15).pack(pady=20)
        
        # İlk grubu göster
        show_group()

    def show_results(self, correct, total, test_name):
        self.clear_window()
        
        percentage = (correct / total) * 100
        
        tk.Label(self.root, text="Test Tamamlandı!", 
                font=("Arial", 24, "bold"), bg="#f0f0f0", fg="#2c3e50").pack(pady=30)
        
        tk.Label(self.root, text=test_name, 
                font=("Arial", 16), bg="#f0f0f0", fg="#7f8c8d").pack(pady=10)
        
        result_frame = tk.Frame(self.root, bg="white", relief=tk.RIDGE, bd=3)
        result_frame.pack(pady=30, padx=100)
        
        tk.Label(result_frame, text=f"Doğru: {correct} / {total}", 
                font=("Arial", 18, "bold"), bg="white", fg="#27ae60").pack(pady=15, padx=50)
        
        tk.Label(result_frame, text=f"Başarı Oranı: %{percentage:.1f}", 
                font=("Arial", 18, "bold"), bg="white", fg="#3498db").pack(pady=15, padx=50)
        ## hatalıları gösterme ##
        tk.Label(result_frame, text="Hatalı Kelimeler:", 
                font=("Arial", 16, "bold"), bg="white", fg="#e74c3c").pack(pady=10, padx=50)
        # Hatalı kelimeleri listele
        # Bu kısmı kullanıcı cevaplarını sakladığınız yere göre uyarlayın -- eklenecek

        if percentage >= 80:
            emoji = "🎉"
            message = "Harika! Mükemmel bir performans!"
        elif percentage >= 60:
            emoji = "👍"
            message = "İyi iş! Gelişmeye devam edin!"
        else:
            emoji = "💪"
            message = "Pratik yapmaya devam edin!"
        
        tk.Label(self.root, text=f"{emoji} {message}", 
                font=("Arial", 14), bg="#f0f0f0", fg="#2c3e50").pack(pady=20)
        
        button_frame = tk.Frame(self.root, bg="#f0f0f0")
        button_frame.pack(pady=20)
        
        tk.Button(button_frame, text="🔄 Tekrar Dene", command=lambda: self.show_main_menu(),
                 font=("Arial", 12), bg="#3498db", fg="white", width=20).pack(side=tk.LEFT, padx=10)
        
        tk.Button(button_frame, text="🏠 Ana Menü", command=self.show_main_menu,
                 font=("Arial", 12), bg="#2ecc71", fg="white", width=20).pack(side=tk.LEFT, padx=10)
    
    def __del__(self):
        self.conn.close()

if __name__ == "__main__":
    root = tk.Tk()
    app = VocabApp(root)
    root.mainloop() 