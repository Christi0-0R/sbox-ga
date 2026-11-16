# Resultados finales del prototipo

Resumen de los resultados del proyecto para el informe final. Cada sección indica en qué carpeta del repositorio se pueden consultar los datos originales. Los resultados se generaron con la configuración congelada (etiqueta `congelado-v1`, commit `6334e2f`) y no se modificaron después de verlos.

## 1. Qué se evaluó

Se compararon dos variantes de un algoritmo genético de permutación para optimizar S-boxes de 8×8 sobre GF(2⁸), con el fitness mono-objetivo `NL − 2·(δ − 4)`:

- **Estática:** parámetros fijos durante toda la ejecución (línea base de control).
- **Adaptativa:** el mismo algoritmo con un lazo que alterna entre explotar y explorar (sube mutpb e indpb y baja el torneo) según el estancamiento de NL y δ y la diversidad de la población.
- **Búsqueda aleatoria** con el mismo presupuesto de evaluaciones, como referencia de sanidad.
- **S-box de AES** (NL = 112, δ = 4) como cota de referencia, no como objetivo a superar.

| Parámetro | Valor |
|---|---|
| Población (N) | 100 |
| Generaciones (G) | 100 |
| Corridas por variante | 100 (semillas 1000 a 1099, las mismas para las tres variantes) |
| Total de corridas | 300 |
| Evaluaciones máximas por corrida | N × (G + 1) = 10,100 |
| Parámetros de la estática | mutpb = 0.4, indpb = 0.02, k = 5, cxpb = 0.9 |
| Umbrales de la adaptativa | ventana = 20, div_min = 0.05, factor = 2.0 |
| Peso de δ en el fitness | λ = 2 (fijo, confirmado con el asesor) |

- **Consultar en:** Configuración: `experimentos/config.py` y `resultados/final/meta.json`

## 2. Resultados descriptivos

Media (desviación estándar) del mejor individuo final de cada corrida, n = 100 por variante.

| Variante | NL | δ | Fitness | Sesgo lineal | Prob. diferencial |
|---|---|---|---|---|---|
| Estática | 98.58 (0.96) | 9.44 (0.90) | 87.70 (1.69) | 0.1149 | 0.0369 |
| Adaptativa | 98.16 (0.73) | 9.34 (0.95) | 87.48 (1.83) | 0.1166 | 0.0365 |
| Aleatoria | 97.82 (0.64) | 9.84 (0.55) | 86.14 (0.51) | 0.1179 | 0.0384 |
| AES (cota) | 112 | 4 | 112 | 0.0625 | 0.0156 |

- **Consultar en:** `resultados/final/analisis/descriptiva.csv`
- **Consultar en:** Un CSV por corrida: `resultados/final/<variante>_<semilla>.csv`
- **Consultar en:** Mejor S-box de cada corrida: `resultados/final/sboxes/`

## 3. Prueba de la hipótesis (H1)

Diferencia adaptativa − estática. Mann-Whitney unilateral en el sentido de H1, con corrección de Holm sobre las tres pruebas; intervalo de confianza del 95 % por bootstrap pareado; delta de Cliff orientado (positivo = la adaptativa es mejor).

| Métrica | Sentido de H1 | Diferencia | IC 95 % | p (Holm) | Cliff |
|---|---|---|---|---|---|
| NL | mayor | −0.42 | [−0.64, −0.20] | 1.000 | −0.20 |
| δ | menor | −0.10 | [−0.30, 0.08] | 0.667 | 0.05 |
| Fitness | mayor | −0.22 | [−0.56, 0.12] | 1.000 | −0.09 |

La prueba de sensibilidad (Wilcoxon pareado por semilla) da las mismas conclusiones (p = 0.9998, 0.159 y 0.850, sin corregir).

**Resultado: H1 no se sostiene.** No hay evidencia de que la variante adaptativa supere a la estática en NL, δ ni fitness, así que se mantiene la hipótesis nula. La cota superior del IC del fitness (+0.12, unas 0.07 desviaciones estándar) descarta una mejora relevante de la adaptativa con este diseño. En NL la adaptativa queda algo por debajo de la estática y el intervalo excluye el cero; como las pruebas son unilaterales, se reporta solo como dato descriptivo.

- **Consultar en:** `resultados/final/analisis/principal.csv`
- **Consultar en:** Salida completa del análisis: `resultados/final/analisis_salida.txt`

## 4. Comparación con la búsqueda aleatoria

| Variante | Diferencia de fitness frente a la aleatoria | IC 95 % | Cliff | p (Holm) |
|---|---|---|---|---|
| Estática | +1.56 | [1.22, 1.90] | 0.52 | < 0.001 |
| Adaptativa | +1.34 | [0.96, 1.72] | 0.38 | < 0.001 |

Las dos variantes del AG superan a la búsqueda aleatoria con el mismo presupuesto de evaluaciones, así que el algoritmo sí aprende algo más que el azar.

- **Consultar en:** `resultados/final/analisis/vs_aleatoria.csv`

## 5. Comparación con la S-box de AES

Ninguna variante se acerca a la cota de AES. El mejor NL obtenido fue 100 (AES: 112) y la mejor δ fue 8 (AES: 4). En términos del atacante, el sesgo del mejor ataque lineal es ≈ 1.8 veces el de AES y la probabilidad del mejor ataque diferencial ≈ 2.4 veces. Esto concuerda con el posicionamiento del protocolo: AES se usa como referencia, no como objetivo.

- **Consultar en:** `resultados/cifrado/comparacion_sboxes.csv`

## 6. Convergencia

Las gráficas muestran la media y el rango intercuartil, entre las 100 semillas, del fitness, la NL y la δ del mejor individuo en cada generación. La estática y la adaptativa son idénticas mientras el lazo no interviene, porque parten de la misma población. Después la adaptativa queda ligeramente por debajo y las dos se separan con claridad de la aleatoria.

- **Consultar en:** `resultados/final/analisis/convergencia_fit_mejor.png`
- **Consultar en:** `resultados/final/analisis/convergencia_nl_mejor.png`
- **Consultar en:** `resultados/final/analisis/convergencia_delta_mejor.png`

## 7. Medidas secundarias y mecanismo (descriptivas)

- **Área bajo la curva de fitness:** diferencia de −0.09 [−0.24, 0.07], sin diferencia apreciable en la velocidad de mejora.
- **Población final:** la NL media de la población es 94.84 en la adaptativa contra 97.46 en la estática (−2.62 [−2.91, −2.33]), y la δ media es 10.54 contra 9.82. La adaptativa conserva una población más diversa y menos convergida, pero eso no produce mejores individuos.
- **Mecanismo:** en 387 entradas al modo explorar, el fitness mejora en promedio 0.057 en las 10 generaciones siguientes en la adaptativa, contra 0.098 en la estática en esas mismas generaciones. Explorar tiene un costo a corto plazo que no se recupera dentro de ese horizonte. No se aplican pruebas porque los eventos de una misma corrida no son independientes.

- **Consultar en:** `resultados/final/analisis/secundarias.csv`

## 8. Experimento suplementario (exploratorio): G = 300

Se declaró antes de ejecutarse para responder si el costo de explorar se amortiza con más generaciones. Usa G = 300, semillas 1000 a 1039 (n = 40) y el resto de la configuración congelada.

| Variante | G = 100 (mismas 40 semillas) | G = 300 |
|---|---|---|
| Estática | 87.70 | 88.70 |
| Adaptativa | 87.50 | 88.75 |
| Aleatoria | 86.15 | 86.20 |

Con G = 300 la diferencia de fitness entre la adaptativa y la estática pasa de −0.22 a +0.05 [−0.70, 0.80]. Va en la dirección de que explorar se amortiza con más tiempo, pero el intervalo incluye tanto una pequeña ventaja como una pequeña desventaja. **No hay evidencia de que la adaptativa supere a la estática a G = 300.** Se presenta como pista para trabajo futuro, no como hallazgo, y no reemplaza la prueba de H1.

- **Consultar en:** `resultados/suplementario_G300/`
- **Consultar en:** Comprobación de coherencia con las corridas finales: `analisis/comprobaciones.py`

## 9. Aplicación: cifrado de archivos binarios

Se tomó la mejor S-box de cada variante y la de AES. Con cada una se cifraron y descifraron cinco archivos: texto, imagen PNG, ejecutable ELF, archivo vacío y 1 MiB de bytes aleatorios.

| S-box | Semilla | NL | δ | Fitness |
|---|---|---|---|---|
| Mejor estática | 1008 | 100 | 8 | 92.0 |
| Mejor adaptativa | 1036 | 100 | 8 | 92.0 |
| AES | – | 112 | 4 | 112.0 |

- **15/15 combinaciones** recuperan el archivo con un SHA-256 idéntico al original.
- El ejecutable recuperado se ejecuta y termina correctamente.

Esto demuestra que las S-boxes del AG son biyectivas, reversibles y utilizables como componente de sustitución. **No** demuestra que protejan datos: la sustitución byte a byte conserva las frecuencias y no es un cifrado seguro por sí sola.

- **Consultar en:** `resultados/cifrado/cifrado_archivos.csv`
- **Consultar en:** Archivos de prueba: `ejemplos/`

## 10. Verificación de los resultados

| Verificación | Resultado | Dónde consultarla |
|---|---|---|
| Regresión del evaluador con AES | NL = 112, δ = 4 | `tests/test_evaluador.py` |
| Contraste con sboxU (AES + 50 aleatorias) | 51/51 coinciden | `evidencia/colab_2026-11-14/contraste_sboxu_51.txt` |
| Contraste de las S-boxes finales con sboxU | 200/200 coinciden | `evidencia/colab_2026-11-14/contraste_final_200.txt` |
| Reproducibilidad laptop vs. Colab | 15/15 archivos idénticos byte a byte | `evidencia/colab_2026-11-14/reproducibilidad.txt` |
| Pruebas automáticas | 126 pasan, 1 se salta (sboxU sin Sage) | `tests/`, `evidencia/colab_2026-11-14/pytest.txt` |

## 11. Ubicación respecto a la literatura

El mejor resultado del proyecto (NL = 100, δ = 8) queda al nivel de la búsqueda aleatoria y de las primeras heurísticas, y por debajo del referente de los métodos especializados (NL = 104, Tesař, 2010). Esos métodos usan entre 5 y 100 veces más evaluaciones y funciones de costo sobre todo el espectro de Walsh, no la NL directamente. Esto no afecta a la prueba de H1, que compara las dos variantes en igualdad de condiciones.

- **Consultar en:** `1_Documentacion/Referencias/literatura_nl_delta.md`

## 12. Conclusiones

1. **H1 no se sostiene.** Con N = 100, G = 100 y 100 corridas por variante, la retroalimentación adaptativa no mejora el compromiso NL–δ frente a una variante estática equivalente y bien calibrada. El resultado es válido y el protocolo lo prevé (riesgo R4).
2. **El AG funciona.** Las dos variantes superan de forma clara a la búsqueda aleatoria con el mismo presupuesto.
3. **La diferencia entre variantes está aislada.** Una prueba demuestra que, con el control neutralizado, la adaptativa produce exactamente el mismo CSV que la estática. Cualquier diferencia observada se debe solo al lazo de control.
4. **El mecanismo adaptativo cumple su función local, pero no paga a este horizonte.** Mantiene una población más diversa, pero explorar cuesta mejora a corto plazo y ese costo no se recupera en 100 generaciones. Con 300 generaciones la tendencia mejora, pero sin evidencia concluyente.
5. **Las S-boxes obtenidas son válidas y utilizables** (biyectivas, reversibles, verificadas con una herramienta pública), aunque lejos de la calidad de AES.
6. **El experimento es reproducible:** configuración congelada, semillas registradas, verificación cruzada con sboxU y resultados idénticos entre máquinas.

## 13. Explicaciones posibles del resultado

Son hipótesis para la discusión, no hechos probados:

- Explorar tiene un costo inmediato que a G = 100 no se amortiza.
- La δ del mejor individuo casi no cambia, así que la señal de estancamiento de δ aporta poca información al lazo.
- El fitness toma pocos valores distintos (casi siempre pares), lo que genera mesetas y muchos empates.
- La estática calibrada ya es una línea base fuerte.
- Calibrar ambas variantes con 20 semillas preliminares pudo sobreestimar a las dos.

## 14. Limitaciones

- Las rejillas de calibración fueron acotadas y el óptimo de ambas variantes quedó en el borde.
- El atacante está simulado mediante NL y δ; no se implementa un ataque criptoanalítico real.
- Con n = 100, el diseño detecta efectos de d ≈ 0.36 (prueba unilateral, 80 % de potencia); diferencias más pequeñas podrían no detectarse.
- La probabilidad de cruce no se adapta; se adaptan mutpb, indpb y el tamaño del torneo.
- El cifrado de archivos es demostrativo y no seguro.
- El presupuesto por corrida (10,100 evaluaciones) es menor que el de los métodos de la literatura que alcanzan NL = 104.

## 15. Trabajo futuro

- Un horizonte más largo (G ≥ 300) con más semillas, declarado de antemano, para confirmar o descartar la tendencia del experimento suplementario.
- Usar una función de costo sobre todo el espectro de Walsh-Hadamard, en lugar de solo la NL, para reducir las mesetas.
- Un lazo adaptativo con señales más informativas que el estancamiento de δ.
- Evaluar métricas adicionales (SAC, grado algebraico, uniformidad boomerang).

## 16. Cómo reproducir estos resultados

Desde la raíz del repositorio, con el entorno instalado (`pip install -r requirements.txt`):

```
python -m pytest -q                                      # pruebas
python -m experimentos.correr_todo                       # 300 corridas finales (reanudable)
python -m experimentos.correr_todo --suplementario       # experimento G = 300
python -m analisis.estadistica resultados/final          # tablas y gráficas
python -m experimentos.contraste_final resultados/final  # contraste (requiere sboxU para el completo)
python -m experimentos.generar_muestras                  # archivos de prueba
python -m experimentos.cifrar_archivos                   # cifrado de archivos
```

## Mapa de carpetas de resultados

| Carpeta | Contenido |
|---|---|
| `resultados/final/` | 300 corridas finales (un CSV por corrida), `meta.json` y `entorno.txt` |
| `resultados/final/sboxes/` | Mejor S-box de cada corrida del AG (200 archivos JSON) |
| `resultados/final/analisis/` | Tablas (descriptiva, principal, secundarias, vs. aleatoria) y gráficas de convergencia |
| `resultados/suplementario_G300/` | Experimento exploratorio con G = 300 |
| `resultados/cifrado/` | Resultados del cifrado de archivos y comparación de S-boxes |
| `resultados/calib_NG/`, `calib_estatica/`, `calib_adaptativa/` | Calibración (semillas preliminares, no son evidencia de H1) |
| `resultados/archivo_v1/` | Histórico del motor anterior (Fase 2), ya no vigente |
| `evidencia/colab_2026-11-14/` | Salidas de la verificación en Colab con sboxU |
| `ejemplos/` | Archivos usados en la prueba de cifrado |