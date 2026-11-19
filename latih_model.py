"""
latih_model.py
Melatih DUA pohon keputusan (PyCaret) dan menyimpan:
  models/model_jantung.pkl        -> model lengkap (13 atribut)
  models/model_jantung_dasar.pkl  -> model tanpa ca dan thal (11 atribut),
                                     dipakai web bila ca/thal belum diperiksa
  models/metrics.json             -> metrik kedua model
Jalankan:  python latih_model.py
"""
import json
import sys
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd
import pycaret
import sklearn
from pycaret.classification import (create_model, get_config, save_model,
                                    setup, tune_model)
from sklearn.base import clone
from sklearn.metrics import confusion_matrix, make_scorer, recall_score
from sklearn.model_selection import (StratifiedKFold, cross_val_predict,
                                     cross_validate)
from sklearn.tree import export_text

SEED = 42
DATA = Path("data/dataset.csv")
OUT = Path("models")
KOLOM_ANGKA = ["age", "trestbps", "chol", "thalach", "oldpeak"]
LANJUTAN = ["ca", "thal"]   # hasil pemeriksaan lanjutan


def kelompok_usia(a):
    return "<50" if a < 50 else ("50-60" if a <= 60 else ">60")


def metrik(y, p, ambang=0.5):
    """Positif (sakit) bila peluang >= ambang."""
    y = np.asarray(y).astype(int)
    pred = (np.asarray(p) >= ambang).astype(int)
    tn, fp, fn, tp = confusion_matrix(y, pred, labels=[0, 1]).ravel()
    return {
        "tp": int(tp), "fp": int(fp), "fn": int(fn), "tn": int(tn),
        "sensitivitas": float(tp / (tp + fn)) if tp + fn else None,
        "spesifisitas": float(tn / (tn + fp)) if tn + fp else None,
        "akurasi": float((tp + tn) / len(y)),
    }


def latih(df, nama):
    """Latih satu pohon dari df (fitur + kolom 'target'), simpan sebagai
    models/<nama>.pkl, lalu kembalikan (dict metrik, indeks data uji)."""
    n_fitur = len([c for c in df.columns if c != "target"])
    print(f"\n##### {nama}: {n_fitur} fitur #####")

    # Setup. 80% latih / 20% uji, CV 10 lipatan bertingkat.
    # Nilai hilang (ca, thal) diisi modus, bukan rata-rata.
    setup(data=df, target="target", train_size=0.8, fold=10,
          fold_strategy="stratifiedkfold", session_id=SEED,
          numeric_imputation="mode", html=False, verbose=False)

    # Latih pohon, lalu cari kedalaman dan ukuran daun terbaik lewat CV.
    # choose_better=False: jangan diam-diam kembali ke pohon tanpa batas.
    dt = create_model("dt", verbose=False)
    model = tune_model(
        dt, optimize="AUC", search_algorithm="grid",
        custom_grid={"max_depth": [3, 4, 5],
                     "min_samples_leaf": [5, 10, 15]},
        choose_better=False, verbose=False)
    print("Hasil tuning:", {k: model.get_params()[k]
                            for k in ("max_depth", "min_samples_leaf")})

    # Data latih dan uji yang sudah diproses
    Xtr = get_config("X_train_transformed")
    ytr = np.asarray(get_config("y_train_transformed"))
    Xte = get_config("X_test_transformed")
    yte = np.asarray(get_config("y_test_transformed"))
    kolom = list(Xtr.columns)
    p_te = model.predict_proba(Xte)[:, 1]   # peluang kelas 1 = ada penyakit

    # Validasi silang pada data latih
    skf = StratifiedKFold(n_splits=10, shuffle=True, random_state=SEED)
    skor = {"akurasi": "accuracy", "sensitivitas": "recall",
            "spesifisitas": make_scorer(recall_score, pos_label=0),
            "auc": "roc_auc"}
    cv = cross_validate(clone(model), Xtr, ytr, cv=skf, scoring=skor)
    cv_ringkas = {
        k: {"rata2": float(cv[f"test_{k}"].mean()),
            "simpangan_baku": float(cv[f"test_{k}"].std(ddof=1)),
            "per_lipatan": [float(v) for v in cv[f"test_{k}"]]}
        for k in skor}
    # Prediksi lipatan untuk SEMUA pasien latih (kinerja per kelompok
    # yang lebih stabil daripada hanya 61 pasien uji)
    p_oof = cross_val_predict(clone(model), Xtr, ytr, cv=skf,
                              method="predict_proba")[:, 1]

    # Faktor berpengaruh (per fitur asli, karena semua kolom numerik)
    importance = dict(sorted(
        zip(kolom, [float(v) for v in model.feature_importances_]),
        key=lambda x: -x[1]))

    # Ujung pohon (daun): jumlah pasien dan proporsi sakit
    daun_tr, daun_te = model.apply(Xtr), model.apply(Xte)
    daun = []
    for d in np.unique(daun_tr):
        m_tr, m_te = daun_tr == d, daun_te == d
        daun.append({
            "id": int(d),
            "n_latih": int(m_tr.sum()), "sakit_latih": int(ytr[m_tr].sum()),
            "peluang": float(ytr[m_tr].mean()),
            "n_uji": int(m_te.sum()), "sakit_uji": int(yte[m_te].sum())})
    aturan = export_text(model, feature_names=kolom, show_weights=True)

    hasil = {
        "berkas": f"models/{nama}.pkl",
        "fitur": kolom,
        "data": {"baris": int(len(df)), "n_latih": int(len(Xtr)),
                 "n_uji": int(len(Xte)),
                 "sakit_latih": int(ytr.sum()), "sakit_uji": int(yte.sum())},
        "model": {"jenis": "DecisionTreeClassifier",
                  "max_depth": model.get_params()["max_depth"],
                  "min_samples_leaf": model.get_params()["min_samples_leaf"],
                  "kedalaman_nyata": int(model.get_depth()),
                  "jumlah_daun": int(model.get_n_leaves())},
        "akurasi_latih": float(model.score(Xtr, ytr)),
        "uji_ambang_0_5": metrik(yte, p_te, 0.5),
        "validasi_silang": cv_ringkas,
        "importance": importance,
        "daun": daun,
        "aturan_teks": aturan,
        "train_ranges": {c: [float(Xtr[c].min()), float(Xtr[c].max())]
                         for c in KOLOM_ANGKA},
        # Satu baris per pasien uji: untuk slider ambang dan kinerja
        # per kelompok di web.
        "uji": [{"y": int(y), "p": float(p), "sex": int(s),
                 "kelompok_usia": kelompok_usia(a)}
                for y, p, s, a in zip(yte, p_te, Xte["sex"], Xte["age"])],
        "oof_latih": [{"y": int(y), "p": float(p), "sex": int(s),
                       "kelompok_usia": kelompok_usia(a)}
                      for y, p, s, a in zip(ytr, p_oof, Xtr["sex"], Xtr["age"])],
    }

    # Simpan model. TIDAK memakai finalize_model: itu melatih ulang dengan
    # data uji sehingga metrik uji tidak lagi sah.
    save_model(model, str(OUT / nama))
    return hasil, list(get_config("y_test").index)


def ringkas(judul, h):
    u, cv = h["uji_ambang_0_5"], h["validasi_silang"]
    print(f"\n=== {judul} ===")
    print("Kedalaman:", h["model"]["kedalaman_nyata"],
          "| daun:", h["model"]["jumlah_daun"],
          "| fitur:", len(h["fitur"]))
    print("Akurasi latih:", round(h["akurasi_latih"], 3),
          "| CV akurasi:", round(cv["akurasi"]["rata2"], 3),
          "±", round(cv["akurasi"]["simpangan_baku"], 3))
    print("CV sens:", round(cv["sensitivitas"]["rata2"], 3),
          "spes:", round(cv["spesifisitas"]["rata2"], 3),
          "AUC:", round(cv["auc"]["rata2"], 3))
    print("Uji -> sens:", round(u["sensitivitas"], 3),
          "spes:", round(u["spesifisitas"], 3),
          "akurasi:", round(u["akurasi"], 3))
    print("Confusion (tn fp fn tp):", u["tn"], u["fp"], u["fn"], u["tp"])
    print("Importance:", {k: round(v, 3)
                          for k, v in list(h["importance"].items())[:5]})
    print("\n", h["aturan_teks"])


def main():
    OUT.mkdir(exist_ok=True)

    # 'num' dibuang: target berasal dari num, jadi kalau ikut sebagai fitur
    # terjadi kebocoran dan akurasi tampak sempurna.
    df = pd.read_csv(DATA).drop(columns=["num"])
    fitur = [c for c in df.columns if c != "target"]
    assert len(fitur) == 13, f"Fitur harus 13, ditemukan {len(fitur)}"
    print("Data:", df.shape, "| nilai hilang:", int(df.isna().sum().sum()))

    lengkap, idx_a = latih(df, "model_jantung")
    dasar, idx_b = latih(df.drop(columns=LANJUTAN), "model_jantung_dasar")
    print("\nPasien uji sama pada kedua model:", idx_a == idx_b)

    semua = {
        "dibuat": datetime.now().isoformat(timespec="seconds"),
        "versi": {"python": sys.version.split()[0],
                  "pycaret": pycaret.__version__,
                  "sklearn": sklearn.__version__},
        "seed": SEED,
        "fitur_lanjutan": LANJUTAN,
        "lengkap": lengkap,   # 13 atribut
        "dasar": dasar,       # 11 atribut, tanpa ca dan thal
    }
    with open(OUT / "metrics.json", "w", encoding="utf-8") as f:
        json.dump(semua, f, ensure_ascii=False, indent=2)

    ringkas("MODEL LENGKAP (13 atribut)", lengkap)
    ringkas("MODEL DASAR (tanpa ca dan thal)", dasar)
    print("\nTersimpan: models/model_jantung.pkl, "
          "models/model_jantung_dasar.pkl, models/metrics.json")


if __name__ == "__main__":   # wajib di Windows agar proses paralel tidak error
    main()