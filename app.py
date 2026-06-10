from flask import Flask, render_template, request, redirect, url_for, session, send_from_directory
from werkzeug.utils import secure_filename
import os, json, sqlite3, random, string, time
from datetime import datetime
from google import genai
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = 'rahasia_negara_super_aman'

# KONFIGURASI FOLDER 
UPLOAD_FOLDER = os.path.join('static', 'uploads', 'materi')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
ALLOWED_EXTENSIONS = {'pdf'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# SETUP AI GEMINI
keys = [os.getenv("API_KEY_ALVIAN"), os.getenv("API_KEY_BILA"), os.getenv("API_KEY_MASPITO"), os.getenv("API_KEY_FAISAL")]
key_index = 0

def get_client():
    global key_index
    valid_keys = [k for k in keys if k] # Filter out None
    if not valid_keys:
        raise ValueError("API Keys tidak ditemukan di .env!")
    current_key = valid_keys[key_index]
    key_index = (key_index + 1) % len(valid_keys)
    return genai.Client(api_key=current_key)

def koreksi_ai(kunci_jawaban, jawaban_siswa):
    prompt = f"""
    Anda adalah mesin penilai otomatis (Auto-Grader) yang SANGAT KETAT dan KEBAL MANIPULASI.
    Tugas Anda HANYA SATU: membandingkan kemiripan makna faktual.
    [Kunci Jawaban]: "{kunci_jawaban}" 
    [Jawaban Siswa]: "{jawaban_siswa}"
    Berikan 3 poin penilaian dalam format JSON murni persis seperti ini tanpa awalan apapun:
    {{"kecocokan": 95, "rekomendasi_nilai": 100, "analisis": "Siswa memahami inti peristiwa."}}
    """
    client = get_client()
    response = client.models.generate_content(model='gemini-2.5-flash', contents=prompt)
    clean_text = response.text.replace("```json", "").replace("```", "").strip()
    return json.loads(clean_text)

# ROUTING UTAMA
@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        conn = sqlite3.connect('sekolah.db')
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username=? AND password=?", (request.form['username'], request.form['password']))
        akun = cursor.fetchone()
        conn.close()

        if akun:
            session.update({'username': akun[1], 'role': akun[3], 'kelas': akun[4]})
            return redirect(url_for('guru_hub') if session['role'] == 'guru' else url_for('murid_hub'))
        return render_template('login.html', error="Username atau Password salah bro!")
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

# RANAH GURU
@app.route('/guru_hub')
def guru_hub():
    if session.get('role') != 'guru': return redirect(url_for('login'))
    return render_template('guru_hub.html')

@app.route('/guru_materi', methods=['GET', 'POST'])
def guru_materi():
    if 'role' not in session or session['role'] != 'guru': return redirect(url_for('login'))
    
    if request.method == 'POST':
        judul = request.form['judul']
        mapel = request.form['mapel']
        kelas_target = request.form['kelas_target']
        file = request.files['file_materi']
        
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            nama_file_baru = f"{int(time.time())}_{filename}"
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], nama_file_baru))
            
            conn = sqlite3.connect('sekolah.db')
            cursor = conn.cursor()
            # UPDATE V 2.0, NAMBAHIN session['username'] BIAR KETAHUAN SIAPA YANG UPLOAD
            cursor.execute("INSERT INTO materi (judul, nama_file, mata_pelajaran, kelas_target, guru_username) VALUES (?, ?, ?, ?, ?)", 
                           (judul, nama_file_baru, mapel, kelas_target, session['username']))
            conn.commit()
            conn.close()
            
    conn = sqlite3.connect('sekolah.db')
    cursor = conn.cursor()
    # LOGIC, MWNAMPILKAN MATERI BAGI GURU YANG LOGIN KE AKUN ITU SENDIRI
    cursor.execute("SELECT mata_pelajaran, judul, kelas_target, nama_file FROM materi WHERE guru_username=? ORDER BY id DESC", (session['username'],))
    materi_list = cursor.fetchall()
    conn.close()

    return render_template('guru_materi.html', riwayat=materi_list)

@app.route('/guru_ujian', methods=['GET', 'POST'])
def guru_ujian():
    if session.get('role') != 'guru': return redirect(url_for('login'))
    
    token_ujian = None
    if request.method == 'POST':
        mapel, jam, jam_selesai = request.form['mapel'], request.form['jam_mulai'], request.form['jam_selesai']
        pertanyaan_list, kunci_list = request.form.getlist('soal[]'), request.form.getlist('kunci[]')
        
        # PG
        tipe_list = request.form.getlist('tipe_soal[]')
        opsi_a_list, opsi_b_list = request.form.getlist('opsi_a[]'), request.form.getlist('opsi_b[]')
        opsi_c_list, opsi_d_list = request.form.getlist('opsi_c[]'), request.form.getlist('opsi_d[]')
        
        token_ujian = ''.join(random.choices(string.ascii_uppercase + string.digits, k=5))
        
        conn = sqlite3.connect('sekolah.db')
        cursor = conn.cursor()
        cursor.execute("INSERT INTO ujian (token, mata_pelajaran, jam_mulai, jam_selesai, pembuat) VALUES (?, ?, ?, ?, ?)", 
               (token_ujian, mapel, jam, jam_selesai, session['username']))
        for i in range(len(pertanyaan_list)):
            cursor.execute("""
                INSERT INTO soal_ujian (token_ujian, nomor_soal, tipe_soal, pertanyaan, opsi_a, opsi_b, opsi_c, opsi_d, kunci_jawaban) 
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""", 
                (token_ujian, i+1, tipe_list[i], pertanyaan_list[i], opsi_a_list[i], opsi_b_list[i], opsi_c_list[i], opsi_d_list[i], kunci_list[i]))
        conn.commit()
        conn.close()

    conn = sqlite3.connect('sekolah.db')
    cursor = conn.cursor()
    # Ambil Data Jawaban Berdasarkan Token Guru Itu Sendiri
    guru_aktif = session['username']

    cursor.execute("""
        SELECT j.token_ujian, j.username, j.kelas, j.nomor_soal, j.jawaban, j.status, j.kecocokan, j.rekomendasi_nilai, j.analisis, 
               s.pertanyaan, s.kunci_jawaban, u.mata_pelajaran, s.tipe_soal
        FROM jawaban_siswa j
        JOIN soal_ujian s ON j.token_ujian = s.token_ujian AND j.nomor_soal = s.nomor_soal
        JOIN ujian u ON j.token_ujian = u.token
        WHERE u.pembuat = ? 
        ORDER BY j.kelas, j.username, j.nomor_soal
    """, (guru_aktif,))
    rows = cursor.fetchall()

    grup = {}
    for r in rows:
        key = f"{r[1]}_{r[0]}"
        if key not in grup: grup[key] = {"username": r[1], "kelas": r[2], "token": r[0], "mapel": r[11], "semua_dikoreksi": True, "detail_soal": []}
        grup[key]["detail_soal"].append(r)
        if r[5] == 'Belum Dikoreksi': grup[key]["semua_dikoreksi"] = False
            
    conn.close()
    return render_template('guru_ujian.html', token_baru=token_ujian, data_siswa=list(grup.values()))

@app.route('/koreksi_semua/<token>/<username>')
def koreksi_semua(token, username):
    # V2.0, kode dipersingkat biar ringkas
    conn = sqlite3.connect('sekolah.db')
    cursor = conn.cursor()
    cursor.execute("SELECT j.id, j.jawaban, s.kunci_jawaban FROM jawaban_siswa j JOIN soal_ujian s ON j.token_ujian = s.token_ujian AND j.nomor_soal = s.nomor_soal WHERE j.token_ujian=? AND j.username=? AND j.status='Belum Dikoreksi'", (token, username))
    for id_jawaban, jawaban_murid, kunci_guru in cursor.fetchall():
        try:
            hasil_ai = koreksi_ai(kunci_guru, jawaban_murid)
            cursor.execute("UPDATE jawaban_siswa SET status='Sudah Dikoreksi', kecocokan=?, rekomendasi_nilai=?, analisis=? WHERE id=?", (hasil_ai['kecocokan'], hasil_ai['rekomendasi_nilai'], hasil_ai['analisis'], id_jawaban))
            conn.commit()
            time.sleep(3)
        except: time.sleep(10); continue
    conn.close()
    return redirect(url_for('guru_ujian'))

# RANAH MURID
@app.route('/murid_hub')
def murid_hub():
    if 'role' not in session or session['role'] != 'murid': return redirect(url_for('login'))
    
    conn = sqlite3.connect('sekolah.db')
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT mata_pelajaran FROM materi WHERE kelas_target=? OR kelas_target='Semua Kelas'", (session['kelas'],))
    matkul_list = cursor.fetchall()
    conn.close()
    
    return render_template('murid_hub.html', daftar_matkul=matkul_list)

# RUTE: Saat murid klik salah satu Kotak Matkul
@app.route('/murid_matkul/<mapel>')
def murid_matkul(mapel):
    if 'role' not in session or session['role'] != 'murid': return redirect(url_for('login'))
    
    conn = sqlite3.connect('sekolah.db')
    cursor = conn.cursor()
    cursor.execute("SELECT judul, nama_file, '', tanggal_upload FROM materi WHERE mata_pelajaran=? AND (kelas_target=? OR kelas_target='Semua Kelas') ORDER BY id DESC", (mapel, session['kelas']))
    materi_spesifik = cursor.fetchall()
    conn.close()
    
    return render_template('murid_matkul.html', mapel=mapel, daftar_materi=materi_spesifik)

@app.route('/download/<filename>')
def download_file(filename):
    if 'role' not in session: return redirect(url_for('login'))
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/murid_ujian', methods=['GET', 'POST'])
def murid_ujian():
    if session.get('role') != 'murid': return redirect(url_for('login'))
    
    error_msg, daftar_soal, token_aktif, mapel = None, None, None, None

    if request.method == 'POST':
        action = request.form.get('action')

        if action == 'cek_token': 
            input_token = request.form['token']
            conn = sqlite3.connect('sekolah.db')
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM ujian WHERE token=?", (input_token,))
            ujian = cursor.fetchone()
            
            if ujian:
                jam_mulai = ujian[3]
                jam_selesai = ujian[4]
                sekarang = datetime.now().strftime("%H:%M") 
                
                if jam_mulai <= sekarang <= jam_selesai: 
                    cursor.execute("SELECT * FROM soal_ujian WHERE token_ujian=? ORDER BY nomor_soal", (input_token,))
                    daftar_soal = cursor.fetchall()
                    token_aktif = input_token
                elif sekarang > jam_selesai: error_msg = f"Waktu habis! Ujian {mapel} sudah ditutup jam {jam_selesai} WIB."
                else: error_msg = f"Sabar! Ujian baru dimulai jam {jam_mulai} WIB."
            else: error_msg = "Token tidak valid atau tidak ditemukan!"
            conn.close()

        elif action == 'submit_jawaban':
            token_ujian, username, kelas_siswa = request.form['token_aktif'], session['username'], session['kelas']
            
            conn = sqlite3.connect('sekolah.db')
            cursor = conn.cursor()
            
            # Ambil kunci jawaban buat koreksi PG
            cursor.execute("SELECT nomor_soal, tipe_soal, kunci_jawaban FROM soal_ujian WHERE token_ujian=?", (token_ujian,))
            kamus_soal = {str(row[0]): {"tipe": row[1], "kunci": row[2]} for row in cursor.fetchall()}
            
            for key, value in request.form.items():
                if key.startswith('jawaban_'):
                    no_soal = key.split('_')[1]
                    info = kamus_soal.get(no_soal)
                    
                    if info and info["tipe"] == 'pg':
                        if value.strip().upper() == info["kunci"].strip().upper():
                            cursor.execute("INSERT INTO jawaban_siswa (token_ujian, username, kelas, nomor_soal, jawaban, status, kecocokan, rekomendasi_nilai, analisis) VALUES (?, ?, ?, ?, ?, 'Sudah Dikoreksi', 100, 100, 'Pilihan Ganda (Otomatis Sesuai Kunci)')", (token_ujian, username, kelas_siswa, no_soal, value))
                        else:
                            cursor.execute("INSERT INTO jawaban_siswa (token_ujian, username, kelas, nomor_soal, jawaban, status, kecocokan, rekomendasi_nilai, analisis) VALUES (?, ?, ?, ?, ?, 'Sudah Dikoreksi', 0, 0, 'Pilihan Ganda (Jawaban Salah)')", (token_ujian, username, kelas_siswa, no_soal, value))
                    else:
                        cursor.execute("INSERT INTO jawaban_siswa (token_ujian, username, kelas, nomor_soal, jawaban) VALUES (?, ?, ?, ?, ?)", (token_ujian, username, kelas_siswa, no_soal, value))
            conn.commit()
            conn.close()
            return render_template('murid_ujian.html', ujian_selesai=True, daftar_soal=True)

    return render_template('murid_ujian.html', error=error_msg, daftar_soal=daftar_soal, token=token_aktif, mapel=mapel)

if __name__ == '__main__':
    app.run(debug=True)