import streamlit as st
from analisis_canal import (
    cargar_imagen_gris, detectar_roi_desde_referencia,
    construir_calibracion, procesar_gradiente
)

if "calibracion" not in st.session_state:
    st.session_state.calibracion = None

st.title("Determinación de la concentración dentro de microcanales mediante el procesamiento digital de imágenes automatizado ٩(^ᗜ^ )و ")

st.header("1. Imagen de referencia ⭑.ᐟ")

st.markdown("Suba **una sola imagen** de tu canal del canal a evaluar con **buen** contraste ٩(⎚-⎚)"
             "-por ejemplo, la imagen con la bifase o cuelquiera donde el canal se vea calaramente distinto al fondo-"
             "Esta imagen se usa **una sola vez** para medir el ancho real del canal en píxeles" 
             "Ese ancho se usará para detectar el canal en todas las demás imágenes que subas más adelante.")

canal_oscuro = st.checkbox("El canal se ve mas oscuro que el fondo", value=True)
archivo_referencia = st.file_uploader(
    "Sube la imagen de referencia (buen contraste)",
    type=["bmp", "png", "jpg", "jpeg", "tif", "tiff"]
)

ancho_canal_ref = None
if archivo_referencia is not None:
    img_referencia = cargar_imagen_gris(archivo_referencia)
    resultado = detectar_roi_desde_referencia(img_referencia, canal_oscuro=canal_oscuro)
    if resultado["exito"]:
        ancho_canal_ref = resultado["ancho"]
        st.success(f"Ancho de canal detectado: {ancho_canal_ref} px")
        st.pyplot(resultado["figura"])
    else:
        st.error(resultado["motivo"])

st.header("2. Sustancia y grupos de concentracion ⭑.ᐟ")

st.markdown("aqui defines tus puntos de calibración conocidos, Necesitas **al menos 2 grupos**"
            "-por ejemplo, un 'blanco'de concentración 0 y 'maxima' con la concentración más alta-"
            ", cada uno con su respectiva imagen de referencia."
            "puedes subir varias imagenes por grupo, entre mas replicas, mas confiable queda la calibracion")

grupos = []
if ancho_canal_ref is None:
    st.info("Sube primero la imagen de referencia (seccion 1) para continuar aqui.")
else:
    nombre_sustancia = st.text_input("Nombre de la sustancia conocida", value="")
    n_grupos = st.number_input("Numero de grupos de concentracion", min_value=2, max_value=8, value=2, step=1)

    for i in range(int(n_grupos)):
        with st.expander(f"Grupo {i + 1}", expanded=(i < 2)):
            nombre_grupo = st.text_input(
                f"Nombre del grupo {i + 1}",
                value=("blanco" if i == 0 else f"grupo_{i + 1}"),
                key=f"nombre_{i}"
            )
            concentracion = st.number_input(
                f"Concentracion de '{nombre_grupo}' (mg/L)",
                min_value=0.0, value=(0.0 if i == 0 else 10.0), step=0.1, key=f"conc_{i}"
            )
            archivos_grupo = st.file_uploader(
                f"Imagenes de '{nombre_grupo}' (puedes subir varias)",
                type=["bmp", "png", "jpg", "jpeg", "tif", "tiff"],
                accept_multiple_files=True,
                key=f"archivos_{i}"
            )
            if archivos_grupo:
                imagenes_cargadas = [cargar_imagen_gris(a) for a in archivos_grupo]
                grupos.append({"nombre": nombre_grupo, "concentracion": concentracion, "imagenes": imagenes_cargadas})

    if grupos:
        st.write("**Grupos configurados hasta ahora:**")
        for g in grupos:
            st.write(f"- **{g['nombre']}**: {g['concentracion']} mg/L, {len(g['imagenes'])} imagen(es)")

st.header("3. Calibracion ⭑.ᐟ")

st.markdown(
    "Al presionar el boton, el programa detecta el canal en cada imagen de tus grupos, mide su "
    "intensidad promedio, y ajusta una recta entre intensidad y concentracion conocida. El "
    "**R²** te dice que tan bien se ajustan tus datos a esa recta -mas cerca de 1.0 es mejor-."
)

if len(grupos) < 2:
    st.info("Necesitas al menos 2 grupos con imagenes subidas (seccion 2) para calibrar ٩(ˋ ◠ ˊ )و")
else:
    if st.button("Ejecutar calibracion", type="primary"):
        with st.spinner("Detectando canal y ajustando la curva de calibracion..."):
            st.session_state.calibracion = construir_calibracion(grupos, ancho_canal_ref, canal_oscuro=canal_oscuro)

if st.session_state.calibracion is not None:
    resultado_cal = st.session_state.calibracion
    if resultado_cal["exito"]:
        st.success(f"Calibracion completa. R² = {resultado_cal['r2']:.4f}")
        st.markdown(f"**Ecuacion:** Concentracion = {resultado_cal['slope']:.4f} x Intensidad + {resultado_cal['intercept']:.4f}")
        st.pyplot(resultado_cal["figura_calibracion"])

        st.write("**Detalle por imagen:**")
        tabla = [{k: v for k, v in fila.items() if k != "figura"} for fila in resultado_cal["detalle"]]
        st.dataframe(tabla, use_container_width=True)

        with st.expander("Ver deteccion imagen por imagen"):
            for fila in resultado_cal["detalle"]:
                if "figura" in fila:
                    st.write(f"{fila['grupo']} - replica {fila['replica']} (confianza={fila.get('confianza', 0):.2f})")
                    st.pyplot(fila["figura"])
    else:
        st.error(resultado_cal.get("motivo", "No se pudo calibrar.(˙◠˙)"))

st.header("4. Aplicar la calibracion a una imagen de gradiente ⭑.ᐟ")

st.markdown(
    "Sube una imagen con un gradiente de concentracion -por ejemplo, un flujo bifase- para "
    "convertir su perfil de intensidad en un perfil real de concentracion, usando la ecuacion de "
    "calibracion de la seccion anterior. Si una parte del perfil resulta fuera del rango que "
    "calibraste, la app te avisa -esa zona es una extrapolacion, no una medicion directa.-"
)

calibracion_lista = st.session_state.calibracion is not None and st.session_state.calibracion.get("exito")

if not calibracion_lista:
    st.info("Completa una calibracion exitosa en la seccion 3 primero.")
else:
    archivo_gradiente = st.file_uploader(
        "Sube la imagen de flujo/gradiente a analizar",
        type=["bmp", "png", "jpg", "jpeg", "tif", "tiff"],
        key="gradiente"
    )
    if archivo_gradiente is not None:
        img_gradiente = cargar_imagen_gris(archivo_gradiente)
        cal = st.session_state.calibracion
        concentraciones_usadas = [g["concentracion"] for g in grupos]
        rango_valido = (min(concentraciones_usadas), max(concentraciones_usadas))

        res_grad = procesar_gradiente(
            img_gradiente, cal["slope"], cal["intercept"],
            ancho_canal_ref, canal_oscuro=canal_oscuro,
            rango_valido=rango_valido
        )
        if res_grad["exito"]:
            st.pyplot(res_grad["figura"])
            st.metric("Concentracion media en el canal", f"{res_grad['concentracion_media']:.4f} mg/L")
            if "porcentaje_fuera_de_rango" in res_grad:
                pct = res_grad["porcentaje_fuera_de_rango"]
                st.write(f"Porcentaje del perfil fuera del rango calibrado (extrapolacion): {pct:.1f}%")
                if pct > 20:
                    st.warning("Una parte importante del perfil esta fuera del rango calibrado - interpreta esa zona con cautela.")
        else:
            st.error(res_grad.get("motivo", "No se pudo procesar la imagen de gradiente. (˙◠˙) "))