'''
Fase 5b: aplicacion de las S-boxes obtenidas al cifrado de archivos (esquema demostrativo)

Para cada S-box (mejor de la estatica, mejor de la adaptativa y AES como referencia) y para cada archivo de ejemplo: cifra, descifra y comprueba que el SHA-256 del archivo recuperado coincide con el del original
Si el archivo es el ejecutable de ejemplo, ademas se ejecuta el archivo recuperado
Tambien escribe la tabla "mejores S-boxes contra AES"

Regla de "mejor S-box" (fijada antes de mirar resultados): mayor fitness; en empate, menor
delta; en empate, menor semilla

python -m experimentos.cifrar_archivos # usa resultados/final y ejemplos/
'''


import csv
import glob
import json
import os
import random
import subprocess
import sys
import tempfile

from src.cifrado import cifrar_archivo, descifrar_archivo, sha256
from src.evaluador import metricas, prob_diferencial, sesgo_lineal
from src.gf256 import aes_sbox

EJECUTABLE = "ejecutable_minimo"
TAM_ALEATORIO = 1 << 20      # 1 MiB, semilla fija


def mejor_sbox(dir_final, variante):
    """Lee resultados/<dir>/sboxes/<variante>_*.json y devuelve el registro de la mejor."""
    registros = []
    for ruta in glob.glob(os.path.join(dir_final, "sboxes", f"{variante}_*.json")):
        with open(ruta, encoding="utf-8") as f:
            registros.append(json.load(f))
    if not registros:
        raise SystemExit(f"no hay S-boxes de la variante {variante} en {dir_final}/sboxes")
    return min(registros, key=lambda j: (-j["fitness"], j["delta"], j["semilla"]))


def sboxes_a_probar(dir_final):
    out = []
    for variante in ("estatica", "adaptativa"):
        j = mejor_sbox(dir_final, variante)
        out.append((f"{variante}_{j['semilla']}", j["semilla"], list(j["sbox"])))
    out.append(("aes", "", list(aes_sbox())))
    return out


def archivos_a_probar(dir_ejemplos, dir_tmp):
    """Archivos de ejemplo + un binario aleatorio generado al vuelo (no se guarda en el repo)."""
    rutas = sorted(os.path.join(dir_ejemplos, n) for n in os.listdir(dir_ejemplos)
                   if os.path.isfile(os.path.join(dir_ejemplos, n)))
    if not rutas:
        raise SystemExit(f"no hay archivos en {dir_ejemplos}; corre experimentos.generar_muestras")
    aleatorio = os.path.join(dir_tmp, "aleatorio_1MiB.bin")
    with open(aleatorio, "wb") as f:
        f.write(random.Random(0).randbytes(TAM_ALEATORIO))
    return rutas + [aleatorio]


def _leer(ruta):
    with open(ruta, "rb") as f:
        return f.read()


def ejecuta_ok(ruta):
    """Ejecuta el archivo recuperado. Devuelve 'si', 'no' o 'n/a' (no se pudo intentar)."""
    if not sys.platform.startswith("linux"):
        return "n/a"
    try:
        os.chmod(ruta, 0o755)
        return "si" if subprocess.run([ruta], timeout=10).returncode == 0 else "no"
    except (OSError, subprocess.SubprocessError):
        return "n/a"


def probar(nombre, semilla, sbox, ruta, dir_tmp):
    base = os.path.basename(ruta)
    cif = os.path.join(dir_tmp, f"{nombre}__{base}.cif")
    rec = os.path.join(dir_tmp, f"{nombre}__{base}.rec")
    cifrar_archivo(ruta, cif, sbox)
    descifrar_archivo(cif, rec, sbox)
    orig, c, r = _leer(ruta), _leer(cif), _leer(rec)
    fila = dict(
        sbox=nombre, semilla=semilla, archivo=base, bytes=len(orig),
        sha256_original=sha256(orig), sha256_recuperado=sha256(r),
        coincide="si" if sha256(orig) == sha256(r) else "NO",
        cifrado_distinto=("n/a" if len(orig) == 0 else ("si" if c != orig else "NO")),
        ejecuta_recuperado=(ejecuta_ok(rec) if base == EJECUTABLE else "n/a"))
    return fila


def tabla_comparacion(sboxes):
    filas = []
    for nombre, semilla, sbox in sboxes:
        nl_, d_ = (int(x) for x in metricas(sbox))
        filas.append(dict(sbox=nombre, semilla=semilla, nl=nl_, delta=d_,
                          fitness=nl_ - 2.0 * (d_ - 4),
                          sesgo_lineal=round(sesgo_lineal(nl_), 4),
                          prob_diferencial=round(prob_diferencial(d_), 4)))
    return filas


def _csv(ruta, filas):
    os.makedirs(os.path.dirname(ruta) or ".", exist_ok=True)
    with open(ruta, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(filas[0].keys()), lineterminator="\n")
        w.writeheader()
        w.writerows(filas)


def principal(dir_final="resultados/final", dir_ejemplos="ejemplos", dir_salida="resultados/cifrado"):
    sboxes = sboxes_a_probar(dir_final)
    comparacion = tabla_comparacion(sboxes)
    filas = []
    with tempfile.TemporaryDirectory(prefix="cifrado_") as tmp:
        for ruta in archivos_a_probar(dir_ejemplos, tmp):
            for nombre, semilla, sbox in sboxes:
                filas.append(probar(nombre, semilla, sbox, ruta, tmp))
    _csv(os.path.join(dir_salida, "cifrado_archivos.csv"), filas)
    _csv(os.path.join(dir_salida, "comparacion_sboxes.csv"), comparacion)

    print("== Mejores S-boxes contra AES")
    for f in comparacion:
        print(f"  {f['sbox']:<18} NL={f['nl']:<4} delta={f['delta']:<3} fitness={f['fitness']:<6} "
              f"sesgo_lineal={f['sesgo_lineal']}  prob_dif={f['prob_diferencial']}")
    print("== Cifrado y descifrado de archivos (SHA-256 original = recuperado)")
    for f in filas:
        print(f"  {f['sbox']:<18} {f['archivo']:<20} {f['bytes']:>8} B  coincide={f['coincide']:<3} "
              f"cifrado_distinto={f['cifrado_distinto']:<3} ejecuta={f['ejecuta_recuperado']}")
    fallos = [f for f in filas if f["coincide"] != "si" or f["cifrado_distinto"] == "NO"
              or f["ejecuta_recuperado"] == "no"]
    print(f"\n{len(filas) - len(fallos)}/{len(filas)} combinaciones correctas")
    for f in fallos:
        print("FALLO:", f["sbox"], f["archivo"])
    return len(fallos)


if __name__ == "__main__":
    raise SystemExit(principal(*sys.argv[1:]))