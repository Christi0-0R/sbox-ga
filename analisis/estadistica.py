'''
Módulo 6: análisis experimental
Plan de análisis (fijado antes de ver los resultados finales):
  - Principal (H1): adaptativa vs estática en NL (mayor), delta (menor) y fitness (mayor)
    del mejor individuo final de cada corrida. Mann-Whitney unilateral, con corrección
    de Holm sobre las tres pruebas
  - Sensibilidad: Wilcoxon pareado por semilla (ambas variantes parten de la misma población)
  - Efecto: diferencia de medias con IC 95 % (bootstrap pareado) y delta de Cliff
  - Secundarias (exploratorias, métricas menos discretas): área bajo la curva de fitness,
    NL y delta promedio de la población final. Ojo: los promedios de la población final
    dependen del modo en que termina cada corrida (explorando = población más diversa y
    peor en promedio), así que miden diversidad más que calidad; solo descriptivos
  - Mecanismo: ¿mejora más la adaptativa justo después de entrar a modo explorar?
  - Referencias: búsqueda aleatoria (piso de sanidad) y AES (cota)

Convención de archivos: <directorio>/<variante>_<semilla>.csv con variante en
{estatica, adaptativa, aleatoria}

Uso:
  PYTHONPATH=. python analisis/estadistica.py resultados/final
'''

import glob
import os
import sys

import numpy as np
import pandas as pd
from scipy.stats import mannwhitneyu, wilcoxon

from src.evaluador import sesgo_lineal, prob_diferencial

AES = dict(nl=112, delta=4)
PRINCIPALES = {"nl_mejor": "mayor", "delta_mejor": "menor", "fit_mejor": "mayor"}
SECUNDARIAS = {"auc_fit": "mayor", "nl_prom_final": "mayor", "delta_prom_final": "menor"}
N_BOOT = 10000


# ---------- carga

def cargar_corridas(directorio, variante):
    # {semilla: DataFrame} de todas las corridas de una variante, indexadas por generación
    corridas = {}
    for ruta in sorted(glob.glob(f"{directorio}/{variante}_*.csv")):
        d = pd.read_csv(ruta).sort_values("generacion").set_index("generacion", drop=False)
        corridas[int(d.semilla.iloc[0])] = d
    return corridas


def resumen_corridas(corridas):
    # Una fila por corrida (semilla): resultado final y medidas secundarias
    filas = {}
    for s, d in corridas.items():
        u = d.iloc[-1]
        filas[s] = dict(
            fit_mejor=u.fit_mejor, nl_mejor=u.nl_mejor, delta_mejor=u.delta_mejor,
            sesgo_lineal=sesgo_lineal(u.nl_mejor), prob_dif=prob_diferencial(u.delta_mejor),
            auc_fit=d.fit_mejor.mean(),
            nl_prom_final=u.nl_prom, delta_prom_final=u.delta_prom,
            frac_explora=(d.k != d.k.iloc[0]).mean() if "k" in d else np.nan)
    return pd.DataFrame.from_dict(filas, orient="index").sort_index()


# ---------- estadística

def holm(pvals):
    # Valores p ajustados por Holm (descenso escalonado)
    p = np.asarray(pvals, dtype=float)
    m = len(p)
    aj = np.empty(m)
    previo = 0.0
    for rango, i in enumerate(np.argsort(p)):
        previo = max(previo, (m - rango) * p[i])
        aj[i] = min(1.0, previo)
    return aj


def cliff(a, b):
    # Delta de Cliff = P(a > b) - P(a < b); en [-1, 1]
    u = mannwhitneyu(a, b).statistic
    return 2 * u / (len(a) * len(b)) - 1


def comparar(a, b, sentido, semilla_boot=0):
    '''
    Compara dos variantes sobre las mismas semillas (a y b alineados por semilla)
    sentido: "mayor" si H1 dice que a debe ser mayor que b; "menor" si debe ser menor
    efecto (Cliff) queda orientado: positivo = a es MEJOR que b
    '''

    if list(a.index) != list(b.index):
        raise ValueError("las variantes no tienen las mismas semillas")
    alt = "greater" if sentido == "mayor" else "less"
    x, y = a.to_numpy(float), b.to_numpy(float)
    dif = x - y

    p_mw = mannwhitneyu(x, y, alternative=alt).pvalue
    p_wil = 1.0 if np.all(dif == 0) else wilcoxon(x, y, alternative=alt).pvalue

    rng = np.random.default_rng(semilla_boot)
    idx = rng.integers(0, len(dif), (N_BOOT, len(dif)))
    medias = dif[idx].mean(axis=1)
    efecto = cliff(x, y) * (1 if sentido == "mayor" else -1) + 0.0   # + 0.0 evita -0.0
    return dict(media_a=x.mean(), media_b=y.mean(), dif=dif.mean(),
                ic_inf=np.percentile(medias, 2.5), ic_sup=np.percentile(medias, 97.5),
                p_mw=p_mw, p_wilcoxon=p_wil, cliff=efecto)


def tabla_comparacion(res_a, res_b, metricas):
    filas = {m: comparar(res_a[m], res_b[m], s) for m, s in metricas.items()}
    t = pd.DataFrame.from_dict(filas, orient="index")
    t.insert(0, "sentido", [metricas[m] for m in t.index])
    t["p_holm"] = holm(t.p_mw.to_numpy())
    return t


# ---------- mecanismo

def mecanismo(corr_adaptativa, corr_estatica, ventana=10):
    '''
    Mejora del mejor fitness en las `ventana` generaciones siguientes a cada entrada a modo
    explorar, contra la mejora de la estática en las mismas generaciones y semilla
    Descriptivo: los eventos de una misma corrida no son independientes
    '''

    filas = []
    for s, da in corr_adaptativa.items():
        de = corr_estatica[s]
        base = da.k.iloc[0]
        entradas = da.index[(da.k.shift(1) == base) & (da.k != base)]
        for g in entradas:
            if g + ventana > da.index[-1]:
                continue
            filas.append(dict(semilla=s, generacion=g,
                              ganancia_adaptativa=da.fit_mejor[g + ventana] - da.fit_mejor[g],
                              ganancia_estatica=de.fit_mejor[g + ventana] - de.fit_mejor[g]))
    ev = pd.DataFrame(filas)
    if ev.empty:
        return dict(eventos=0)
    return dict(eventos=len(ev),
                ganancia_adaptativa=float(ev.ganancia_adaptativa.mean()),
                ganancia_estatica=float(ev.ganancia_estatica.mean()),
                frac_adaptativa_mayor=float((ev.ganancia_adaptativa > ev.ganancia_estatica).mean()),
                frac_estatica_mayor=float((ev.ganancia_adaptativa < ev.ganancia_estatica).mean()))


# ---------- análisis completo

def descriptiva(resumenes):
    cols = ["nl_mejor", "delta_mejor", "fit_mejor", "sesgo_lineal", "prob_dif"]
    filas = []
    for nombre, r in resumenes.items():
        for c in cols:
            filas.append(dict(variante=nombre, metrica=c, media=r[c].mean(), sd=r[c].std(),
                              mediana=r[c].median(), mejor=r[c].max() if c in ("nl_mejor", "fit_mejor") else r[c].min()))
    return pd.DataFrame(filas)


def analizar(directorio):
    corr = {v: cargar_corridas(directorio, v) for v in ("estatica", "adaptativa", "aleatoria")}
    if not corr["estatica"] or not corr["adaptativa"]:
        raise FileNotFoundError(f"faltan corridas de estatica o adaptativa en {directorio}")
    res = {v: resumen_corridas(c) for v, c in corr.items() if c}

    out = dict(
        descriptiva=descriptiva(res),
        principal=tabla_comparacion(res["adaptativa"], res["estatica"], PRINCIPALES),
        secundarias=tabla_comparacion(res["adaptativa"], res["estatica"], SECUNDARIAS),
        mecanismo=mecanismo(corr["adaptativa"], corr["estatica"]),
        resumenes=res, corridas=corr)
    if "aleatoria" in res:
        out["vs_aleatoria"] = pd.concat(
            {"adaptativa": tabla_comparacion(res["adaptativa"], res["aleatoria"], {"fit_mejor": "mayor"}),
             "estatica": tabla_comparacion(res["estatica"], res["aleatoria"], {"fit_mejor": "mayor"})})
    return out


def graficas(corridas, salida):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    os.makedirs(salida, exist_ok=True)
    estilos = {"estatica": "#1f77b4", "adaptativa": "#d62728", "aleatoria": "#7f7f7f"}
    for metrica, titulo in (("fit_mejor", "Fitness del mejor"), ("nl_mejor", "NL del mejor"),
                            ("delta_mejor", "δ del mejor")):
        fig, ax = plt.subplots(figsize=(7, 4))
        for v, c in corridas.items():
            if not c:
                continue
            m = np.vstack([d[metrica].to_numpy() for d in c.values()])
            g = np.arange(m.shape[1])
            ax.plot(g, m.mean(axis=0), label=f"{v} (n={len(c)})", color=estilos[v])
            ax.fill_between(g, np.percentile(m, 25, axis=0), np.percentile(m, 75, axis=0),
                            color=estilos[v], alpha=0.15)
        ax.set_xlabel("generación")
        ax.set_ylabel(titulo)
        ax.set_title(f"{titulo}: media y rango intercuartil entre semillas")
        ax.legend()
        fig.tight_layout()
        fig.savefig(f"{salida}/convergencia_{metrica}.png", dpi=130)
        plt.close(fig)


def principal(directorio):
    pd.set_option("display.width", 140)
    out = analizar(directorio)
    destino = f"{directorio}/analisis"
    os.makedirs(destino, exist_ok=True)
    for nombre in ("descriptiva", "principal", "secundarias"):
        out[nombre].to_csv(f"{destino}/{nombre}.csv", lineterminator="\n")
        print(f"\n== {nombre}\n", out[nombre].round(4).to_string())
    if "vs_aleatoria" in out:
        out["vs_aleatoria"].to_csv(f"{destino}/vs_aleatoria.csv", lineterminator="\n")
        print("\n== vs_aleatoria (fitness)\n", out["vs_aleatoria"].round(4).to_string())
    print("\n== mecanismo (mejora de fitness en las 10 generaciones tras entrar a explorar)")
    for clave, valor in out["mecanismo"].items():
        print(f"   {clave}: {valor:.3f}" if isinstance(valor, float) else f"   {clave}: {valor}")
    graficas(out["corridas"], destino)
    print(f"\nAES como cota: NL={AES['nl']}, delta={AES['delta']}")
    print(f"Tablas y gráficas en {destino}")
    return out


if __name__ == "__main__":
    principal(sys.argv[1] if len(sys.argv) > 1 else "resultados/final")