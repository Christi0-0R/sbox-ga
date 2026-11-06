import itertools
import pandas as pd
from experimentos.config import CFG, SEMILLAS_PRELIM
from src.motor_ga import correr


def resumen(nombre, cfg, adaptativo):
    filas = []
    for s in SEMILLAS_PRELIM:
        ruta = f"resultados/calib/{nombre}_{s}.csv"
        correr(s, adaptativo, cfg, ruta)
        d = pd.read_csv(ruta)
        u = d.iloc[-1]
        filas.append((u.fit_mejor, u.nl_mejor, u.delta_mejor,
                      d.diversidad.iloc[10:].mean(), d.mutpb.iloc[10:].mean()))
    df = pd.DataFrame(filas, columns=["fit", "nl", "delta", "div_media", "mutpb_medio"])
    m = df.mean()
    print(f"{nombre:28s} fit={m.fit:5.1f} nl={m.nl:5.1f} delta={m.delta:5.1f} "
          f"div={m.div_media:.3f} mutpb={m.mutpb_medio:.2f}")


# Controles estaticos
resumen("estatica_base", CFG, False)
resumen("estatica_mutpb0.8", dict(CFG, mutpb=0.8), False)

# Adaptativa: rejilla de umbrales
for div_min, ventana in itertools.product([0.05, 0.1, 0.2, 0.5], [3, 5, 8]):
    cfg = dict(CFG, div_min=div_min, ventana=ventana)
    resumen(f"adapt_div{div_min}_v{ventana}", cfg, True)