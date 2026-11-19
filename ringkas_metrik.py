import json

m = json.load(open("models/metrics.json", encoding="utf-8"))
for kunci in ("lengkap", "dasar"):
    d = m[kunci]
    u = d["uji_ambang_0_5"]
    tp, fp, fn, tn = u["tp"], u["fp"], u["fn"], u["tn"]
    presisi = tp / (tp + fp)
    recall = tp / (tp + fn)
    f1 = 2 * presisi * recall / (presisi + recall)
    cv = d["validasi_silang"]
    print(f"\n== Model {kunci}: latih {d['data']['n_latih']}, uji {d['data']['n_uji']}")
    print(f"  Uji: akurasi {u['akurasi']:.4f}  presisi {presisi:.4f}  "
          f"recall {recall:.4f}  F1 {f1:.4f}")
    print(f"  Confusion (TN FP FN TP): {tn} {fp} {fn} {tp}")
    print(f"  Validasi silang: akurasi {cv['akurasi']['rata2']:.3f} "
          f"± {cv['akurasi']['simpangan_baku']:.3f}, "
          f"sensitivitas {cv['sensitivitas']['rata2']:.3f}, "
          f"AUC {cv['auc']['rata2']:.3f}")