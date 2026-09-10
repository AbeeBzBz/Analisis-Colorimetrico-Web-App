import streamlit as st
from analisis_canal import (
    cargar_imagen_gris, detectar_roi_desde_referencia,
    construir_calibracion, procesar_gradiente
)

if "calibracion" not in st.session_state:
    st.session_state.calibracion = None

st.title("Analisis colorimetrico de microcanales")

st.header("1. Imagen de referencia")
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

st.header("2. Sustancia y grupos de concentracion")

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

st.header("3. Calibracion")

if len(grupos) < 2:
    st.info("Necesitas al menos 2 grupos con imagenes subidas (seccion 2) para calibrar.")
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
        st.error(resultado_cal.get("motivo", "No se pudo calibrar."))

st.header("4. Aplicar la calibracion a una imagen de gradiente")

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
                    st.warning("Una parte importante del perfil esta fuera del rango calibrado -- interpreta esa zona con cautela.")
        else:
            st.error(res_grad.get("motivo", "No se pudo procesar la imagen de gradiente."))