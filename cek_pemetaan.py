import io
import subprocess

import pandas as pd

K13 = ["age", "sex", "cp", "trestbps", "chol", "fbs", "restecg",
       "thalach", "exang", "oldpeak", "slope", "ca", "thal"]

teks = subprocess.run(["git", "show", "main:data/dataset.csv"],
                      capture_output=True, text=True, check=True).stdout
uci = pd.read_csv(io.StringIO(teks), na_values="?")
kag = pd.read_csv("data/dataset.csv")

u = uci[K13 + ["target"]].copy()
u["cp"] = u["cp"].map({1: 3, 2: 1, 3: 2, 4: 0})
u["restecg"] = u["restecg"].map({0: 1, 1: 2, 2: 0})
u["slope"] = u["slope"].map({1: 2, 2: 1, 3: 0})
u["thal"] = u["thal"].map({3: 2, 6: 1, 7: 3})
u["target"] = 1 - u["target"]          # berkas temanmu: 1 = tidak sakit

k = kag.copy()
k["ca"] = k["ca"].replace(4, float("nan"))
k["thal"] = k["thal"].replace(0, float("nan"))

print("Duplikat UCI:", int(u.duplicated().sum()), "| duplikat berkas v2:", int(k.duplicated().sum()))
u = u.drop_duplicates().astype(float)
k = k.drop_duplicates().astype(float)
hasil = u.merge(k, how="outer", indicator=True)["_merge"].value_counts()
print(hasil.to_string())
print("COCOK SEMUA" if set(hasil.index.astype(str)) <= {"both"} or
      (hasil.get("left_only", 0) == 0 and hasil.get("right_only", 0) == 0) else "ADA YANG TIDAK COCOK")

m = u.merge(k, how="outer", indicator=True)
print(m[m["_merge"] != "both"].to_string())