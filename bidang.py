"""bidang.py - definisi isian form, label, dan contoh pasien."""

# (judul kelompok, [isian]). jenis: angka / radio / pilih.
GRUP = [
    ("Data umum", [
        {"id": "nama", "label": "Nama pasien", "jenis": "teks",
         "bantuan": "Opsional. Pakai nama rekaan atau kode, misalnya "
                    "\"Pasien A\"."},
        {"id": "age", "label": "Usia", "jenis": "angka", "step": 1,
         "format": "%d", "bantuan": "tahun, 20 sampai 100"},
        {"id": "sex", "label": "Jenis kelamin", "jenis": "radio",
         "pilihan": [(0, "Perempuan"), (1, "Laki-laki")]},
    ]),
    ("Keluhan dan tanda vital", [
        {"id": "cp", "label": "Jenis nyeri dada", "jenis": "pilih",
         "pilihan": [(1, "Angina tipikal"), (2, "Angina atipikal"),
                     (3, "Nyeri non-angina"), (4, "Tanpa gejala nyeri")],
         "bantuan": "Pada data latih, \"tanpa gejala nyeri\" justru paling "
                    "sering berkaitan dengan penyakit jantung (73%), jadi "
                    "bukan berarti aman."},
        {"id": "trestbps", "label": "Tekanan darah istirahat",
         "jenis": "angka", "step": 1, "format": "%d",
         "bantuan": "mm Hg, 80 sampai 220"},
        {"id": "chol", "label": "Kolesterol serum", "jenis": "angka",
         "step": 1, "format": "%d", "bantuan": "mg/dl, 100 sampai 600"},
        {"id": "fbs", "label": "Gula darah puasa di atas 120 mg/dl",
         "jenis": "radio", "pilihan": [(0, "Tidak"), (1, "Ya")]},
    ]),
    ("Pemeriksaan jantung", [
        {"id": "restecg", "label": "Hasil EKG istirahat", "jenis": "pilih",
         "pilihan": [(0, "Normal"), (1, "Kelainan gelombang ST-T"),
                     (2, "Hipertrofi ventrikel kiri")]},
        {"id": "thalach", "label": "Detak jantung maksimum",
         "jenis": "angka", "step": 1, "format": "%d",
         "bantuan": "bpm, 60 sampai 220"},
        {"id": "exang", "label": "Nyeri dada saat olahraga",
         "jenis": "radio", "pilihan": [(0, "Tidak"), (1, "Ya")]},
        {"id": "oldpeak", "label": "Depresi segmen ST (oldpeak)",
         "jenis": "angka", "step": 0.1, "format": "%.1f",
         "bantuan": "0 sampai 7"},
        {"id": "slope", "label": "Kemiringan segmen ST", "jenis": "pilih",
         "pilihan": [(1, "Menanjak"), (2, "Datar"), (3, "Menurun")]},
    ]),
    ("Pemeriksaan lanjutan", [
        {"id": "ca", "label": "Pembuluh darah utama pada fluoroskopi",
         "jenis": "pilih",
         "pilihan": [(0, "0"), (1, "1"), (2, "2"), (3, "3")],
         "bantuan": "Jumlah pembuluh darah utama yang terlihat."},
        {"id": "thal", "label": "Hasil uji thalium (thal)",
         "jenis": "pilih",
         "pilihan": [(3, "Normal"), (6, "Cacat tetap"),
                     (7, "Cacat reversibel")],
         "bantuan": "Uji perfusi thalium, bukan kelainan darah thalassemia."},
    ]),
]

# Nama pendek untuk grafik faktor berpengaruh dan riwayat
LABEL = {
    "age": "Usia", "sex": "Jenis kelamin", "cp": "Jenis nyeri dada",
    "trestbps": "Tekanan darah", "chol": "Kolesterol",
    "fbs": "Gula darah puasa", "restecg": "EKG istirahat",
    "thalach": "Detak jantung maks.", "exang": "Nyeri saat olahraga",
    "oldpeak": "Depresi ST (oldpeak)", "slope": "Kemiringan ST",
    "ca": "Pembuluh darah utama", "thal": "Uji thalium",
}

# Tombol "Isi contoh pasien". oldpeak harus float (isian berjenis desimal).
CONTOH = {"age": 58, "sex": 1, "cp": 4, "trestbps": 140, "chol": 260,
          "fbs": 0, "restecg": 2, "thalach": 120, "exang": 1,
          "oldpeak": 2.0, "slope": 2, "ca": 2, "thal": 7}