# LMS V3.5 - AI Auto-Grader Platform

Platform Learning Management System (LMS) modern berbasis web yang dilengkapi dengan modul manajemen materi kuliah (.PDF) dan sistem evaluasi ujian campuran (Pilihan Ganda & Analisis Essay) yang dikoreksi secara otomatis menggunakan kecerdasan buatan LLM (Gemini-2.5-Flash).

## Fitur Utama (V3.5 Stable)
- **AI Auto-Grader (Gemini AI Integration):** Mengoreksi jawaban essay siswa secara otomatis dengan mendeteksi kemiripan esensi makna faktual, memberikan skor, tingkat kecocokan (%), beserta analisis mendalam.
- **Kombinasi Tipe Soal:** Mendukung pembuatan soal Pilihan Ganda (auto-koreksi instan tanpa memotong kuota API) dan Soal Analisis Essay berbasis AI.
- **Isolasi Kelas & Guru:** Fleksibilitas distribusi materi kuliah (.PDF) dan ruang ujian berdasarkan target kelas spesifik (TKJ 1, TKRO 1, dll).
- **Frontend Purifikasi (Vanilla CSS External):** Antarmuka responsif mobile-ready yang dibangun murni menggunakan kombinasi HTML5 dan External CSS murni tanpa overhead framework pihak ketiga.

## Tech Stack & Tools
- **Backend Architecture:** Python 3 & Flask Framework
- **Database Engine:** SQLite3 (Relational Database)
- **AI Engine:** Google GenAI SDK (Gemini-2.5-Flash Model)
- **Frontend Engine:** Vanilla HTML5 & Custom External CSS (`style.css`)
- **Deployment & Tunneling:** Linux Mint OS & Ngrok Secure Tunneling

## Prasyarat & Panduan Instalasi (Prerequisites & Setup)
Ikuti langkah-langkah di bawah ini untuk menjalankan project LMS V3.5 di lokal komputer/laptop Anda dari nol.

### 1. Install Tools yang Dibutuhkan (Prerequisites)
Pastikan sistem operasi Anda sudah terinstal Git, Python 3, Pip, dan Virtual Environment module. Untuk pengguna Linux (Ubuntu/Debian/Mint), jalankan perintah berikut di terminal:
```bash
sudo apt update
sudo apt install git python3 python3-pip python3-venv -y
```
### 2. Clone Repository
Unduh berkas project ini dari GitHub ke direktori lokal Anda menggunakan Git:
```bash
git clone [https://github.com/alvianadiwibowo/EssayAutoCorrection-AI-Flask.git](https://github.com/alvianadiwibowo/EssayAutoCorrection-AI-Flask.git)
cd EssayAutoCorrection-AI-Flask
```
### 3. Setup Virtual Environment (Karantina Library)
Sangat direkomendasikan untuk membuat Virtual Environment agar modul python project tidak bertabrakan dengan modul sistem bawaan:
```bash
# Membuat folder environment bernama 'env'
python3 -m venv env
# Mengaktifkan Virtual Environment
source env/bin/activate
```
### 4. Install Dependencies & Module Python
Instal seluruh library pendukung yang dibutuhkan oleh sistem Flask dan Gemini AI:
```bash
pip install flask google-genai python-dotenv werkzeug
```
### 5. Konfigurasi Environment Variables (.env)
Project ini membutuhkan akses API Key dari Google Gemini.
1. Buat berkas baru bernama .env di folder utama project (sejajar dengan app.py).
2. Isi berkas .env tersebut dengan format seperti berikut:
```bash
API_KEY_[ANDA]=Masukan_API_Key_Gemini_Anda_Disini
API_KEY_[ANDA]=Masukan_API_Key_Kedua_Jika_Ada
```
(Catatan: Anda minimal harus mengisi satu API Key pada variabel API_KEY_[ANDA] agar fitur koreksi essay otomatis dapat berjalan).
### 6. Inisialisasi Database (Setup Awal)
Sebelum menyalakan server, Anda wajib membangun struktur database SQLite3 terlebih dahulu untuk menciptakan tabel akun default (Guru & Murid) serta tabel penampung data:
```bash
python3 setup_db.py
```
(Pastikan muncul pesan log: "✅ Database diperbarui tanpa menghancurkan data lama!").
### 7. Jalankan Aplikasi Web LMS
Setelah seluruh konfigurasi selesai, nyalakan server lokal Flask dengan perintah:
```bash
python3 app.py
```
Buka browser Anda lalu akses URL: http://127.0.0.1:5000

🔑 Akun Uji Coba Default (Testing Accounts)
Gunakan akun di bawah ini yang sudah terdaftar di database untuk mencoba sistem:
- Akun Guru: Username: guru_bima | Password: 123
- Akun Siswa (TKJ): Username: faisal1 | Password: 123 (Kelas: TKJ 1)
- Akun Siswa (TKRO): Username: hamid1 | Password: 123 (Kelas: TKRO 1)

## Struktur Folder Project
```text
📂 EssayAutoCorrection-AI-Flask
 ┣ 📂 static/
 ┃ ┣ 📂 uploads/materi/      # Direktori penyimpanan fisik file PDF
 ┃ ┗ 📄 style.css            # Custom External CSS (Responsive Layout)
 ┣ 📂 templates/             # Direktori Core HTML5 User Interface
 ┃ ┣ 📄 login.html
 ┃ ┣ 📄 guru_hub.html
 ┃ ┣ 📄 guru_materi.html
 ┃ ┣ 📄 guru_ujian.html
 ┃ ┣ 📄 murid_hub.html
 ┃ ┣ 📄 murid_matkul.html
 ┃ ┗ 📄 murid_ujian.html
 ┣ 📄 app.py                 # Core Backend Flask Server Logic
 ┣ 📄 setup_db.py            # Database Schema & Initialization
 ┗ 📄 .gitignore             # Git Security Guard Exclusion List
