from prediksi import prediksi, validasi

BASE = {"age": 58, "sex": 1, "cp": 4, "trestbps": 140, "chol": 260,
        "fbs": 0, "restecg": 2, "thalach": 120, "exang": 1,
        "oldpeak": 2.0, "slope": 2, "ca": 2, "thal": 7}
hasil = []


def cek(nama, kondisi):
    hasil.append(bool(kondisi))
    print(("LULUS  " if kondisi else "GAGAL  ") + nama)


def dekat(a, b):
    return abs(a - b) < 0.001


# Tinggi: thalium bukan normal (daun 84 dari 109)
h = prediksi(BASE)
cek("Tinggi: peluang 0,7706", dekat(h["peluang"], 84 / 109))
cek("Tinggi: kategori tinggi", h["kategori"] == "tinggi")
cek("Tinggi: ujung pohon 84 dari 109", h["ujung"] == {"n": 109, "sakit": 84})
cek("Tinggi: tanpa catatan model", h["catatan_model"] == "")

h = prediksi({**BASE, "thal": 6})
cek("Cacat tetap: masuk kelompok tinggi", h["kategori"] == "tinggi")

# Sedang: thalium normal, pembuluh darah >= 1, nyeri dada bukan non-angina
h = prediksi({**BASE, "thal": 3})
cek("Sedang: peluang 0,6154", dekat(h["peluang"], 16 / 26))
cek("Sedang: kategori sedang", h["kategori"] == "sedang")
cek("Sedang: ujung pohon 16 dari 26", h["ujung"] == {"n": 26, "sakit": 16})

# Rendah: thalium normal dan pembuluh darah 0
h = prediksi({**BASE, "thal": 3, "ca": 0})
cek("Rendah: peluang 0,1042", dekat(h["peluang"], 10 / 96))
cek("Rendah: kategori rendah", h["kategori"] == "rendah")
cek("Rendah: ujung pohon 10 dari 96", h["ujung"] == {"n": 96, "sakit": 10})

# Rendah 0%: thalium normal, pembuluh darah >= 1, nyeri non-angina
h = prediksi({**BASE, "thal": 3, "cp": 3})
cek("Rendah 0%: peluang 0,0", dekat(h["peluang"], 0.0))
cek("Rendah 0%: kategori rendah", h["kategori"] == "rendah")

# Valid tetapi di luar rentang data latih
h = prediksi({**BASE, "age": 90})
cek("Usia 90: peringatan di luar rentang latih", "age" in h["di_luar_rentang"])

# Validasi
cek("Usia 300 ditolak", set(validasi({**BASE, "age": 300})) == {"age"})
cek("Usia kosong ditolak", set(validasi({**BASE, "age": None})) == {"age"})
cek("Teks 'abc' ditolak", set(validasi({**BASE, "age": "abc"})) == {"age"})
cek("thal=5 ditolak", set(validasi({**BASE, "thal": 5})) == {"thal"})
cek("ca kosong ditolak", set(validasi({**BASE, "ca": None})) == {"ca"})
cek("thal kosong ditolak", set(validasi({**BASE, "thal": None})) == {"thal"})
cek("Data lengkap valid", validasi(BASE) == {})

try:
    prediksi({**BASE, "age": 300})
    cek("prediksi() menolak input tidak valid", False)
except ValueError:
    cek("prediksi() menolak input tidak valid", True)

print(f"\n{sum(hasil)} dari {len(hasil)} skenario lulus")