"""
latih_model.py (branch v2)
Alur sama dengan notebook laporan: dataset berkode berkas laporan (302 baris
setelah pembersihan), label dibalik, tuning F1. Menyimpan:
  models/model_jantung.pkl
  models/metrics.json
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
                                     cross_validate, train_test_split)
from sklearn.tree import export_text

SEED = 42
DATA = Path("data/dataset.csv")
OUT = Path("models")
KOLOM_13 = ["age", "sex", "cp", "trestbps", "chol", "fbs", "restecg",
            "thalach", "exang", "oldpeak", "slope", "ca", "thal"]
KOLOM_KATEGORI = ["sex", "cp", "fbs", "restecg", "exang", "slope", "thal"]
KOLOM_ANGKA = ["age", "trestbps", "chol", "thalach", "oldpeak", "ca"]
KOLOM_RENTANG = ["age", "trestbps", "chol", "thalach", "oldpeak"]


def kelompok_usia(a):
    return "<50" if a < 50 else ("50-60" if a <= 60 else ">60")


def metrik(y, pred):
    """Positif (sakit) bila label prediksi model = 1 (seperti di notebook)."""
    y = np.asarray(y).astype(int)
    pred = np.asarray(pred).astype(int)
    tn, fp, fn, tp = confusion_matrix(y, pred, labels=[0, 1]).ravel()
    return {
        "tp": int(tp), "fp": int(fp), "fn": int(fn), "tn": int(tn),
        "sensitivitas": float(tp / (tp + fn)) if tp + fn else None,
        "spesifisitas": float(tn / (tn + fp)) if tn + fp else None,
        "akurasi": float((tp + tn) / len(y)),
    }


def siapkan_data():
    """Pembersihan seperti Lampiran 2 dan 3 pada laporan."""
    df = pd.read_csv(DATA)
    print("Data awal:", df.shape)
    n_dup = int(df.duplicated().sum())
    df = df.drop_duplicates().reset_index(drop=True)
    n_ca = int((df["ca"] == 4).sum())
    n_thal = int((df["thal"] == 0).sum())
    df["ca"] = df["ca"].replace(4, np.nan)       # ca valid 0-3
    df["thal"] = df["thal"].replace(0, np.nan)   # thal valid 1-3
    # Di berkas ini target = 1 berarti TIDAK sakit. Dibalik: 1 = ada penyakit.
    df["target"] = 1 - df["target"]
    print("Duplikat dihapus:", n_dup, "| ca=4 -> kosong:", n_ca,
          "| thal=0 -> kosong:", n_thal, "| ukuran akhir:", df.shape)
    print("Distribusi kelas (1 = ada penyakit):",
          df["target"].value_counts().sort_index().to_dict())
    info = {"baris_awal": n_dup + len(df), "duplikat_dihapus": n_dup,
            "ca_diubah_kosong": n_ca, "thal_diubah_kosong": n_thal,
            "baris_akhir": int(len(df))}
    return df, info


def latih(df):
    data_latih, data_uji = train_test_split(
        df, test_size=0.2, random_state=SEED, stratify=df["target"])
    data_latih = data_latih.reset_index(drop=True)
    data_uji = data_uji.reset_index(drop=True)
    print("Data latih:", data_latih.shape, "| Data uji:", data_uji.shape)

    setup(data=data_latih, test_data=data_uji, target="target",
          categorical_features=KOLOM_KATEGORI, numeric_features=KOLOM_ANGKA,
          imputation_type="simple", numeric_imputation="median",
          categorical_imputation="mode", fold=10, session_id=SEED,
          index=False, html=False, verbose=False)

    dt = create_model("dt", verbose=False)
    model = tune_model(dt, optimize="F1", n_iter=30, verbose=False)
    pr = model.get_params()
    print("Pengaturan model akhir:", {k: pr[k] for k in (
        "criterion", "max_depth", "min_samples_leaf", "min_samples_split")})

    Xtr = get_config("X_train_transformed")
    ytr = np.asarray(get_config("y_train_transformed"))
    Xte = get_config("X_test_transformed")
    yte = np.asarray(get_config("y_test_transformed"))
    kolom = list(Xtr.columns)
    mentah_tr = get_config("X_train")     # kolom asli (untuk jenis kelamin, usia)
    mentah_te = get_config("X_test")
    p_te = model.predict_proba(Xte)[:, 1]
    pred_te = model.predict(Xte)

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
    p_oof = cross_val_predict(clone(model), Xtr, ytr, cv=skf,
                              method="predict_proba")[:, 1]

    # Faktor berpengaruh: jumlahkan kolom one-hot kembali ke atribut asalnya
    def asal(c):
        for k in KOLOM_13:
            if c == k or c.startswith(k + "_"):
                return k
        return c

    importance = {}
    for c, v in zip(kolom, model.feature_importances_):
        importance[asal(c)] = importance.get(asal(c), 0.0) + float(v)
    importance = dict(sorted(importance.items(), key=lambda x: -x[1]))
    tak_dikenal = [k for k in importance if k not in KOLOM_13]
    assert not tak_dikenal, (f"Kolom transformasi tidak dikenal: {tak_dikenal}. "
                             f"Kirim daftar kolom ini ke pembimbing: {kolom}")

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

    s_te, a_te = mentah_te["sex"].to_numpy(), mentah_te["age"].to_numpy()
    s_tr, a_tr = mentah_tr["sex"].to_numpy(), mentah_tr["age"].to_numpy()
    hasil = {
        "berkas": "models/model_jantung.pkl",
        "fitur": kolom,
        "data": {"baris": int(len(df)), "n_latih": int(len(Xtr)),
                 "n_uji": int(len(Xte)),
                 "sakit_latih": int(ytr.sum()), "sakit_uji": int(yte.sum())},
        "model": {"jenis": "DecisionTreeClassifier",
                  "criterion": pr["criterion"],
                  "max_depth": pr["max_depth"],
                  "min_samples_leaf": pr["min_samples_leaf"],
                  "kedalaman_nyata": int(model.get_depth()),
                  "jumlah_daun": int(model.get_n_leaves())},
        "akurasi_latih": float(model.score(Xtr, ytr)),
        "uji_ambang_0_5": metrik(yte, pred_te),
        "validasi_silang": cv_ringkas,
        "importance": importance,
        "daun": daun,
        "aturan_teks": aturan,
        "train_ranges": {c: [float(mentah_tr[c].min()), float(mentah_tr[c].max())]
                         for c in KOLOM_RENTANG},
        "uji": [{"y": int(y), "p": float(p), "sex": int(s),
                 "kelompok_usia": kelompok_usia(a)}
                for y, p, s, a in zip(yte, p_te, s_te, a_te)],
        "oof_latih": [{"y": int(y), "p": float(p), "sex": int(s),
                       "kelompok_usia": kelompok_usia(a)}
                      for y, p, s, a in zip(ytr, p_oof, s_tr, a_tr)],
    }
    save_model(model, str(OUT / "model_jantung"))   # bukan finalize_model
    return hasil


def ringkas(h):
    u, cv = h["uji_ambang_0_5"], h["validasi_silang"]
    print("\n=== MODEL (13 atribut) ===")
    print("Kedalaman:", h["model"]["kedalaman_nyata"],
          "| daun:", h["model"]["jumlah_daun"])
    print("Akurasi latih:", round(h["akurasi_latih"], 3),
          "| CV akurasi:", round(cv["akurasi"]["rata2"], 3),
          "±", round(cv["akurasi"]["simpangan_baku"], 3))
    print("CV sens:", round(cv["sensitivitas"]["rata2"], 3),
          "spes:", round(cv["spesifisitas"]["rata2"], 3),
          "AUC:", round(cv["auc"]["rata2"], 3))
    print("Uji -> sens:", round(u["sensitivitas"], 3),
          "spes:", round(u["spesifisitas"], 3),
          "akurasi:", round(u["akurasi"], 4))
    print("Confusion (tn fp fn tp):", u["tn"], u["fp"], u["fn"], u["tp"])
    print("Importance:", {k: round(v, 3)
                          for k, v in list(h["importance"].items())[:7]})


def _jsonkan(o):
    """Ubah angka numpy menjadi angka Python agar bisa ditulis ke JSON."""
    if isinstance(o, np.integer):
        return int(o)
    if isinstance(o, np.floating):
        return float(o)
    if isinstance(o, np.bool_):
        return bool(o)
    raise TypeError(f"Tipe {type(o).__name__} tidak bisa ditulis ke JSON")

def main():
    OUT.mkdir(exist_ok=True)
    df, info = siapkan_data()
    assert [c for c in df.columns if c != "target"] == KOLOM_13
    lengkap = latih(df)
    semua = {
        "dibuat": datetime.now().isoformat(timespec="seconds"),
        "versi": {"python": sys.version.split()[0],
                  "pycaret": pycaret.__version__,
                  "sklearn": sklearn.__version__},
        "seed": SEED,
        "pembersihan": info,
        "lengkap": lengkap,
    }
    with open(OUT / "metrics.json", "w", encoding="utf-8") as f:
        json.dump(semua, f, ensure_ascii=False, indent=2, default=_jsonkan)
    ringkas(lengkap)
    print("\nTersimpan: models/model_jantung.pkl, models/metrics.json")


if __name__ == "__main__":
    main()