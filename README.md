# Prioritas Poli Jantung

Prototipe aplikasi web untuk memperkirakan risiko penyakit jantung dari 13 atribut klinis
memakai model Decision Tree. Dibuat untuk mata kuliah Kapita Selekta (B10CKP02405),
kasus **C2: RS Jantung Pratama Sentosa**.

> **Peringatan:** Ini prototipe akademik. Hasil prediksi **bukan diagnosis** dan tidak boleh
> dipakai langsung untuk keputusan klinis. Hanya memakai data fiktif atau dataset publik
> yang sudah dide-identifikasi.

## Tujuan
Membantu memprioritaskan antrean pemeriksaan lanjutan di poli jantung sebagai informasi
pendukung bagi tenaga medis, bukan menggantikan penilaian klinis.

## Fitur
- **Beranda:** informasi sistem, cara pakai, aturan penggunaan, dan profil tim.
- **Prediksi:** input 13 atribut klinis, validasi kelengkapan dan rentang, peluang,
  kategori risiko (rendah, sedang, tinggi), faktor yang paling berpengaruh, dan peringatan
  yang selalu tampil. Bila hasil pemeriksaan lanjutan (`ca` atau `thal`) belum ada,
  aplikasi memakai model tanpa kedua atribut itu disertai peringatan bahwa hasilnya
  kurang akurat.
- **Riwayat:** penyimpanan hasil ke CSV, serta unduhan Excel dan CSV.

## Alat dan versi
| Alat | Versi |
|---|---|
| Python | 3.11.9 |
| PyCaret | 3.3.2 |
| Streamlit | 1.66.0 |
| numpy / pandas / scikit-learn | 1.26.4 / 2.1.4 / 1.4.2 |
| pyarrow | 20.0.0 |
| openpyxl | 3.1.5 |

Daftar lengkap ada di `requirements.txt`.

## Cara menjalankan (Windows PowerShell)
1. Ambil repositori:
   ```powershell
   git clone https://github.com/AndiFahrul21/UAS-Kapita-Selekta-kelompok-C2.git
   cd UAS-Kapita-Selekta-kelompok-C2
   ```
2. Buat dan aktifkan lingkungan virtual:
   ```powershell
   python -m venv venv
   .\venv\Scripts\Activate.ps1
   ```
3. Pasang pustaka:
   ```powershell
   pip install -r requirements.txt
   ```
4. (Opsional) Latih ulang model: `python latih_model.py`.
   Model terlatih sudah tersedia di folder `models/`.
5. Jalankan aplikasi:
   ```powershell
   streamlit run app.py
   ```
6. Buka alamat yang tampil di terminal (biasanya http://localhost:8501).

Catatan: PyCaret 3.3.2 membutuhkan Python 3.9 sampai 3.11. Jangan memperbarui pip
di dalam lingkungan ini, dan pakai versi pustaka seperti pada `requirements.txt`.

## Struktur repositori
```
README.md, requirements.txt
app.py, bidang.py, halaman_prediksi.py, prediksi.py, riwayat.py, gaya.css   (aplikasi)
latih_model.py, cek_model.py, uji_prediksi.py, ringkas_metrik.py            (model dan pengujian)
.streamlit/config.toml              (tema)
data/dataset.csv                    (data uji)
models/                             (model terlatih dan metrics.json)
foto_pengembang/                    (foto tim)
```

## Pengujian
- `python cek_model.py`: menghitung peluang pasien contoh langsung dari berkas model,
  untuk dibandingkan dengan angka di aplikasi.
- `python uji_prediksi.py`: 16 skenario uji logika prediksi (16 dari 16 lulus).
- `python ringkas_metrik.py`: mencetak ringkasan metrik dari `models/metrics.json`.

## Data
- **Sumber:** UCI Heart Disease, Cleveland (303 baris, 14 atribut).
  Janosi, A., Steinbrunn, W., Pfisterer, M., & Detrano, R. (1989). Heart Disease [Dataset].
  UCI Machine Learning Repository. https://doi.org/10.24432/C52P4X
- **Lisensi:** Creative Commons Attribution 4.0 International (CC BY 4.0).
  https://creativecommons.org/licenses/by/4.0/
- Data sudah dide-identifikasi. Isian nama pasien di aplikasi hanya untuk nama rekaan
  atau kode (misalnya Pasien A).

## Hasil model
Model dilatih dengan PyCaret (Decision Tree), pembagian 80% data latih (242) dan 20% data
uji (61), serta validasi silang 10 lipatan (seed 42). Hasil pada data uji:

| Metrik | Nilai |
|---|---|
| Akurasi | 83,6% |
| Presisi | 82,1% |
| Sensitivitas (recall) | 82,1% |
| Spesifisitas | 84,8% |
| F1-score | 82,1% |

Confusion matrix (TN, FP, FN, TP): 28, 5, 5, 23. Validasi silang pada data latih:
akurasi 78,9% (simpangan baku 7,2), sensitivitas 73,9%, AUC 0,873. Data uji hanya
61 pasien, sehingga hasilnya bersifat awal. Rincian lengkap ada di `models/metrics.json`.

## Keterbatasan
- Data hanya 303 pasien dari satu pusat layanan, sehingga tidak digeneralisasi.
- Decision Tree dapat keliru pada nilai di dekat batas percabangan.
- Peluang model hanya memiliki sedikit nilai, sehingga kategori sedang jarang muncul.
- Batas kategori (0,40 dan 0,65) ditentukan dari nilai peluang model, bukan standar klinis.
- Aplikasi tidak diuji secara klinis maupun dengan tenaga medis.

## Pernyataan penggunaan AI
- **Alat:** Claude (Anthropic).
- **Bagian:** Bantuan menulis kode aplikasi Streamlit dan pelatihan model Decision Tree,
  serta menyusun draf teks proposal.
- **Verifikasi:** Seluruh kode dijalankan dan diuji (`uji_prediksi.py`, `cek_model.py`),
  angka dicocokkan dengan `models/metrics.json`, dan teks diperiksa serta disesuaikan
  oleh anggota kelompok. Seluruh anggota memahami isi proyek.

## Tim dan kontribusi
| Anggota | Peran | Kontribusi |
|---|---|---|
| Achmad Mauladi | Koordinator, pengembang data/model | Unggah Drive monitoring, pipeline PyCaret, validasi silang, metrik, faktor berpengaruh, berkas model dan metrik |
| Indah Dhiya Nabila H. | Analis kasus dan rumusan masalah | Analisis kebutuhan, etika data, rencana implementasi |
| Suci Pratiwi | Desain UI/UX | Perancangan desain dan prototipe awal |
| A. Fahrul | Perancang dan pengembang web | Pengembangan website, antarmuka Streamlit, validasi input, riwayat prediksi, banner peringatan |