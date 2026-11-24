import pandas as pd

d = pd.read_csv("data/dataset.csv")
print("Ukuran:", d.shape, "| duplikat:", d.duplicated().sum())
print("Kolom:", list(d.columns))
print("target:", d["target"].value_counts().to_dict())
print("thal:", sorted(d["thal"].unique()), "| cp:", sorted(d["cp"].unique()))