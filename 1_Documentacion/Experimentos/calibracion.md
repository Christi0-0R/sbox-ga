# Calibración (Fases 3 y 4)

**Para qué existe:** fijar N, G y los parámetros de cada variante **antes** de las corridas finales, con el mismo esfuerzo para ambas, usando solo las semillas preliminares (1 a 20). Todos los criterios se escribieron en el docstring de cada script antes de ver resultados. Los tres scripts son reanudables (omiten los CSV que ya existen) y usan varios procesos.

## 1. `experimentos/calibracion_NG.py`: ¿qué N y G?

- Barre (N, G) ∈ {(100, 100), (100, 200), (200, 200)} con 20 semillas, corriendo la estática y la búsqueda aleatoria.
- Criterios: (a) la estática supera a la aleatoria (Mann-Whitney unilateral, p < 0.05) y (b) la búsqueda se estanca (≥ 50 % de las corridas no mejoran en el último 20 % de las generaciones; si no se estancara, la adaptativa no tendría nada que corregir).
- Se elige la más barata que cumpla ambos: **N = 100, G = 100**.
- Salida: `resultados/calib_NG/`.

## 2. `experimentos/calibracion_estatica.py`: parámetros de la estática

- Rejilla `mutpb ∈ {0.1, 0.2, 0.4}` × `indpb ∈ {0.01, 0.02, 0.05}` × `k ∈ {2, 3, 5}` = 27 configuraciones × 20 semillas.
- Criterio: mayor fitness final medio. Si varias quedan a menos de `TOLERANCIA = 0.3` del mejor, gana la más cercana a la configuración base (menor distancia en posiciones de la rejilla).
- Elegida: **mutpb = 0.4, indpb = 0.02, k = 5**.
- Salida: `resultados/calib_estatica/`.

## 3. `experimentos/calibracion_adaptativa.py`: umbrales de la adaptativa

- Rejilla `ventana ∈ {5, 10, 20}` × `div_min ∈ {0.05, 0.15, 0.30}` × `factor ∈ {1.25, 1.5, 2.0}` = 27 configuraciones × 20 semillas (el mismo presupuesto que la estática).
- **Compuerta:** solo es elegible una configuración que pase en modo explorar entre el 5 % y el 70 % de las generaciones (menos: el control casi no actúa; más: se vuelve búsqueda casi aleatoria). Las 27 pasaron.
- Criterio: mayor fitness final medio; en empate (< 0.3), la más "simple": factor menor, luego ventana mayor, luego div_min menor.
- Elegida: **ventana = 20, div_min = 0.05, factor = 2.0**.
- También corre la estática calibrada en las mismas semillas, solo como referencia (no interviene en la elección).
- Salida: `resultados/calib_adaptativa/`.

## Avisos que hay que repetir en el informe

- Elegir el máximo de 27 medias sobreestima un poco el valor real; por eso los valores p sobre semillas de calibración no son evidencia de H1.
- El óptimo de ambas rejillas quedó en el borde (estática: mutpb y k máximos; adaptativa: ventana y factor máximos, div_min mínimo). No se amplió ninguna para no dar más esfuerzo a una variante que a la otra. Es una limitación declarada.

## Scripts históricos (Fase 2)

`experimentos/calibracion.py` y `experimentos/prelim_estatica.py` corresponden a la primera versión del motor (N = 30, G = 50, regla adaptativa sin histéresis, 14 configuraciones). Sus resultados están en `resultados/archivo_v1/` y ya no se usan.
