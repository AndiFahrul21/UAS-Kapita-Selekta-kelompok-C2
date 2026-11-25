# Prioritas Poli Jantung

Prototipe aplikasi web untuk memperkirakan risiko penyakit jantung dari 13 atribut klinis
memakai model Decision Tree. Dibuat untuk mata kuliah Kapita Selekta (B10CKP02405),
kasus **C2: RS Jantung Pratama Sentosa**.

> **Peringatan:** Ini prototipe akademik. Hasil prediksi **bukan diagnosis** dan tidak boleh
> dipakai langsung untuk keputusan klinis. Hanya memakai data fiktif atau dataset publik
> yang sudah dide-identifikasi.

## Branch
- `v2` (branch ini): versi yang sesuai dengan laporan proposal (alur pelatihan dan angka evaluasi sama).
- `main`: versi awal dengan alur pelatihan dan dataset berbeda.

## Tujuan
Membantu memprioritaskan antrean pemeriksaan lanjutan di poli jantung sebagai informasi
pendukung bagi tenaga medis, bukan menggantikan penilaian klinis.

## Fitur
- **Beranda:** informasi sistem, cara pakai, aturan penggunaan, dan profil tim.
- **Prediksi:** input 13 atribut klinis (semua wajib diisi), validasi kelengkapan dan rentang,
  peluang, kategori risiko (rendah, sedang, tinggi), jalur keputusan pasien, faktor yang paling
  berpengaruh, dan peringatan yang selalu tampil.
- **Riwayat:** penyimpanan hasil ke CSV (`history.csv`), serta unduhan Excel dan CSV.

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
1. Ambil repositori (branch `v2`):
   ```powershell
   git clone -b v2 https://github.com/AndiFahrul21/UAS-Kapita-Selekta-kelompok-C2.git
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
data/dataset.csv                    (data latih dan uji)
models/                             (model terlatih dan metrics.json)
foto_pengembang/                    (foto tim)
```

## Data
- **Sumber:** UCI Heart Disease, Cleveland.
  Janosi, A., Steinbrunn, W., Pfisterer, M., & Detrano, R. (1989). Heart Disease [Dataset].
  UCI Machine Learning Repository. https://doi.org/10.24432/C52P4X
- **Lisensi:** Creative Commons Attribution 4.0 International (CC BY 4.0).
  https://creativecommons.org/licenses/by/4.0/
- **Berkas yang dipakai di branch ini:** salinan berkode ulang dari data di atas (303 baris,
  14 kolom). Berkas ini berbeda satu baris dari berkas UCI asli. Pada pelatihan, 1 baris
  duplikat dihapus, sehingga **302 baris** dipakai.
- **Pembersihan:** `ca` = 4 dan `thal` = 0 (kode data hilang) diubah menjadi kosong
  (masing-masing 4 dan 2 baris); label `target` dibalik karena pada berkas ini 1 berarti
  tidak sakit, sehingga 1 = ada penyakit jantung (138 sakit, 164 tidak sakit).
- Formulir aplikasi memakai kode UCI (misalnya `thal` 3, 6, 7); `prediksi.py`
  menerjemahkannya ke kode berkas data sebelum dikirim ke model.
- Isian nama pasien di aplikasi hanya untuk nama rekaan atau kode (misalnya Pasien A).

## Model
Decision Tree (PyCaret), data dibagi 80% latih (241) dan 20% uji (61), validasi silang
10 lipatan, seed 42, tuning dengan metrik F1 (`tune_model`, 30 iterasi). Pengaturan akhir:
kriteria entropy, `max_depth` 7, `min_samples_leaf` 3. Pohon yang terbentuk hanya sedalam
3 tingkat dengan 4 ujung, dan hanya memakai tiga atribut:

| Faktor | Pengaruh |
|---|---|
| Uji thalium (`thal`) | 72% |
| Pembuluh darah utama (`ca`) | 15% |
| Jenis nyeri dada (`cp`) | 13% |

| Ujung | Syarat | Pasien latih (sakit) | Peluang | Kategori |
|---|---|---|---|---|
| 1 | Uji thalium bukan normal | 109 (84) | 77,1% | Tinggi |
| 2 | Thalium normal, pembuluh darah 0 | 96 (10) | 10,4% | Rendah |
| 3 | Thalium normal, pembuluh darah 1–3, nyeri dada bukan non-angina | 26 (16) | 61,5% | Sedang |
| 4 | Thalium normal, pembuluh darah 1–3, nyeri dada non-angina | 10 (0) | 0,0% | Rendah |

Batas kategori: rendah di bawah 0,40, sedang 0,40 sampai kurang dari 0,65, tinggi 0,65 ke atas
(ditentukan dari nilai peluang ujung pohon, bukan standar klinis).

## Hasil model
Hasil pada data uji (61 pasien):

| Metrik | Nilai |
|---|---|
| Akurasi | 73,8% |
| Presisi | 66,7% |
| Sensitivitas (recall) | 85,7% |
| Spesifisitas | 63,6% |
| F1-score | 75,0% |

Confusion matrix (TN, FP, FN, TP): 21, 12, 4, 24. Validasi silang 10 lipatan pada data latih:
akurasi 78,0% (simpangan baku 8,7), sensitivitas 84,5%, AUC 0,820. Data uji hanya 61 pasien,
sehingga hasilnya bersifat awal. Rincian lengkap ada di `models/metrics.json`.

## Pengujian
- `python uji_prediksi.py`: 22 skenario uji logika prediksi dan validasi (22 dari 22 lulus).
- `python cek_model.py`: membandingkan peluang model yang dipanggil langsung dengan peluang
  yang dipakai aplikasi.
- `python ringkas_metrik.py`: mencetak ringkasan metrik dari `models/metrics.json`.

## Keterbatasan
- Data hanya 302 pasien dari satu pusat layanan, sehingga tidak digeneralisasi.
- Pohon hanya memiliki 4 ujung, sehingga peluang hanya bernilai 4 macam dan pasien yang
  berbeda jauh dapat memperoleh peluang yang sama.
- Decision Tree dapat keliru pada nilai di dekat batas percabangan, dan hasilnya dapat
  berubah bila data latih sedikit berbeda.
- Faktor berpengaruh bersifat umum untuk model, bukan alasan khusus tiap pasien, dan bukan
  hubungan sebab-akibat.
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