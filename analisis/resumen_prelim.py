import glob
import pandas as pd

for a in sorted(glob.glob("resultados/prelim/estatica_*.csv")):
    d = pd.read_csv(a)
    print(a.split("/")[-1])
    for g in (0, 10, 25, 50):
        r = d[d.generacion == g].iloc[0]
        print(f"  gen {g:2d}: fit={r.fit_mejor:6.1f}  NL={int(r.nl_mejor):3d}  "
              f"delta={int(r.delta_mejor):3d}  div={r.diversidad:.3f}  sin_mejora={int(r.sin_mejora)}")