# Catch The Ball - Mini Game Berbasis Warna Tangan

Project 1 mata kuliah Pengolahan Citra Digital.

Ini mini game sederhana yang dikontrol pakai **tangan** lewat webcam, tanpa keyboard atau mouse. Pemain memakai sarung tangan berwarna biru, lalu komputer mendeteksi posisi sarung tangan itu untuk menggerakkan papan di bawah layar. Tugas pemain: jaga supaya bola yang memantul tidak jatuh.

## Tampilan Game

<!-- Tempel screenshot game di sini: simpan gambarnya di folder images/ lalu sesuaikan nama file -->
![Tampilan game](images/tampilan-game.png)

*Kiri: jendela Game. Kanan: jendela Kamera & Mask (hasil deteksi warna).*

## Fitur

- Papan dikontrol dengan gerakan tangan (kiri dan kanan)
- Bola memantul di dinding dan papan
- Setiap bola kena papan, skor bertambah dan bola makin cepat
- Ada sistem nyawa dan layar Game Over
- Dua jendela: satu untuk game, satu untuk melihat kamera dan mask (hasil deteksi warna)
- Kalibrasi warna dengan menekan satu tombol, jadi bisa pakai sarung tangan warna lain

## Cara Kerjanya

Deteksi tangan memakai beberapa teknik pengolahan citra yang dipelajari di kelas:

1. **Flip frame**: gambar kamera dicerminkan supaya gerakan tangan sama arahnya dengan layar.
2. **Gaussian blur**: menghaluskan gambar supaya noise kamera berkurang.
3. **Konversi ke HSV dan `inRange`**: memisahkan piksel yang warnanya biru dari sisa gambar. Hasilnya berupa mask (putih = terdeteksi, hitam = bukan).
4. **Morfologi (closing dan opening)**: menutup lubang kecil di dalam mask dan menghapus bintik noise di luarnya.
5. **Contour dan centroid**: dicari objek terbesar di mask (dianggap sebagai tangan), lalu dihitung titik tengahnya. Posisi horizontal titik itu dipakai untuk menggerakkan papan.

## Sarung Tangan yang Dipakai

<!-- Tempel foto sarung tangan di sini -->
![Sarung tangan](images/sarung-tangan.jpg)

Sarung tangan rajut biru kobalt polos. Warnanya satu rata dan tidak mengkilap, jadi mudah dideteksi kamera. Warna biru dipilih karena jauh dari warna kulit, sehingga wajah dan tangan yang tidak tertutup sarung tangan tidak ikut terdeteksi.

## Asset

<!-- Tempel gambar background atau asset lain di sini -->
![Background game](images/background.jpg)

Background game memakai gambar `bg.jpg`. Gambar ini otomatis digelapkan sedikit oleh program supaya bola dan papan tetap terlihat jelas. Kalau file `bg.jpg` tidak ada, game memakai background gradasi biru gelap.

Sumber gambar: _isi sumber atau pembuat gambar_

## Kebutuhan

- Python 3.x
- Webcam
- Sarung tangan atau benda berwarna biru polos (disarankan yang tidak mengkilap)
- Library:
  - `opencv-python`
  - `numpy`

Install library dengan:

```
pip install opencv-python numpy
```

## Cara Menjalankan

1. Clone atau download repo ini.
2. Install library seperti di atas.
3. Pastikan `bg.jpg` ada di folder yang sama dengan `project1-game.py`.
4. Jalankan file game:

```
python project1-game.py
```

Bisa juga dibuka di Spyder lalu tekan F5.

Kalau jendela video tidak muncul di Spyder, coba jalankan lewat terminal sistem, atau pilih *Run > Configuration per file > Execute in an external system terminal*.

## Cara Bermain

1. Pakai sarung tangan biru, lalu duduk di depan webcam dengan latar belakang yang tidak ada benda birunya.
2. Tekan **Spasi** untuk mulai.
3. Gerakkan tangan ke kiri dan kanan untuk menggerakkan papan.
4. Pantulkan bola sebanyak mungkin. Bola makin cepat tiap kena papan.
5. Kalau nyawa habis, game selesai. Tekan **Spasi** untuk main lagi.

Bagian papan yang terkena bola mempengaruhi arah pantulan: kena tengah papan, bola memantul lurus. Kena pinggir papan, bola memantul miring.

## Tombol

| Tombol | Fungsi |
|--------|--------|
| Spasi | Mulai atau main lagi |
| C | Kalibrasi warna |
| Q | Keluar |

Klik dulu salah satu jendela game supaya tombolnya terbaca.

## Kalibrasi Warna

Default-nya game mendeteksi warna biru. Kalau sarung tangan Anda warnanya lain, atau tangan tidak terdeteksi:

1. Lihat jendela **Kamera & Mask**. Ada kotak kuning di tengah gambar kamera.
2. Taruh sarung tangan di dalam kotak kuning itu.
3. Tekan **C**.

Kalau mau mengatur manual, ubah nilai `LOWER` dan `UPPER` di bagian pengaturan pada `project1-game.py`. Nilainya dalam format HSV OpenCV (H: 0-179, S: 0-255, V: 0-255).

## Tips Supaya Deteksi Bagus

- Pakai pencahayaan yang cukup dan merata dari depan.
- Hindari baju atau benda lain yang berwarna biru di dekat kamera, karena ikut terdeteksi.
- Pilih sarung tangan yang satu warna dan tidak mengkilap.
- Lihat jendela mask: hanya sarung tangan yang boleh putih.

## Pengaturan Game

Beberapa nilai bisa diubah di bagian paling atas `project1-game.py`:

| Nama | Fungsi |
|------|--------|
| `PAPAN_W` | Lebar papan (makin kecil makin susah) |
| `KECEPATAN_AWAL` | Kecepatan bola di awal |
| `KECEPATAN_MAKS` | Batas kecepatan bola |
| `NAIK_PAPAN` | Seberapa besar kecepatan naik tiap kena papan |
| `NYAWA_AWAL` | Jumlah nyawa |
| `LOWER` dan `UPPER` | Rentang warna yang dideteksi |

## Struktur File

```
.
├── project1-game.py        # kode utama game
├── bg.jpg                  # gambar background game
├── images/                 # gambar-gambar untuk README
│   ├── tampilan-game.png
│   ├── sarung-tangan.jpg
│   └── background.jpg
└── README.md
```

## Masalah yang Mungkin Muncul

- **Kamera tidak terbuka**: ubah `SUMBER_VIDEO = 0` jadi `1`, atau tutup aplikasi lain yang sedang memakai kamera.
- **Tangan tidak terdeteksi**: lakukan kalibrasi warna (tombol C) dan cek pencahayaan.
- **Papan bergetar**: deteksi warna kurang stabil, coba perbaiki pencahayaan atau singkirkan benda lain yang warnanya mirip.
- **Error `No module named cv2`**: install ulang dengan `pip install opencv-python`.

## Dibuat Oleh

- Nama: _isi nama_
- NIM: _isi NIM_
- Mata kuliah: Pengolahan Citra Digital
