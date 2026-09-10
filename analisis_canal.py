"""
(˶ᵔ ᵕ ᵔ˶)ノ¨ Bienvenidos a ─ ★ analisis_canal.py ★ ─ 

 (╭ರᴗ•́) Esto es un modulo de analisis de imagenes de microcanales cuya función es la deteccion de canales en imagenes de chips de microfluidica y su calibración para la detección de concentracion basados en la conversión de los niveles de intensidad.

Converte los niveles detectados de intensidad a concentracion mediante el uso de un filtro adaptado (matched filter).ദ്ദി˙∇˙)ว (esto funcionó mejor para adaptarse y compensar las diferencias entre las condiciones de luz y pocición de la camara entre foto y foto)

Esta diseñado para ser usado desde notebooks de Jupyter o VScode. Es decir, validacion local. (│˶˙ᵕ˙˶)꜆ vea validacion_local.ipynb) por facilidad para quien lo use pueda cargar sus rutas locales con sus imagenes propias y tambien porque planea hacer una version que corra desde la app de Streamlit (app.py) para que sea de acceso más abierto sin que todo mundo ocupe modificar directamente el codigo}

1En otras palabras ◝(ᵔᗜᵔ)◜:
Ninguna función de aqui depende de rutas de archivo especificas o fijas, ni de Streamlit. Asi como, ninguna llama a plt.show() internamente (quien la use decide como mostrar la figura. ya sea: plt.show() en un notebook, o st.pyplot(fig en Streamlit).

Para la mejor comprensión y análisis de lo que sucede con las imagenes, las funciones de deteccion/analisis nos regresan un diccionario con al
menos la llave "exito" (bool). En caso de que "exito" sea False, nos manda una llave "motivo" con una descripcion legible del probable problema. ദ്ദി(˵ •̀ ᴗ - ˵ ) ✧
"""
#   Importar las Librerias ᕕ( ᐛ )ᕗ  #

import numpy as np
from scipy.signal import find_peaks
from scipy.stats import linregress
from skimage import filters, io
from skimage.util import img_as_float
import matplotlib.pyplot as plt


#   Cargar las imagenes ( ˶ˆᗜˆ˵ )   #
"""
Esta función carga una imagen y la pasa a escala de grises, con valores normalizados asignados de entre 0.0 y 1.0. (Donde: 0.0 es el negro absoluto o ausencia total de luz y 1.0 es blanco o la intensidad máxima permitida)

(˶ᵔᗜᵔ˶)ﾉﾞ En si "Fuente" puede ser:
⋆ Una ruta de archivo (str o Path), para uso local o notebook.
⋆ Un objeto tipo archivo (p. ej. lo que entrega st.file_uploader() en Streamlit, o un BytesIO), para uso en la tentativa app web.

Lanza "ValueError" (ᵕ—ᴗ—) con un mensaje legible si la imagen no se pudo cargar, en vez de fallar con una excepcion críptica de skimage o imageio.
"""
def cargar_imagen_gris(fuente):
    try:
        img = io.imread(fuente, as_gray=True)
        return img_as_float(img)
    except Exception as e:
        nombre = getattr(fuente, "name", fuente)
        raise ValueError(f" (ᵕ◞‸ ◟) No se pudo cargar la imagen '{nombre}': {e}")

#   Deteccion del ROI (Region Of Interest) de referencia utilizando una imagen de buen contraste (e.g. la de la bifase) \(˙ᵕ˙)  #

"""                              
Aqui se detecta la region de interes (ROI) de referencia a partir de una imagen de buen contraste (e.g la imagen de la bifase). 
    ⋆ Se usa una sola vez, al principio, para obtener el ancho de canal de referencia (en px). 
    ⋆ La deteccion en el resto de las imagenes (blanco, maxima, gradiente) usan detectar_canal_por_contraste() con ese ancho ya conocido. 
        Esta fue la solución o bueno compensación que se llego para el problema del leve desplazamiento del ROI de las imagenes de referencia del blanco debido al bajo contraste, diferentes condiciones de luz y posición de camara en las imagenes (◜ᴗ◝')

Encuentra todas las caidas fuertes de intensidad (posibles parades del canal), y elige como paredes del canal el par de caidas que esten más cercanas entre si.
    Ya que el canal es realmente una franja angosta, mientras que otras estructuras del chip (otro segmento, un borde del soporte, etc.) tipicamente estan mucho más separadas entre si. 
        ⋆ En caso de que el chip tenga varias estructuras y este criterio no elige la correcta, utilice: "rango_busqueda=(fila_min, fila_max)" para limitar donde busca el programa.

⋆ rango_busqueda: tupla (estructura de datos ordenada que permite almacenar una colección de elementos que no pueden modificarse después de ser creados) opcional (fila_min, fila_max) para restringir la busqueda a una region conocida de la imagen.

⋆ Devuelve un dict (diccionario) con: exito, y_top, y_bottom, y_center, ancho, todos_los_bordes (todas las posiciones candidatas encontradas, sirve para verificar visualmente que se eligio la pareja correcta), y (si generar_figura=True) figura (matplotlib.figure.Figure).
    O sea, la figura marca todos los bordes candidatos en naranja, y resalta en cian/amarillo el par elegido, para que puedas confirmar de un vistazo si la eleccion tiene sentido en tu imagen.
"""
def detectar_roi_desde_referencia(img, canal_oscuro=True, rango_busqueda=None,escala_um_por_px=None, generar_figura=True):
    
    alto_img, ancho_img = img.shape[:2]
    blur = filters.gaussian(img, sigma=3.0)
    perfil = np.mean(blur, axis=1)
    gradiente = np.diff(perfil)

    umbral = np.std(gradiente) * 1.5
    if canal_oscuro:
        #   Sabemos lo que son paredes ya que se ven como caídas de intensidad. Dicho de otra manera, Transiociones negativas.    #
        picos, _ = find_peaks(-gradiente, height=umbral, distance=20)
    else:
        picos, _ = find_peaks(gradiente, height=umbral, distance=20)

    picos = np.sort(picos)
    if rango_busqueda is not None:
        fila_min, fila_max = rango_busqueda
        picos = picos[(picos >= fila_min) & (picos <= fila_max)]

    if len(picos) < 2:
        return {
            "exito": False,
            "motivo": (
                f"Se necesitan al menos 2 bordes fuertes (las paredes) y solo se "
                f"encontraron {len(picos)}. Prueba ajustar canal_oscuro, rango_busqueda, "
                f"o revisar el contraste de la imagen ( ´･･)ﾉ(._.`) "
            ),
        }

    separaciones = np.diff(picos)
    idx_par = int(np.argmin(separaciones))
    y_top = int(picos[idx_par])
    y_bottom = int(picos[idx_par + 1])
    y_center = (y_top + y_bottom) // 2

    ancho_px = y_bottom - y_top
    resultado = {
        "exito": True,
        "y_top": y_top,
        "y_bottom": y_bottom,
        "y_center": y_center,
        "ancho": y_bottom - y_top,
        "todos_los_bordes": picos.tolist(),
        "dimensiones_imagen_px": (alto_img, ancho_img),
    }
    if escala_um_por_px is not None:
        resultado["ancho_um"]= ancho_px * escala_um_por_px
        resultado["dimensiones_imagen_um"]= (alto_img * escala_um_por_px, ancho_img * escala_um_por_px)

    if generar_figura:
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

        ax1.imshow(img, cmap="gray")
        etiqueta_usada = False
        for p in picos:
            es_descartado = p not in (y_top, y_bottom)
            etiqueta = None
            if es_descartado and not etiqueta_usada:
                etiqueta = "Otro borde detectado (descartado)"
                etiqueta_usada = True
            ax1.axhline(p, color="orange", lw=1, ls=":", alpha=0.6, label=etiqueta)
        ax1.axhline(y_top, color="cyan", lw=2, label="Pared superior del canal")
        ax1.axhline(y_bottom, color="magenta", lw=2, label="Pared inferior del canal")
        ax1.axhline(y_center, color="lime", lw=1.5, ls="-.", label="Centro del canal")

        x_flecha = ancho_img * 0.88
        ax1.annotate("", xy=(x_flecha, y_top), xytext=(x_flecha, y_bottom),
                      arrowprops=dict(arrowstyle="<->", color="white", lw=1.5))
        ax1.text(x_flecha - 5, y_center, f"{ancho_px} px", color="white", fontsize=9,
                  ha="right", va="center", rotation=90,
                  bbox=dict(facecolor="black", alpha=0.5, pad=1))

        ax1.set_title(f"Imagen ({alto_img}x{ancho_img} px) -- el canal detectado mide {ancho_px} px de ancho", fontsize=10)
        ax1.axis("off")
        ax1.legend(fontsize=7, loc="lower right")

        ax2.plot(perfil, "b-", lw=1.5, label="Intensidad promedio por fila")
        for p in picos:
            ax2.axvline(p, color="orange", ls=":", alpha=1.0)
        ax2.axvline(y_top, color="cyan", ls="--")
        ax2.axvline(y_bottom, color="magenta", ls="--")
        ax2.axvline(y_center, color="lime", ls="-.")
        ax2.set_xlabel("Posicion vertical (fila de la imagen, px)")
        ax2.set_ylabel("Intensidad media de esa fila (0=negro, 1=blanco)")
        ax2.set_title(f"Perfil de intensidad -- {len(picos)} bordes candidatos (naranja)\n"
                       f"cian/magenta = el programa elige el par mas cercano entre si como paredes del canal (ancho = {ancho_px})",
                       fontsize=9)
        ax2.grid(True, alpha=0.4)
        ax2.legend(fontsize=8)

        fig.text(0.5, -0.02,
                  f"En resumen (´∇´)/: el canal esta ubicado entre las filas {y_top} y {y_bottom} de la imagen "
                  f"({ancho_px} pixeles de ancho). Las lineas naranjas son otras posibles paredes que el "
                  f"programa considero pero no eligio.",
                  ha="center", fontsize=9, wrap=True,
                  bbox=dict(facecolor="lightyellow", edgecolor="gray", pad=6))

        plt.tight_layout()
        resultado["figura"] = fig

    return resultado



#   Detección de canal por filtro adaptado (matched filter). método que nos da resultados razonables incluso cuando las condiciones no son ideales (como el problema del bajo contraste, condiciones de luz y posición de cámara inconsistentes entre imagenes), siempre que se conozca el ancho del canal de antemano L(˶ᵔ ᵕ ᵔ˶)   #

"""
Detecta la posicion vertical de un canal de un ⋆ancho ya conocido⋆  comparando el promedio de intensidad dentro de una ventana de ese ancho contra el promedio de una banda más ancha (fondo) alrededor, y eligiendo la posición que  tiene más contraste.

A diferencia de buscar un solo pico de gradiente (sensible al ruido y al bajo contraste), aqui se promedia sobre ⋆todas⋆ las filas de la ventana,lo cual atenúa el ruido y es mucho más confiable en imagenes de bajo contraste (como las del blanco que son pura agua desionizada).

Devuelve un dict (diccionario) con: exito, y_top, y_bottom, y_center, ancho, confianza, perfil (arreglo 1D de intensidad promedio por fila), y (si generar_figura=True) figura.
"""
def detectar_canal_por_contraste(img, ancho_ref, canal_oscuro=True, margen=15, generar_figura=True):

    if img is None:
        return {"exito": False, "motivo": "Imagen invalida (None) [˙◠˙ ] "}

    ancho_ref = int(round(ancho_ref))
    blur = filters.gaussian(img, sigma=3.0)
    perfil = np.mean(blur, axis=1)

    kernel_dentro = np.ones(ancho_ref) / ancho_ref
    promedio_dentro = np.convolve(perfil, kernel_dentro, mode="valid")  
    #   tam. = n - ancho_ref + 1 (para promedio_dentro, con mode="valid") #

    ancho_fondo = ancho_ref + 2 * margen
    kernel_fondo = np.ones(ancho_fondo) / ancho_fondo
    promedio_fondo_full = np.convolve(perfil, kernel_fondo, mode="same")
    #   tam. = n (para promedio_fondo_full, con mode="same")    #

    centro_offset = ancho_ref // 2
    promedio_fondo = promedio_fondo_full[centro_offset: centro_offset + len(promedio_dentro)]

    if canal_oscuro:
        contraste = promedio_fondo - promedio_dentro
    else:
        contraste = promedio_dentro - promedio_fondo

    borde = max(50, margen)
    if len(contraste) <= 2 * borde:
        return {"exito": False, "motivo": "Imagen demasiado pequeña para el margen configurado ('~';) "}

    tramo_valido = contraste[borde: len(contraste) - borde]
    y_top = int(np.argmax(tramo_valido)) + borde
    y_bottom = y_top + ancho_ref
    y_center = (y_top + y_bottom) // 2
    confianza = float(contraste[y_top] / (np.std(perfil) + 1e-9))

    resultado = {
        "exito": True,
        "y_top": y_top,
        "y_bottom": y_bottom,
        "y_center": y_center,
        "ancho": ancho_ref,
        "confianza": confianza,
        "perfil": perfil,
        "contraste": contraste,
        "rango_busqueda_valido": (borde, len(contraste) - borde),
    }

    if generar_figura:
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

        ax1.imshow(img, cmap="gray")
        ax1.axhline(y_top, color="red", lw=2, label="Borde superior")
        ax1.axhline(y_bottom, color="red", lw=2, label="Borde inferior")
        ax1.axhline(y_center, color="lime", lw=1.5, ls="-.", label=f"Centro = {y_center}")
        ax1.set_title(f"Canal por contraste (confianza = {confianza:.2f})")
        ax1.axis("off")
        ax1.legend()

        ax2.plot(perfil, "b-", lw=1.2, alpha=0.7, label="Perfil de intensidad")
        ax2.axvline(y_top, color="green", ls="--", label="Y_top detectado")
        ax2.axvline(y_bottom, color="green", ls="--", label="Y_bottom detectado")
        ax2.set_xlabel("Posicion vertical (px)")
        ax2.set_ylabel("Intensidad promedio horizontal")
        ax2.set_title("Perfil de intensidad -- deteccion por contraste")
        ax2.legend(loc="upper left", fontsize=8)
        ax2.grid(True)

        ax2b = ax2.twinx()
        rango_contraste = np.arange(borde, len(contraste) - borde)
        ax2b.plot(rango_contraste, contraste[borde: len(contraste) - borde],
                   color="purple", alpha=0.6, lw=1.2, label="Contraste (aqui se elige el pico)")
        ax2b.axvline(y_top, color="green", ls="--")
        ax2b.set_ylabel("Contraste (mayor = mejor candidato)", color="purple")
        ax2b.tick_params(axis="y", labelcolor="purple")
        ax2b.legend(loc="upper right", fontsize=8)

        plt.tight_layout()
        resultado["figura"] = fig

    return resultado



#   Curva de calibracion (intensidad a concentracion) ᕙ( •̀ ᗜ •́ )ᕗ   #
    
"""
Construye la curva de calibracion de ✩intensidad a concentracion✩ a partir de N grupos de imagenes (no solo "blanco" y "maxima". Sino, cualquier número de puntos de concentracion, cada uno con cualquier número de replicas)

✩grupos✩: lista de diccionarios (dicts), cada uno con:
    ✩ "nombre": "blanco", "concentracion": 0.0, "imagenes": [arr1, arr2, ...]
    ✩ Las imagenes ya deben estar cargadas (ver cargar_imagen_gris).

Devuelve un diccionario con:
    ✩ exito, slope, intercept, r2, detalle (lista de resultados por imagen, cada uno con su propia figura de detección si generar_figuras=True), intensidades, concentraciones, y figura_calibracion (grafica) de intensidad vs. concentracion con la recta ajustada).
"""

def construir_calibracion(grupos, ancho_canal_ref, canal_oscuro=True, generar_figuras=True):

    intensidades, concentraciones, detalle = [], [], []

    for grupo in grupos:
        nombre = grupo["nombre"]
        conc = grupo["concentracion"]
        for i, img in enumerate(grupo["imagenes"]):
            fila = {"grupo": nombre, "replica": i + 1, "concentracion_objetivo": conc}

            res = detectar_canal_por_contraste(
                img, ancho_canal_ref, canal_oscuro=canal_oscuro, generar_figura=generar_figuras
            )
            if not res.get("exito"):
                fila["estado"] = f"( • ᴖ •)!! NO DETECTADO ({res.get('motivo', '')})"
                detalle.append(fila)
                continue

            mean_int = float(np.mean(img[res["y_top"]:res["y_bottom"], :]))
            intensidades.append(mean_int)
            concentraciones.append(conc)

            fila.update({
                "estado": "OK",
                "intensidad": mean_int,
                "y_top": res["y_top"],
                "y_bottom": res["y_bottom"],
                "confianza": res["confianza"],
            })
            if "figura" in res:
                fila["figura"] = res["figura"]
            detalle.append(fila)

    if len(intensidades) < 2:
        return {
            "exito": False,
            "motivo": "Puntos validos insuficientes (´•︵•`) se necesitan al menos 2 con detección exitosa",
            "detalle": detalle,
        }

    slope, intercept, r_value, _, _ = linregress(intensidades, concentraciones)

    resultado = {
        "exito": True,
        "slope": slope,
        "intercept": intercept,
        "r2": r_value ** 2,
        "detalle": detalle,
        "intensidades": intensidades,
        "concentraciones": concentraciones,
    }

    if generar_figuras:
        fig, ax = plt.subplots(figsize=(7, 5))
        ax.scatter(intensidades, concentraciones, color="tab:blue", zorder=3, label="Datos")
        x_line = np.linspace(min(intensidades), max(intensidades), 50)
        ax.plot(
            x_line, slope * x_line + intercept, "r--",
            label=f"Ajuste: y = {slope:.3f}x + {intercept:.3f}\nR² = {r_value ** 2:.4f}",
        )
        ax.set_xlabel("Intensidad media")
        ax.set_ylabel("Concentracion (mg/L)")
        ax.set_title("Curva de calibracion")
        ax.legend()
        ax.grid(True)
        resultado["figura_calibracion"] = fig

    return resultado



#  ( ◡̀_◡́)ᕤ Aplicar la calibración a una imagen de gradiente de concentracion o bifase real   #
"""
Se aplica la ecuación de calibracion (slope, intercept) a una imagen con flujo en bifase o con gradiente de concentraciones para obtener el perfil y mapa de concentracion real a lo largo del canal.

Devuelve un diccionario (dicts) con: exito, y_top, y_bottom, perfil_intensidad, perfil_concentracion, mapa_concentracion, concentracion_media, y (si generar_figura=True) figura. ദ്ദി(ᵔᗜᵔ)
"""

def procesar_gradiente(img, slope, intercept, ancho_canal_ref, canal_oscuro=True, rango_valido=None, generar_figura=True):    

    
    res = detectar_canal_por_contraste(img, ancho_canal_ref, canal_oscuro=canal_oscuro, generar_figura=False)
    if not res.get("exito"):
        return {"exito": False, "motivo": f" No se pudo detectar el canal: {res.get('motivo', '')} (˙𐃷˙;)"}

    y_top, y_bottom = res["y_top"], res["y_bottom"]
    canal = img[y_top:y_bottom, :]
    perfil_intensidad = np.mean(canal, axis=1)
    perfil_concentracion = slope * perfil_intensidad + intercept
    posicion = np.arange(len(perfil_concentracion))
    mapa_concentracion = np.tile(perfil_concentracion[:, np.newaxis], (1, canal.shape[1]))

    resultado = {
        "exito": True,
        "y_top": y_top,
        "y_bottom": y_bottom,
        "perfil_intensidad": perfil_intensidad,
        "perfil_concentracion": perfil_concentracion,
        "mapa_concentracion": mapa_concentracion,
        "concentracion_media": float(np.mean(perfil_concentracion)),
    }

    if rango_valido is not None:
        conc_min, conc_max = rango_valido 
        fuera_de_rango = (perfil_concentracion < conc_min) | (perfil_concentracion > conc_max)
        resultado["porcentaje_fuera_de_rango"] = float(np.mean(fuera_de_rango) * 100)
        resultado["rango_valido"] = (conc_min, conc_max)

    if generar_figura:
        fig, axes = plt.subplots(2, 2, figsize=(13, 9))

        axes[0, 0].imshow(img, cmap="gray")
        axes[0, 0].axhline(y_top, color="r", lw=2)
        axes[0, 0].axhline(y_bottom, color="r", lw=2)
        axes[0, 0].set_title("Imagen original")
        axes[0, 0].axis("off")

        im = axes[0, 1].imshow(mapa_concentracion, cmap="viridis", aspect="auto")
        plt.colorbar(im, ax=axes[0, 1], label="Concentracion (mg/L)")
        axes[0, 1].set_title("Mapa de concentracion pixel por pixel")
        axes[0, 1].set_xlabel("Ancho del canal (px)")
        axes[0, 1].set_ylabel("Altura del canal (px)")

        axes[1, 0].plot(posicion, perfil_concentracion, "b-", lw=2, label="Concentracion estimada", zorder=3)
        if rango_valido is not None:
            axes[1, 0].axhspan(conc_min, conc_max, color="green", alpha=0.1, label="Rango calibrado (confiable)")
            axes[1, 0].axhline(conc_min, color="green", ls="--", lw=1, alpha=0.6)
            axes[1, 0].axhline(conc_max, color="green", ls="--", lw=1, alpha=0.6)
            axes[1, 0].legend(fontsize=8)
        axes[1, 0].set_xlabel("Posicion a lo largo del canal (px)")
        axes[1, 0].set_ylabel("Concentracion (mg/L)")
        axes[1, 0].set_title("Perfil de concentracion (fuera de la franja verde = extrapolación)")
        axes[1, 0].grid(True)

        axes[1, 1].imshow(canal, cmap="gray")
        axes[1, 1].set_title("Zona del canal (ampliada)")
        axes[1, 1].axis("off")

        plt.tight_layout()
        resultado["figura"] = fig

    return resultado
    