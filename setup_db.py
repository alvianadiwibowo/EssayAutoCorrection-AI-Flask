import sqlite3
import os

# ! TOMBOL NUKLIR
# * CATATAN PENTING: Fugsi Sensitif. Ini Buat Eksperiman Aja, Pas Implementasi Matiin Pake #
#if os.path.exists('sekolah.db'):
   #os.remove('sekolah.db')

conn = sqlite3.connect('sekolah.db')
cursor = conn.cursor()

# BUAT TABEL.  IF NOT EXIST: Kalo di Run, Tabel Yang Ada Bakal Di Abaikan
cursor.execute('''CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT UNIQUE, password TEXT, role TEXT, kelas TEXT)''') #TABEL USER: Buat Data LOgin

cursor.execute('''CREATE TABLE IF NOT EXISTS ujian (
    id INTEGER PRIMARY KEY AUTOINCREMENT, token TEXT UNIQUE, mata_pelajaran TEXT, jam_mulai TEXT, jam_selesai TEXT, pembuat TEXT)''') #UJIAN: Info UJian & Token

cursor.execute('''CREATE TABLE IF NOT EXISTS materi (
    id INTEGER PRIMARY KEY AUTOINCREMENT, 
    judul TEXT, 
    nama_file TEXT, 
    mata_pelajaran TEXT,
    kelas_target TEXT, 
    guru_username TEXT,
    tanggal_upload TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''') #MATERI: FIle PDF, judul, Gurunya, Khusus Kelas MAna

cursor.execute('''CREATE TABLE IF NOT EXISTS soal_ujian (
    id INTEGER PRIMARY KEY AUTOINCREMENT, token_ujian TEXT, nomor_soal INTEGER,
    tipe_soal TEXT, pertanyaan TEXT, opsi_a TEXT, opsi_b TEXT, opsi_c TEXT, opsi_d TEXT, kunci_jawaban TEXT)''') #UJIAN: Nyimpen Soal dan Jawaban -> Token Ujian

cursor.execute('''CREATE TABLE IF NOT EXISTS jawaban_siswa (
    id INTEGER PRIMARY KEY AUTOINCREMENT, token_ujian TEXT, username TEXT, kelas TEXT, nomor_soal INTEGER, jawaban TEXT,
    status TEXT DEFAULT 'Belum Dikoreksi', kecocokan INTEGER, rekomendasi_nilai INTEGER, analisis TEXT)''') # Jawaban Murid

# 4. BUAT MASUKIN DATA
akun_default = [
    ('guru_bima', '123', 'guru', 'Guru'), ('guru_hamid', '123', 'guru', 'Guru'),
    ('faisal1', '123', 'murid', 'TKJ 1'), ('bila1', '123', 'murid', 'TKJ 1'), ('hamid1', '123', 'murid', 'TKRO 1')
]
cursor.executemany("INSERT OR IGNORE INTO users (username, password, role, kelas) VALUES (?, ?, ?, ?)", akun_default)

conn.commit()
conn.close()
print("✅ Sistem Aman: Database diperbarui tanpa menghancurkan data lama!")