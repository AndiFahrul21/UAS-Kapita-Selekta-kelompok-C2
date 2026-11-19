import pandas as pd
from pycaret.classification import load_model, predict_model

m_lengkap = load_model("models/model_jantung")
m_dasar = load_model("models/model_jantung_dasar")

# 11 atribut yang dipakai kedua model
dasar = {"age": 58, "sex": 1, "cp": 4, "trestbps": 140, "chol": 260,
         "fbs": 0, "restecg": 2, "thalach": 120, "exang": 1,
         "oldpeak": 2.0, "slope": 2}

# Model lengkap menerima 13 atribut, model dasar hanya 11
h1 = predict_model(m_lengkap, data=pd.DataFrame([{**dasar, "ca": 2, "thal": 7}]),
                   raw_score=True)
h2 = predict_model(m_dasar, data=pd.DataFrame([dasar]), raw_score=True)

print("\nMODEL LENGKAP\n", h1.T)
print("\nMODEL DASAR (tanpa ca dan thal)\n", h2.T)