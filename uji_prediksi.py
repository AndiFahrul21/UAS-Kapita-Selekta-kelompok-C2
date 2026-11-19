from prediksi import prediksi, validasi

DASAR = {"age": 58, "sex": 1, "cp": 4, "trestbps": 140, "chol": 260,
         "fbs": 0, "restecg": 2, "thalach": 120, "exang": 1,
         "oldpeak": 2.0, "slope": 2}
hasil = []


def cek(nama, kondisi):
    hasil.append(bool(kondisi))
    print(("LULUS  " if kondisi else "GAGAL  ") + nama)


# Pasien lengkap -> model lengkap
h = prediksi({**DASAR, "ca": 2, "thal": 7})
cek("Lengkap: memakai model lengkap", h["model"] == "lengkap")
cek("Lengkap: peluang 1,0 (toleransi 0,001)", abs(h["peluang"] - 1.0) < 0.001)
cek("Lengkap: kategori tinggi", h["kategori"] == "tinggi")
cek("Lengkap: ujung pohon 41 dari 41", h["ujung"] == {"n": 41, "sakit": 41})

# ca dan thal kosong -> model dasar
h = prediksi({**DASAR, "ca": None, "thal": None})
cek("Kosong: memakai model dasar", h["model"] == "dasar")
cek("Kosong: peluang 0,9574 (toleransi 0,001)", abs(h["peluang"] - 0.9574) < 0.001)
cek("Kosong: ujung pohon 45 dari 47", h["ujung"] == {"n": 47, "sakit": 45})
cek("Kosong: ada catatan model", h["catatan_model"] != "")

# Hanya salah satu terisi -> tetap model dasar
h = prediksi({**DASAR, "ca": 2, "thal": None})
cek("Sebagian terisi: memakai model dasar", h["model"] == "dasar")

# Valid tetapi di luar rentang data latih (29 sampai 77)
h = prediksi({**DASAR, "age": 90, "ca": None, "thal": None})
cek("Usia 90: peringatan di luar rentang latih", "age" in h["di_luar_rentang"])

# Validasi
lengkap = {"ca": 2, "thal": 7}
cek("Usia 300 ditolak",
    set(validasi({**DASAR, **lengkap, "age": 300})) == {"age"})
cek("Usia kosong ditolak",
    set(validasi({**DASAR, **lengkap, "age": None})) == {"age"})
cek("Teks 'abc' ditolak",
    set(validasi({**DASAR, **lengkap, "age": "abc"})) == {"age"})
cek("thal=5 ditolak",
    set(validasi({**DASAR, "ca": 1, "thal": 5})) == {"thal"})
cek("ca dan thal kosong diperbolehkan",
    validasi({**DASAR, "ca": None, "thal": None}) == {})

try:
    prediksi({**DASAR, **lengkap, "age": 300})
    cek("prediksi() menolak input tidak valid", False)
except ValueError:
    cek("prediksi() menolak input tidak valid", True)

print(f"\n{sum(hasil)} dari {len(hasil)} skenario lulus")