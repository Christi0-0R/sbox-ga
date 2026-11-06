import glob
import pandas as pd
import matplotlib.pyplot as plt

archivos = sorted(glob.glob("resultados/prelim/estatica_*.csv"))
cols = [("fit_mejor", "Fitness del mejor"), ("nl_mejor", "NL del mejor"),
        ("delta_mejor", "δ del mejor"), ("diversidad", "Diversidad")]

fig, ejes = plt.subplots(2, 2, figsize=(11, 7))
for ax, (col, titulo) in zip(ejes.ravel(), cols):
    for a in archivos:
        d = pd.read_csv(a)
        ax.plot(d["generacion"], d[col], label=f"semilla {d['semilla'][0]}")
    ax.set_title(titulo)
    ax.set_xlabel("generación")
ejes[0, 0].legend()
plt.tight_layout()
plt.savefig("analisis/prelim_estatica.png", dpi=120)
print("Guardada: analisis/prelim_estatica.png")