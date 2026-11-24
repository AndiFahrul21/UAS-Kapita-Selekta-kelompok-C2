import json

m = json.load(open("models/metrics.json", encoding="utf-8"))["lengkap"]
print(m["aturan_teks"])
print()
for d in m["daun"]:
    print("daun", d["id"], "| pasien latih:", d["n_latih"],
          "| sakit:", d["sakit_latih"], "| peluang:", f'{d["peluang"]:.1%}')