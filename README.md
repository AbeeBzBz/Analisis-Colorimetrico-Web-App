# Cuantificación colorimétrica de concentración mediante detección automática de regiones de interés y procesamiento digital de imágenes en microcanales.

** ¿Qué es esto? (╭ರ_•)...? **

Es un conjunto de pasos en Python que detecta automáticamente una Región de Interés (ROI) en imágenes de microcanales y construye una curva de calibración de la intensidad de luz del pixel a concentración del fluido pasando por el sistema microfluídico.
Se usa un filtro adaptado (matched filter) de gran tolerancia al bajo contraste.
Lo que se desarrolló y valida aquí es el método de procesamiento de imágenes en sí ya que está pensado para poder utilizarse con cualquier estructura de canal de ancho conocido, no solo con este chip en particular ٩(⎚-⎚).

** ¿Qué incluye el folder? **

✦. Analisis_colorimetrico_local.ippynb (Notebook Principal. Corre todo el análisis ( ◡̀_◡́)ᕤ ).
✦. analisis_canal.py (Módulo con las funciones de detección y calibración (⎚-⎚✧) ).
✦. imagenes/ (Folder con imagenes .bmp usadas; blanco, maxima, referencias, gradiente).
✦. README.md (El presente archivo que describe la funcionalidad y generalidades del código).

!!	Asegurese de que esten TODOS juntos en la misma carpeta, ya que el notebook busca `analisis_canal.py`
y la carpeta `imagenes/` justo al lado de sí mismo	¡¡


** ¿Qué se necesita para correrlo? (˶ᵔ ᵕ ᵔ˶) **
(yo uso VScode como ambiente, pero Tambien se puede usar solo el ambiente de Jupyter Notebooks)

✦.Python 
	(vía [Anaconda](https://www.anaconda.com/download), que ya incluye Jupyter, numpy, scipy, matplotlib y pandas).

✦. scikit-image (la única librería que probablemente falte) se instala con:
	'''
	  bash
	 pip install scikit-image
	'''

✦.Visual Studio Code 
	Con las extensiones Python y Jupyter instaladas 
	(desde el ícono de Extensiones en la barra lateral, buscar cada una por nombre e instalar)
!!	sin estas dos extensiones, VS Code no puede abrir ni correr notebooks	¡¡

** ¿Cómo abrir y correrlo? Paso a paso ٩(^ᗜ^ )و ´- **

	1. Descomprime la carpeta, manteniendo el notebook, `analisis_canal.py` y `imagenes/` juntos.
	2. Abre VS Code → File > Open Folder... → selecciona esa carpeta.
	3. En el explorador de archivos de la izquierda, haz clic en `Analisis_colorimetrico_local.ipynb`.
	4. En la esquina superior derecha del notebook, haz clic en "Select Kernel" y elige tu ambiente de Python/Anaconda (donde ya instalaste `scikit-image`).
	5. Corre las celdas en orden, de arriba hacia abajo (▷ en cada celda, o `Run All` desde el menú superior del notebook).

Nota:* `analisis_canal.py` no se abre ni se corre por separado — es un módulo que el notebook importa !٩(ˋ ᗣ ˊ )و
!!	Solo debe existir en la misma carpeta ¡¡

** ¿Cómo saber que funcionó bien?◝(ᵔᗜᵔ)◜ **

En orden, el notebook debería mostrarte:

1. Sección 1 (rutas): un mensaje confirmando que se encontraron todas las imágenes en la carpeta `imagenes/` (si falta alguna, te dice cuál).
2. Sección 2 (ancho de referencia): una gráfica con la imagen de referencia y su perfil de intensidad, más el ancho de canal detectado en píxeles impreso arriba.
3. Sección 3 (validación): una gráfica por cada imagen de blanco y máxima (6 en total), y al final una tabla con la posición y "confianza" detectada en cada una.
4. Sección 4 (calibración): la ecuación de calibración (`Concentración = pendiente × Intensidad + intercepto`) junto con su R², la gráfica de la curva ajustada, y una tabla con el detalle de cada imagen usada.
5. Sección 5 (gradiente): un mapa de concentración y un perfil a lo largo del canal para la imagen de flujo/gradiente, junto con la concentración media y el porcentaje del perfil que cae fuera del rango calibrado (un valor alto ahí es normal si esa imagen se tomó en condiciones de luz distintas a blanco/máxima, no es un error...).

** ¿Qué hacer si no funcionó? (ᵕ• ᴗ •)ﾉﾞ(◞ ‸ ◟°｡) **

✦. ModuleNotFoundError: No module named 'analisis_canal'`
	el archivo `analisis_canal.py` no está en la misma carpeta que el notebook. Verifica con:
	```python
	  import os
	  print(os.listdir())
	```
✦. Subrayados rojos o "could not be resolved" en `analisis_canal.py` dentro de VS
  Code
	normalmente no son errores reales, sino que VS Code está usando un intérprete de Python distinto al del kernel. Se corrige con `Ctrl+Shift+P` → "Python: Select Interpreter" → elige el mismo ambiente que seleccionaste como kernel.

✦. Error de PowerShell sobre "running scripts is disabled" o similar
	pasa si le das clic en "Run" directamente sobre `analisis_canal.py` como si fuera un script independiente. 
	No lo es: es un módulo que el notebook importa. Corre el notebook, no el archivo `.py` directo.

✦. "No se encontraron estos archivos" o `FileNotFoundError`
	falta la carpeta `imagenes/` junto al notebook, o le faltan `.bmp` adentro con los nombres esperados.

✦. El kernel de conda no aparece en la lista de VS Code
	confirma que las extensiones Python y Jupyter estén instaladas; si aun así no aparece, prueba "Select Another Kernel" → "Python Environments" en vez del menú rápido.

✦. Cualquier otro error: copia el mensaje completo en rojo debajo de la celda (no solo la última línea) para poder revisarlo con contexto completo.

 
**** Para Dudas Y Aclaraciónes ✧｡٩(´ᗜ´ )و✧*｡ *****
Autora: Esmeralda Abigail Ortiz Cervantes
Expediente: 221203684
Correo: a221203684@unison.mx

