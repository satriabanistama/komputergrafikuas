# Mengimpor modul yang diperlukan dari Flask
from flask import Flask, request, render_template, jsonify
# Mengimpor modul OpenCV untuk memanipulasi gambar
import cv2
# Mengimpor modul numpy untuk bekerja dengan array
import numpy as np
# Mengimpor modul base64 untuk mengkonversi gambar menjadi string base64
import base64
# Mengimpor modul io untuk membaca dan menulis data biner
import io

# Membuat instance Flask
app = Flask(__name__)

# Fungsi untuk memotong gambar berdasarkan posisi dan ukuran
def crop_by_position(img, position, size):
    height, width = img.shape[:2]
    return {
        'top_left': img[:size, :size],
        'top_center': img[:size, width // 2 - size // 2:width // 2 + size // 2],
        'top_right': img[:size, width - size:width],
        'center_left': img[height // 2 - size // 2:height // 2 + size // 2, :size],
        'center': img[height // 2 - size // 2:height // 2 + size // 2, width // 2 - size // 2:width // 2 + size // 2],
        'center_right': img[height // 2 - size // 2:height // 2 + size // 2, width - size:width],
        'bottom_left': img[height - size:height, :size],
        'bottom_center': img[height - size:height, width // 2 - size // 2:width // 2 + size // 2],
        'bottom_right': img[height - size:height, width - size:width],
    }[position]

# Fungsi untuk memotong gambar dan mengembalikan hasilnya dalam format byte
def crop_image(img, position, size):
    cropped_img = crop_by_position(img, position, size)
    _, buffer = cv2.imencode('.jpg', cropped_img)
    cropped_bytes = base64.b64encode(buffer)
    return cropped_bytes

# Route utama untuk menerima permintaan GET dan POST
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'GET':
        return render_template('index.html')  # Menampilkan halaman HTML

    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'})  # Menampilkan pesan kesalahan jika tidak ada file yang diunggah

    file = request.files['file']  # Mendapatkan file yang diunggah dari permintaan
    position = request.form['position']  # Mendapatkan posisi potongan gambar dari formulir
    size = int(request.form['size'])  # Mendapatkan ukuran potongan gambar dari formulir

    if file.filename == '':
        return jsonify({'error': 'No file selected'})  # Menampilkan pesan kesalahan jika tidak ada file yang dipilih

    if file and allowed_file(file.filename):  # Memeriksa apakah file yang diunggah adalah file gambar yang diperbolehkan
        img = cv2.imdecode(np.frombuffer(file.read(), np.uint8), cv2.IMREAD_UNCHANGED)  # Membaca dan mendecode gambar menggunakan OpenCV
        cropped_bytes = crop_image(img, position, size)  # Memotong gambar dan mengkonversi hasilnya menjadi string base64
        return cropped_bytes


# Fungsi untuk memeriksa apakah ekstensi file gambar diperbolehkan
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'png', 'jpg', 'jpeg'}

# Menjalankan aplikasi Flask
if __name__ == '__main__':
    app.run()
