import pandas as pd
from pycaret.classification import load_model, predict_model

from prediksi import prediksi

model = load_model("models/model_jantung")

# Pasien contoh pada isian formulir (kode UCI)
formulir = {"age": 58, "sex": 1, "cp": 4, "trestbps": 140, "chol": 260,
            "fbs": 0, "restecg": 2, "thalach": 120, "exang": 1,
            "oldpeak": 2.0, "slope": 2, "ca": 2, "thal": 7}

# Pasien yang sama pada kode dataset model (cp 4->0, restecg 2->0, slope 2->1, thal 7->3)
kode_model = {"age": 58, "sex": 1, "cp": 0, "trestbps": 140, "chol": 260,
              "fbs": 0, "restecg": 0, "thalach": 120, "exang": 1,
              "oldpeak": 2.0, "slope": 1, "ca": 2.0, "thal": 3.0}

h = predict_model(model, data=pd.DataFrame([kode_model]), raw_score=True,
                  round=6)
print("\nMODEL (dipanggil langsung)\n", h.T)

p_langsung = float(h["prediction_score_1"].iloc[0])
p_web = prediksi(formulir)["peluang"]
print(f"\nPeluang langsung: {p_langsung:.4f} | lewat prediksi.py (web): {p_web:.4f}")
print("SAMA" if abs(p_langsung - p_web) < 1e-6 else "BERBEDA")