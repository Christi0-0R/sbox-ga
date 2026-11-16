# experimentos/config.py (parámetros congelados)

**Para qué existe:** un solo lugar con todos los parámetros, compartido por ambas variantes, para que la única diferencia entre ellas sea el lazo de control. Está congelado desde la etiqueta `congelado-v1`; `correr_todo.py` se niega a correr si no coincide con `CFG_CONGELADA`.

## Parámetros comunes

| Clave | Valor | Origen |
|---|---|---|
| `N` | 100 | Calibración de N y G (Fase 3) |
| `G` | 100 | Calibración de N y G (Fase 3) |
| `cxpb` | 0.9 | Fijo; no se adapta |
| `mutpb` | 0.4 | Rejilla de la estática (Fase 3) |
| `indpb` | 0.02 | Rejilla de la estática (Fase 3) |
| `k` | 5 | Rejilla de la estática (Fase 3) |
| `lam` | 2.0 | **Fijo** antes de calibrar (riesgo R7) |

## Solo variante adaptativa

| Clave | Valor | Origen |
|---|---|---|
| `k_explorar` | 3 | Fijo antes de calibrar |
| `mutpb_max` | 0.8 | Fijo antes de calibrar |
| `indpb_max` | 0.1 | Fijo antes de calibrar |
| `div_rec` | 0.6 | Fijo antes de calibrar |
| `ventana` | 20 | Rejilla de la adaptativa (Fase 4) |
| `div_min` | 0.05 | Rejilla de la adaptativa (Fase 4) |
| `factor` | 2.0 | Rejilla de la adaptativa (Fase 4) |

## Semillas

- `SEMILLAS_PRELIM = 1 … 20`: solo para calibrar. Nunca se usan en el análisis final.
- `SEMILLAS_FINALES = 1000 … 1099`: n = 100 por variante, las mismas para estática, adaptativa y aleatoria, así que las tres parten de la misma población inicial.

## Diferencias con el protocolo V4

El protocolo planteaba N = 30, G = 50 y 30 semillas por variante. Se ampliaron tras la calibración (N y G) y para tener más potencia estadística (n = 100 detecta d ≈ 0.36 unilateral con 80 % de potencia, contra d ≈ 0.66 con n = 30).
