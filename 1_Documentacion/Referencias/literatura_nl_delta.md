# Valores de NL y δ reportados en la literatura (S-boxes biyectivas de 8×8)

Pendiente heredado de la Fase 1: tener valores de referencia, además de AES, para ubicar los resultados del AG en la discusión.

> **Antes de citar en el informe:** la columna "Fuente del dato" indica si el valor se tomó del artículo original o de otro artículo que lo cita. Los marcados como *secundaria* deben confirmarse en el artículo original (tabla de resultados) antes de usarlos.

## Tabla de referencia

| Método | Autores | NL | δ | Presupuesto aprox. | Fuente del dato |
|---|---|---|---|---|---|
| Inverso en GF(2⁸) + afín (AES) | Daemen y Rijmen (2002) | 112 | 4 | Construcción algebraica | Primaria (y regresión del proyecto) |
| Búsqueda pseudoaleatoria | Varios (resumen de Ivanov et al.) | 94 – 100 | 8 | — | Secundaria [1] |
| Heurísticas (HC, SA, GA) en general | Varios (resumen de Ivanov et al.) | 98 – 104 | 6 | — | Secundaria [1] |
| Hill climbing / GA + HC | Millan et al. | 100 | n. r. | — | Secundaria [2] |
| Recocido simulado con función de costo WHS | Clark, Jacob y Stepney (2004/2005) | 102 | n. r. | — | Confirmado por Tesař (2010) [11] |
| GA + búsqueda en árbol (GaT), costo de Clark afinado | Tesař (2010) | 104 | n. r. | — | Primaria [11] |
| GA + costo WHS | Kuznetsov et al. (2024) | 104 | n. r. | ≈ 49,400 iteraciones (media) | Primaria [6] |
| GA "en reversa" (δ en el fitness) | Ivanov, Nikolov y Nikova | 110 | 4 | — | Primaria (presentación) [1] |
| GA adaptativo híbrido con búsqueda local (HAGA) | Behera y Gangopadhyay (2023) | 108 | 6 | — | Primaria (resumen) [7] |
| GA con operadores nuevos (uniformidad boomerang) | Kang y Wang (2022) | 108 | 6 | — | Primaria (resumen) [8] |
| **Este proyecto, mejor de 100 corridas** | Estática (1008) y adaptativa (1036) | **100** | **8** | ≤ 10,100 evaluaciones | `resultados/cifrado/comparacion_sboxes.csv` |
| **Este proyecto, media** | Estática / adaptativa | 98.58 / 98.16 | 9.44 / 9.34 | ≤ 10,100 evaluaciones | `resultados/final/analisis/descriptiva.csv` |

n. r.: no reportado en la fuente consultada.

Picek, Čupić y Rotim (2016) se cita por su propuesta de función de costo (ver protocolo, sección 1.1.2), no por valores numéricos: el artículo no está en acceso abierto y no se pudo consultar su tabla de resultados, así que no se reportan cifras de ese trabajo.

## Lectura para la discusión

1. **Dónde quedan los resultados.** El mejor NL del proyecto (100) está al nivel de la búsqueda pseudoaleatoria y de las primeras heurísticas, y por debajo del referente habitual de la literatura para métodos heurísticos (NL = 104). Picek et al. (2017) señalan que incluso los mejores resultados heurísticos de 8×8 están lejos de NL = 112 y δ = 4 [9], lo que es coherente con tomar AES como cota y no como objetivo.
2. **Presupuesto.** Cada corrida del proyecto evalúa como máximo N × (G + 1) = 10,100 S-boxes. Los métodos que alcanzan 104 reportan del orden de 50,000 a 1,000,000 de evaluaciones. La comparación con la literatura no es en igualdad de presupuesto.
3. **Función de costo.** Los trabajos que llegan a 104 no optimizan NL directamente, sino funciones de costo sobre todo el espectro de Walsh-Hadamard (Clark, Picek, Freyre-Echevarría), porque NL solo mira el peor coeficiente y deja una superficie de búsqueda con mesetas grandes. El fitness del proyecto (`NL − 2(δ − 4)`) hereda esas mesetas, lo que concuerda con los muchos empates observados. Esto es una explicación posible del techo en NL = 100, no un hecho probado, y es una línea natural de trabajo futuro.
4. **Umbral práctico.** Un artículo sobre construcción de S-boxes biyectivas considera "fuertes" a las de 8×8 con δ ≤ 10 y NL ≥ 100 [10]. Las mejores S-boxes del proyecto (100, 8) cumplen ese umbral; la media de las corridas (≈ 98.5, ≈ 9.4) no lo cumple en NL.
5. **Lo que no cambia.** Nada de esto afecta la prueba de H1, que compara dos variantes bajo las mismas condiciones; solo ubica el nivel absoluto de ambas.

## Fuentes

1. Ivanov, G., Nikolov, N. y Nikova, S. *Generation of good bijective S-boxes using a Reversed Genetic Algorithm* (presentación). https://org.uib.no/selmer/people/lbu061/nikova.pdf
2. Clark, J. A., Jacob, J. L. y Stepney, S. (2005). The design of S-boxes by simulated annealing. *New Generation Computing*, 23, 219-231. https://doi.org/10.1007/BF03037656 (valores de HC y GA/HC tomados de una tabla de un artículo que lo cita: https://scite.ai/reports/the-design-of-s-boxes-by-05PQnb)
3. Freyre-Echevarría, A. et al. (2020). An external parameter independent novel cost function for evolving bijective substitution-boxes. *Symmetry*, 12(11), 1896. https://doi.org/10.3390/sym12111896
4. Djurasevic, M., Jakobovic, D., Mariot, L., Mesnager, S. y Picek, S. (2022). On the evolution of boomerang uniformity in cryptographic S-boxes (sección de trabajo relacionado). https://arxiv.org/abs/2212.04789
5. Picek, S., Čupić, M. y Rotim, L. (2016). A new cost function for evolution of S-boxes. *Evolutionary Computation*, 24(4), 695-718. https://doi.org/10.1162/EVCO_a_00191
6. Kuznetsov, O., Poluyanenko, N., Frontoni, E., Arnesano, M. y Smirnov, O. (2024). Evolutionary approach to S-box generation: optimizing nonlinear substitutions in symmetric ciphers. https://arxiv.org/abs/2407.03510
7. Behera, P. K. y Gangopadhyay, S. (2023). Evolving bijective S-boxes using hybrid adaptive genetic algorithm with optimal cryptographic properties. *Journal of Ambient Intelligence and Humanized Computing*, 14(3), 1713-1730. https://doi.org/10.1007/s12652-021-03392-6
8. Kang, M. y Wang, M. (2022). New genetic operators for developing S-boxes with low boomerang uniformity. *IEEE Access*, 10, 10898-10906. https://doi.org/10.1109/ACCESS.2022.3144458
9. Picek, S., Mariot, L., Leporati, A. y Jakobovic, D. (2017). Evolving S-boxes based on cellular automata with genetic programming. *GECCO '17 Companion*. https://www.human-competitive.org/sites/default/files/picek-paper-1-gecco.pdf
10. *Practical bijective S-box design* (2013). https://arxiv.org/abs/1301.4723
11. Tesař, P. (2010). A new method for generating high non-linearity S-boxes. *Radioengineering*, 19(1), 23-26. https://www.radioeng.cz/fulltexts/2010/10_01_023_026.pdf

## Relevancia especial de Behera y Gangopadhyay (2023)

Es un **GA adaptativo** para S-boxes de 8×8 con NL y δ, es decir, el trabajo más cercano a la variante adaptativa del proyecto. No está en las fuentes del protocolo V4; conviene leerlo y agregarlo al marco de referencia del informe (sección 2.2), aunque sea para marcar la diferencia: ellos combinan adaptación con búsqueda local, mientras que aquí la adaptación es el único factor que cambia entre variantes.
