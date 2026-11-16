# experimentos/correr_todo.py y baseline_aleatoria.py (Fase 5a)

## correr_todo.py: las corridas finales

**Qué hace:** corre las tres variantes (estática, adaptativa, aleatoria) con las 100 semillas finales: 300 corridas, en paralelo.

**Garantías:**
- **Reanudable:** un CSV terminado es la marca de "corrida hecha"; si se interrumpe, se vuelve a lanzar el mismo comando.
- **Escritura atómica:** cada CSV se escribe como `.tmp` y se renombra al final (`os.replace`); los `.tmp` huérfanos se borran al reanudar.
- **Configuración congelada:** se niega a correr si `config.py` no coincide con `CFG_CONGELADA` o si el directorio tiene corridas de otra configuración.
- **Trazabilidad:** guarda `meta.json` (configuración, semillas, commit, fechas, versión de Python) y `entorno.txt` (`pip freeze`).
- Guarda la mejor S-box de cada corrida del AG en `sboxes/<variante>_<semilla>.json` (con NL, δ y fitness).
- Fija un hilo de BLAS por proceso: el paralelismo lo da el `Pool`.

**Modos:**

| Comando | Qué corre | Directorio |
|---|---|---|
| `python -m experimentos.correr_todo` | 3 variantes × semillas 1000 a 1099 | `resultados/final` |
| `... --smoke` | Prueba rápida (N = 20, G = 10, 3 semillas); no es resultado | `resultados/smoke` |
| `... --suplementario` | Exploratorio: G = 300, semillas 1000 a 1039 | `resultados/suplementario_G300` |
| `... --workers 4` | Limita el número de procesos | — |

El diseño del suplementario (`SUPLEMENTARIO = dict(G=300, n_semillas=40)`) se declaró antes de correrlo y solo cambia G y el número de semillas.

## baseline_aleatoria.py: la referencia de sanidad

- Evalúa N × (G + 1) permutaciones al azar, agrupadas en G + 1 "generaciones" de N, y registra el mejor acumulado con el mismo esquema de CSV que el AG.
- Con la misma semilla, sus primeras N permutaciones son idénticas a la población inicial del AG, así que comparten punto de partida.
- Recibe un presupuesto igual o mayor que el AG (el AG no reevalúa al élite ni a los descendientes sin cambios).
- Es una referencia (atributo 7 del estándar ACM SIGSOFT), no una tercera hipótesis.

## analisis/comprobaciones.py

Comprueba que las primeras 100 generaciones de las corridas con G = 300 sean idénticas a las corridas finales, y que las 40 semillas den los mismos promedios a G = 100 que las 100 semillas.
