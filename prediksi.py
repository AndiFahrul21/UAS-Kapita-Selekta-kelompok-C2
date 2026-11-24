"""
prediksi.py
Logika prediksi yang dipanggil web (aturan lengkap ada di KONTRAK.md).
Tidak memakai Streamlit, jadi bisa diuji dari terminal.
"""
import json
import math
from functools import lru_cache
from pathlib import Path

import pandas as pd
from pycaret.classification import load_model, predict_model

MODELS = Path("models")
BATAS_RENDAH = 0.40   # di bawah ini: risiko rendah
BATAS_TINGGI = 0.65   # mulai dari ini: risiko tinggi

KOLOM_13 = ["age", "sex", "cp", "trestbps", "chol", "fbs", "restecg",
            "thalach", "exang", "oldpeak", "slope", "ca", "thal"]
LANJUTAN = ["ca", "thal"]
KOLOM_11 = [k for k in KOLOM_13 if k not in LANJUTAN]

# Aturan validasi (KONTRAK.md bagian 3)
RENTANG = {"age": (20, 100), "trestbps": (80, 220), "chol": (100, 600),
           "thalach": (60, 220), "oldpeak": (0, 7)}
PILIHAN = {"sex": {0, 1}, "cp": {1, 2, 3, 4}, "fbs": {0, 1},
           "restecg": {0, 1, 2}, "exang": {0, 1}, "slope": {1, 2, 3},
           "ca": {0, 1, 2, 3}, "thal": {3, 6, 7}}
# Kode formulir (kode UCI) -> kode dataset model (berkas laporan)
PETA_KODE = {"cp": {1: 3, 2: 1, 3: 2, 4: 0},
             "restecg": {0: 1, 1: 2, 2: 0},
             "slope": {1: 2, 2: 1, 3: 0},
             "thal": {3: 2, 6: 1, 7: 3}}
KOLOM_BULAT = ["sex", "cp", "fbs", "restecg", "exang", "slope"]


def ke_kode_model(data):
    """Terjemahkan isian formulir ke kode yang dipelajari model."""
    d = {}
    for k in KOLOM_13:
        v = float(data[k])
        if k in PETA_KODE:
            v = float(PETA_KODE[k][int(v)])
        d[k] = int(v) if k in KOLOM_BULAT else v
    return d


def _angka(v):
    """None bila kosong. ValueError bila bukan angka."""
    if v is None or (isinstance(v, str) and not v.strip()):
        return None
    x = float(v)
    return None if math.isnan(x) else x


def validasi(data):
    """Kembalikan {kolom: pesan}. Kosong berarti semua valid.
    ca dan thal boleh kosong ("belum diperiksa"), kolom lain wajib."""
    galat = {}
    for k in KOLOM_13:
        try:
            v = _angka(data.get(k))
        except (TypeError, ValueError):
            galat[k] = "Harus berupa angka."
            continue
        if v is None:
            galat[k] = "Wajib diisi."
        elif k in RENTANG:
            lo, hi = RENTANG[k]
            if not lo <= v <= hi:
                galat[k] = f"Isi antara {lo} dan {hi}."
        elif v not in PILIHAN[k]:
            galat[k] = "Pilihan tidak valid."
    return galat


def kategori(p):
    """Kembalikan (kode, label) sesuai KONTRAK.md bagian 6."""
    if p < BATAS_RENDAH:
        return "rendah", "Risiko rendah"
    if p < BATAS_TINGGI:
        return "sedang", "Risiko sedang"
    return "tinggi", "Risiko tinggi"


def di_luar_rentang(data, train_ranges):
    """Kolom bernilai valid tetapi di luar rentang data latih."""
    hasil = []
    for k, (lo, hi) in train_ranges.items():
        v = _angka(data.get(k))
        if v is not None and not lo <= v <= hi:
            hasil.append(k)
    return hasil


@lru_cache(maxsize=None)
def _muat(nama):
    berkas = MODELS / f"{nama}.pkl"
    if not berkas.exists():
        raise FileNotFoundError(
            f"Berkas model tidak ditemukan: {berkas}. Jalankan latih_model.py.")
    return load_model(str(MODELS / nama), verbose=False)


def muat_metrik():
    berkas = MODELS / "metrics.json"
    if not berkas.exists():
        raise FileNotFoundError(
            f"Berkas metrik tidak ditemukan: {berkas}. Jalankan latih_model.py.")
    with open(berkas, encoding="utf-8") as f:
        return json.load(f)


def _ujung(p, daun):
    """Jumlah pasien latih di ujung pohon yang peluangnya sama dengan p."""
    cocok = [d for d in daun if abs(d["peluang"] - p) < 0.001]
    if not cocok:
        return None
    return {"n": sum(d["n_latih"] for d in cocok),
            "sakit": sum(d["sakit_latih"] for d in cocok)}


def prediksi(data, metrik=None):
    """data: dict 13 atribut (kode formulir). Mengembalikan dict hasil.
    Memunculkan ValueError bila input tidak valid."""
    galat = validasi(data)
    if galat:
        raise ValueError(f"Input tidak valid: {galat}")
    metrik = metrik or muat_metrik()

    df = pd.DataFrame([ke_kode_model(data)], columns=KOLOM_13)
    hasil = predict_model(_muat("model_jantung"), data=df, raw_score=True,
                          round=6, verbose=False)
    p = float(hasil["prediction_score_1"].iloc[0])   # peluang ada penyakit

    kode, label = kategori(p)
    return {
        "peluang": p,
        "kategori": kode,
        "label": label,
        "model": "lengkap",
        "catatan_model": "",
        "di_luar_rentang": di_luar_rentang(
            data, metrik["lengkap"]["train_ranges"]),
        "ujung": _ujung(p, metrik["lengkap"]["daun"]),
    }