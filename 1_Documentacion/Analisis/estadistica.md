# analisis/estadistica.py (Módulo 6: análisis experimental)

**Para qué existe:** generar, con un solo comando y a partir de los CSV, todas las tablas y gráficas del análisis. El plan de análisis está escrito en el docstring y se fijó antes de ver los resultados finales.

```
python -m analisis.estadistica resultados/final
```

Escribe en `resultados/final/analisis/`: `descriptiva.csv`, `principal.csv`, `secundarias.csv`, `vs_aleatoria.csv` y `convergencia_{fit,nl,delta}_mejor.png`.

## Plan de análisis

| Nivel | Qué se compara | Prueba |
|---|---|---|
| **Principal (H1)** | Adaptativa vs. estática en NL (mayor), δ (menor) y fitness (mayor) del mejor individuo final | Mann-Whitney unilateral con corrección de Holm sobre las tres |
| Sensibilidad | Lo mismo, pareado por semilla (ambas parten de la misma población) | Wilcoxon pareado |
| Efecto | Diferencia de medias | IC 95 % por bootstrap pareado (10,000 remuestreos) y delta de Cliff |
| Secundarias (descriptivas) | Área bajo la curva de fitness; NL y δ medios de la población final | Igual que la principal |
| Mecanismo (descriptivo) | Mejora del fitness en las 10 generaciones tras cada entrada a explorar, contra la estática en esas mismas generaciones | Sin prueba (los eventos de una corrida no son independientes) |
| Referencias | Cada variante vs. búsqueda aleatoria; AES como cota | Mann-Whitney con Holm |

## Funciones

| Función | Qué hace |
|---|---|
| `cargar_corridas(dir, variante)` | Lee `<variante>_<semilla>.csv` en un diccionario por semilla. |
| `resumen_corridas` | Una fila por corrida: métricas finales, AUC, promedios de la población final. |
| `holm(pvals)` | Corrección de Holm-Bonferroni (con monotonía). |
| `cliff(a, b)` | Delta de Cliff: P(a > b) − P(a < b). |
| `comparar(a, b, sentido)` | Diferencia, IC bootstrap pareado, Mann-Whitney, Wilcoxon y Cliff. Exige las mismas semillas en ambos grupos. El Cliff que reporta está orientado: positivo = `a` es **mejor** que `b` en el sentido de H1 (por eso en δ se invierte el signo). |
| `tabla_comparacion` | Aplica `comparar` a varias métricas y corrige con Holm. |
| `mecanismo` | Ganancia media tras cada entrada a explorar. |
| `descriptiva` | Media y desviación estándar por variante, con sesgo lineal y probabilidad diferencial. |
| `graficas` | Media y rango intercuartil entre semillas, por generación. |

## Notas de interpretación

- Los promedios de la población final dependen del modo en que termina cada corrida (si termina explorando, la población es más diversa y peor en promedio), así que miden diversidad más que calidad.
- El fitness toma pocos valores distintos: hay muchos empates, lo que reduce la potencia de las pruebas basadas en rangos.
- Las pruebas son unilaterales en el sentido de H1; una diferencia en contra (como la de NL) se reporta como descriptiva, con su IC.
