import sqlite3
import os

# 1. TOMBOL NUKLIR DIMATIKAN (Di-comment pake hashtag)
#if os.path.exists('sekolah.db'):
    #os.remove('sekolah.db')

conn = sqlite3.connect('sekolah.db')
cursor = conn.cursor()

# 2. PENGAMAN "IF NOT EXISTS" BIAR DATA GA HANCUR KETIKA DI-RUN
cursor.execute('''CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT UNIQUE, password TEXT, role TEXT, kelas TEXT)''')

cursor.execute('''CREATE TABLE IF NOT EXISTS ujian (
    id INTEGER PRIMARY KEY AUTOINCREMENT, token TEXT UNIQUE, mata_pelajaran TEXT, jam_mulai TEXT, jam_selesai TEXT, pembuat TEXT)''')

# 3. TABEL MATERI DIBALIKIN 'kelas_target'-NYA & DITAMBAH 'guru_username'
cursor.execute('''CREATE TABLE IF NOT EXISTS materi (
    id INTEGER PRIMARY KEY AUTOINCREMENT, 
    judul TEXT, 
    nama_file TEXT, 
    mata_pelajaran TEXT,
    kelas_target TEXT, 
    guru_username TEXT,
    tanggal_upload TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')

cursor.execute('''CREATE TABLE IF NOT EXISTS soal_ujian (
    id INTEGER PRIMARY KEY AUTOINCREMENT, token_ujian TEXT, nomor_soal INTEGER,
    tipe_soal TEXT, pertanyaan TEXT, opsi_a TEXT, opsi_b TEXT, opsi_c TEXT, opsi_d TEXT, kunci_jawaban TEXT)''')

cursor.execute('''CREATE TABLE IF NOT EXISTS jawaban_siswa (
    id INTEGER PRIMARY KEY AUTOINCREMENT, token_ujian TEXT, username TEXT, kelas TEXT, nomor_soal INTEGER, jawaban TEXT,
    status TEXT DEFAULT 'Belum Dikoreksi', kecocokan INTEGER, rekomendasi_nilai INTEGER, analisis TEXT)''')

# 4. INSERT DATA DENGAN PENGAMAN 'IGNORE' (Ga bakal error duplikat)
akun_default = [
    ('guru_bima', '123', 'guru', 'Guru'), ('guru_hamid', '123', 'guru', 'Guru'),
    ('faisal1', '123', 'murid', 'TKJ 1'), ('bila1', '123', 'murid', 'TKJ 1'), ('hamid1', '123', 'murid', 'TKRO 1')
]
cursor.executemany("INSERT OR IGNORE INTO users (username, password, role, kelas) VALUES (?, ?, ?, ?)", akun_default)

conn.commit()
conn.close()
print("✅ Sistem Aman: Database diperbarui tanpa menghancurkan data lama!")