"""riwayat.py - menyimpan dan membaca riwayat prediksi (history.csv)."""
from datetime import datetime
from io import BytesIO
from pathlib import Path

import pandas as pd

from bidang import LABEL
from prediksi import KOLOM_13

BERKAS = Path("history.csv")
KOLOM = ["waktu", "nama"] + KOLOM_13 + ["peluang", "kategori", "model"]


def baca():
    if not BERKAS.exists():
        return pd.DataFrame(columns=KOLOM)
    try:
        df = pd.read_csv(BERKAS, dtype={"nama": "string"})
        return df.reindex(columns=KOLOM)   # berkas lama tanpa kolom nama aman
    except Exception:   # berkas rusak: jangan hentikan aplikasi
        return pd.DataFrame(columns=KOLOM)


def simpan(data, hasil, nama="Tanpa nama"):
    """Tambahkan satu baris. Memunculkan OSError bila berkas tak bisa ditulis."""
    baris = {"waktu": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
             "nama": nama,
             **{k: data.get(k) for k in KOLOM_13},
             "peluang": round(hasil["peluang"], 4),
             "kategori": hasil["label"], "model": hasil["model"]}
    baru = pd.DataFrame([baris], columns=KOLOM)
    lama = baca()
    gabung = baru if lama.empty else pd.concat([lama, baru], ignore_index=True)
    gabung.to_csv(BERKAS, index=False, encoding="utf-8")


def jumlah():
    return len(baca())


def hapus():
    if BERKAS.exists():
        BERKAS.unlink()


def tabel():
    """Versi tampilan: terbaru di atas, kode diganti label Indonesia."""
    df = baca().iloc[::-1].copy()
    if df.empty:
        return df
    df["nama"] = df["nama"].fillna("-")
    df["sex"] = df["sex"].map({0: "Perempuan", 1: "Laki-laki"})
    for k in ("ca", "thal"):
        df[k] = df[k].astype("Int64").astype("string").fillna("belum diperiksa")
    df["peluang"] = (df["peluang"] * 100).round(1).astype(str).str.replace(
        ".", ",", regex=False) + "%"
    df["model"] = df["model"].map({"lengkap": "Lengkap (13)",
                                   "dasar": "Dasar (11)"})
    nama = {"waktu": "Waktu", "nama": "Nama pasien", **LABEL,
            "peluang": "Peluang", "kategori": "Kategori", "model": "Model"}
    return df.rename(columns=nama)


def ke_excel():
    """Berkas .xlsx dengan lebar kolom otomatis (tidak muncul ######).
    Memunculkan ImportError bila openpyxl belum terpasang."""
    df = tabel()
    buf = BytesIO()
    with pd.ExcelWriter(buf, engine="openpyxl") as tulis:
        df.to_excel(tulis, index=False, sheet_name="Riwayat")
        ws = tulis.sheets["Riwayat"]
        for i, kol in enumerate(df.columns, start=1):
            lebar = max([len(str(kol))] + [len(str(v)) for v in df[kol]]) + 2
            huruf = ws.cell(row=1, column=i).column_letter
            ws.column_dimensions[huruf].width = min(lebar, 40)
    return buf.getvalue()