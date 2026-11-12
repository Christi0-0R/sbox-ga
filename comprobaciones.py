import pandas as pd

for v in ("estatica", "adaptativa", "aleatoria"):
    f100, f300, igual = [], [], True
    for s in range(1000, 1040):
        a = pd.read_csv(f"resultados/final/{v}_{s}.csv")
        b = pd.read_csv(f"resultados/suplementario_G300/{v}_{s}.csv")
        igual &= a.equals(b.iloc[:len(a)].reset_index(drop=True))
        f100.append(a.fit_mejor.iloc[-1]); f300.append(b.fit_mejor.iloc[-1])
    print(v, "G100:", round(sum(f100)/40, 2), "G300:", round(sum(f300)/40, 2), "prefijo igual:", igual)