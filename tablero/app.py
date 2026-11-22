"""Tablero público del Observatorio del Puerto de Manzanillo.

Ejecutar desde la raíz del repositorio:  streamlit run tablero/app.py

Lee solo archivos ya generados por el pipeline (no hace peticiones a las fuentes):
- data/oro/pronostico_teu.csv   pronóstico oficial (notebook de Estadística)
  · si aún no existe, usa tablero/datos_ejemplo/pronostico_teu.csv y lo avisa
- data/oro/mensual_integrado.csv  serie mensual validada
- calidad/e1/resumen.json         resultado de la puerta de calidad
- calidad/e1/fiabilidad.json      disponibilidad de la captura
"""

from __future__ import annotations

import json
from pathlib import Path

import altair as alt
import pandas as pd
import pydeck as pdk
import streamlit as st

RAIZ = Path(__file__).resolve().parents[1]
PRONOSTICO = RAIZ / "data/oro/pronostico_teu.csv"
PRONOSTICO_EJEMPLO = RAIZ / "tablero/datos_ejemplo/pronostico_teu.csv"
ORO = RAIZ / "data/oro/mensual_integrado.csv"
RESUMEN = RAIZ / "calidad/e1/resumen.json"
FIABILIDAD = RAIZ / "calidad/e1/fiabilidad.json"
REPO = "https://github.com/gabeMoran05-coder/TDL-MANZADOCKER"
COLUMNAS = ["fecha", "tipo", "valor", "li_95", "ls_95", "modelo"]


def mostrar_negocio() -> None:
    # Cálculo local a la sesión: los datos del cliente no se persisten ni se envían a una API.
    import sys

    if str(RAIZ) not in sys.path:
        sys.path.insert(0, str(RAIZ))
    from src.negocio import escenario

    st.subheader("¿Cuánto deja la operación de tu transportista?")
    st.write("Para transportistas que retiran contenedores de importación en Manzanillo. "
             "Planea capacidad y compara costos mensuales con tus propios datos agregados.")
    st.caption("Escenario de planeación. El volumen del puerto no equivale a tus viajes; "
               "el pronóstico mensual no predice citas ni horas de espera.")
    if st.session_state.pop("aviso_costo_ruta", False):
        st.success("Costo variable actualizado desde el comparador del mapa.")
    with st.expander("Calcular capacidad, costo de esperas y resultado operativo"):
        a, b = st.columns(2)
        solicitados = a.number_input("Servicios solicitados en el mes", min_value=0, value=None, key="negocio_solicitados")
        capacidad = b.number_input("Capacidad mensual en servicios", min_value=0, value=None, key="negocio_capacidad")
        tarifa = a.number_input("Ingreso cobrado por servicio (MXN, sin IVA)", min_value=0.0, value=None, key="negocio_tarifa")
        costo = b.number_input("Costo variable por servicio, sin esperas (MXN)", min_value=0.0, value=None, key="negocio_costo_variable")
        horas = a.number_input("Horas de espera por servicio", min_value=0.0, value=None, key="negocio_horas")
        costo_hora = b.number_input("Costo por hora de espera (MXN)", min_value=0.0, value=None, key="negocio_costo_hora")
        fijos = a.number_input("Costos fijos mensuales asignados (MXN)", min_value=0.0, value=None, key="negocio_fijos")
        precio = b.number_input("Costo mensual de la app a evaluar (MXN)", min_value=0.0, value=None, key="negocio_suscripcion")
        if all(v is not None for v in [solicitados, capacidad, tarifa, costo, horas, costo_hora, fijos, precio]):
            r = escenario(solicitados=solicitados, capacidad=capacidad, tarifa=tarifa,
                          costo_variable=costo, horas_espera=horas, costo_hora=costo_hora,
                          costos_fijos=fijos, suscripcion=precio)
            c1, c2, c3 = st.columns(3)
            c1.metric("Servicios atendibles", r["servicios_atendibles"])
            c2.metric("Costo de esperas estimado", f'${r["costo_esperas_estimado"]:,.2f}')
            c3.metric("Resultado operativo estimado", f'${r["resultado_operativo_estimado"]:,.2f}')
            st.write(f'Servicios sin capacidad: {r["servicios_sin_capacidad"]}. '
                     f'Margen por servicio: ${r["margen_contribucion_por_servicio"]:,.2f} MXN.')
            if r["margen_contribucion_por_servicio"] < 0:
                st.warning("Con estos supuestos, cada servicio deja margen negativo. "
                           "Revisa la cotización y sus costos antes de comprometer capacidad.")
            st.caption("Estimación según tus entradas, antes de intereses e impuestos. "
                       "No acredita ahorro conseguido ni garantiza demanda. Evita contar un costo dos veces.")
        else:
            st.info("Completa las ocho entradas con datos de tu operación. No usamos cifras inventadas.")


def mostrar_geografia() -> None:
    from tablero.logistica import mostrar_comparador

    ruta = RAIZ / "data/oro/denue_celdas.csv"
    st.subheader("Entorno industrial y portuario de Manzanillo")
    if not ruta.exists():
        st.info("El contexto geográfico todavía no está disponible en esta actualización.")
        return
    tabla_celdas = pd.read_csv(ruta)
    try:
        catalogo, recorridos = mostrar_comparador(RAIZ)
    except (OSError, ValueError, KeyError):
        catalogo, recorridos = [], []
        st.info("El catálogo logístico no está disponible en esta actualización.")
    agregado = []
    ruta_celdas = RAIZ / "data/oro/denue_celdas.csv"
    if ruta_celdas.exists():
        tabla_celdas = pd.read_csv(ruta_celdas)
        maximo = max(int(tabla_celdas.total.max()), 1)
        agregado = [{
            "coordenadas": [[c.oeste, c.sur], [c.este, c.sur], [c.este, c.norte], [c.oeste, c.norte]],
            # un solo tono, más opaco donde hay más establecimientos
            "color": [42, 120, 214, int(40 + 160 * c.total / maximo)],
            "nombre": "Celda de ~1 km (agregado DENUE)",
            "tipo": f"{int(c.total)} establecimientos logísticos", "id_denue": "agregado",
            "lat": c.lat, "lon": c.lon,
        } for c in tabla_celdas.itertuples()]
    densidad = pdk.Layer("PolygonLayer", data=agregado, get_polygon="coordenadas",
                         get_fill_color="color", get_line_color=[255, 255, 255],
                         line_width_min_pixels=1, pickable=True)
    celdas = [{"coordenadas": [[x0, y0], [x1, y0], [x1, y1], [x0, y1]]}
              for x0, x1 in [(-104.36, -104.30), (-104.30, -104.24)]
              for y0, y1 in [(18.99, 19.06), (19.06, 19.13)]]
    rejilla = pdk.Layer("PolygonLayer", data=celdas, get_polygon="coordenadas",
                        filled=False, stroked=True, get_line_color=[130, 130, 130],
                        line_width_min_pixels=1)
    sitios = pdk.Layer("ScatterplotLayer", data=catalogo, get_position="[lon, lat]",
                       get_radius=90, get_fill_color=[238, 128, 40], pickable=True)
    trayectos = pdk.Layer("PathLayer", data=recorridos, get_path="coordenadas",
                          get_color=[17, 138, 72], get_width=4, width_min_pixels=3)
    st.pydeck_chart(pdk.Deck(layers=[densidad, rejilla, sitios, trayectos], map_style="light", map_provider="carto",
                            initial_view_state=pdk.ViewState(latitude=19.06, longitude=-104.30, zoom=11),
                            tooltip={"text": "{nombre}\n{tipo}\nDENUE {id_denue}\n{lat}, {lon}"}))
    st.caption("Celdas azules: cuántos establecimientos de logística hay en cada cuadro de ~1 km "
               "(más intenso = más establecimientos). "
               "Naranja: catálogo de referencia. Verde: recorrido consultado.")
    if agregado:
        total = int(tabla_celdas.total.sum())
        st.caption(f"{total} establecimientos en {len(agregado)} celdas. Las celdas con menos de "
                   f"{int(tabla_celdas.k_minimo.iloc[0])} establecimientos no se muestran, para que "
                   "se reduzca el riesgo de identificación. Es una rejilla de estudio, no un límite oficial; "
                   "el municipio sí es el que asigna INEGI.")
    st.markdown("**Establecimientos:** [INEGI, DENUE](https://www.inegi.org.mx/inegi/terminos.html). "
                "**Mapa base:** © OpenStreetMap contributors / CARTO. "
                "**Recorridos:** OSRM/FOSSGIS, datos OSM bajo "
                "[ODbL](https://www.openstreetmap.org/copyright).")
    st.caption(f'Captura: {tabla_celdas.fecha_captura_utc.iloc[0]}. '
               "Conteos de establecimientos SCIAN 484/488/493; no son "
               "rutas, accesos ni límites oficiales. Las cuatro celdas son de estudio. "
               "El mapa actual no se usa para explicar ni predecir TEU históricos.")
    with st.expander("Ver objetos y procedencia"):
        st.dataframe(tabla_celdas[["celda", "total", "zona_estudio", "url_origen", "fecha_captura_utc"]],
                     hide_index=True)
        st.download_button("Descargar contexto geográfico (INEGI)", ruta.read_bytes(),
                           file_name=ruta.name, mime="text/csv")

AZUL = "#2a78d6"  # un solo tono: real y pronóstico son la misma magnitud
MESES = ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto",
         "septiembre", "octubre", "noviembre", "diciembre"]
MOTIVOS = {
    "periodo_no_publicado":
        "Meses que ASIPONA todavía no publica. Se apartan para no contarlos como cero.",
    "periodo_posterior_a_captura":
        "Meses posteriores a la fecha en que se descargó el informe.",
}

st.set_page_config(page_title="Observatorio del Puerto de Manzanillo",
                   page_icon="⚓", layout="centered")


def mes_texto(fecha: pd.Timestamp) -> str:
    return f"{MESES[fecha.month - 1]} {fecha.year}"


def miles(n: float) -> str:
    return f"{n:,.0f}"


def firma(*rutas: Path) -> tuple:
    """Cambia cuando un archivo aparece o se modifica: invalida la caché."""
    return tuple((r.name, r.stat().st_mtime if r.exists() else None) for r in rutas)


@st.cache_data
def cargar_pronostico(version: tuple) -> tuple[pd.DataFrame, bool]:
    ruta, es_ejemplo = (PRONOSTICO, False) if PRONOSTICO.exists() else (PRONOSTICO_EJEMPLO, True)
    datos = pd.read_csv(ruta, parse_dates=["fecha"])
    faltan = set(COLUMNAS) - set(datos.columns)
    if faltan:
        raise ValueError(f"{ruta.name} no cumple el contrato; faltan columnas: {sorted(faltan)}")
    datos["mes"] = datos["fecha"].map(mes_texto)
    return datos.sort_values("fecha").reset_index(drop=True), es_ejemplo


@st.cache_data
def cargar_json(ruta: Path, version: tuple) -> dict | None:
    return json.loads(ruta.read_text(encoding="utf-8")) if ruta.exists() else None


def grafica(datos: pd.DataFrame) -> alt.LayerChart:
    hist = datos[datos["tipo"] == "historico"]
    pron = datos[datos["tipo"] == "pronostico"]
    # el pronóstico y su banda arrancan en el último mes real: la incertidumbre
    # empieza en cero donde termina el dato observado
    ancla = hist.tail(1).assign(li_95=hist["valor"].iloc[-1], ls_95=hist["valor"].iloc[-1])
    puente = pd.concat([ancla, pron])
    lineas = pd.concat([hist.assign(serie="Real"), puente.assign(serie="Pronóstico")])

    x = alt.X("fecha:T", title=None,
              axis=alt.Axis(format="%Y", tickCount="year", grid=False, labelColor="#898781"))
    y = alt.Y("valor:Q", title=None, scale=alt.Scale(zero=False),
              axis=alt.Axis(format=",.0f", gridColor="#e1e0d9", gridOpacity=0.6,
                            labelColor="#898781", tickCount=5))
    info = [alt.Tooltip("mes:N", title="Mes"),
            alt.Tooltip("valor:Q", title="TEU", format=",.0f"),
            alt.Tooltip("li_95:Q", title="Mínimo probable (95%)", format=",.0f"),
            alt.Tooltip("ls_95:Q", title="Máximo probable (95%)", format=",.0f")]

    banda = alt.Chart(puente).mark_area(color=AZUL, opacity=0.18).encode(
        x=x, y="li_95:Q", y2="ls_95:Q")
    trazo = alt.Chart(lineas).mark_line(color=AZUL, strokeWidth=2).encode(
        x=x, y=y, detail="serie:N",
        strokeDash=alt.StrokeDash(
            "serie:N", title=None,
            scale=alt.Scale(domain=["Real", "Pronóstico"], range=[[1, 0], [6, 4]]),
            legend=alt.Legend(orient="top", direction="horizontal", symbolStrokeColor=AZUL,
                              symbolStrokeWidth=2, labelColor="#898781", symbolSize=300)))
    puntos = alt.Chart(pron).mark_point(color=AZUL, filled=True, size=70).encode(x=x, y=y)

    # capa de lectura: línea vertical y punto en el mes más cercano al cursor
    cerca = alt.selection_point(nearest=True, on="pointerover", fields=["fecha"], empty=False)
    lector = alt.Chart(datos).mark_rule(color="#898781", strokeWidth=1).encode(
        x="fecha:T",
        opacity=alt.condition(cerca, alt.value(0.6), alt.value(0)),
        tooltip=info,
    ).add_params(cerca)
    marca = alt.Chart(datos).mark_point(color=AZUL, filled=True, size=60).encode(
        x="fecha:T", y="valor:Q",
        opacity=alt.condition(cerca, alt.value(1), alt.value(0)))

    return alt.layer(banda, trazo, puntos, lector, marca).properties(
        height=320).configure_view(strokeWidth=0)


def main() -> None:
    try:
        datos, es_ejemplo = cargar_pronostico(firma(PRONOSTICO, PRONOSTICO_EJEMPLO))
    except (FileNotFoundError, ValueError) as error:
        st.error(f"No se pudo cargar el pronóstico: {error}")
        st.stop()

    hist = datos[datos["tipo"] == "historico"]
    pron = datos[datos["tipo"] == "pronostico"]
    ultimo = hist.iloc[-1]
    siguiente = pron.iloc[0]

    st.title("Observatorio del Puerto de Manzanillo")
    st.caption(
        f"Contenedores movidos cada mes, medidos en TEU (un TEU = un contenedor de 20 pies). "
        f"Último mes publicado por ASIPONA: **{ultimo['mes']}**."
    )

    mostrar_negocio()

    if es_ejemplo:
        st.warning(
            "**Pronóstico de ejemplo.** Estas cifras usan un método sencillo (repetir el mismo "
            "mes del año anterior) solo para probar el tablero. El pronóstico oficial se "
            "publicará aquí cuando se integre el análisis estadístico del equipo.",
            icon="⚠️",
        )

    # --- La respuesta primero -------------------------------------------------------------
    st.subheader(f"¿Cuántos contenedores en {siguiente['mes']}?")
    col1, col2 = st.columns(2)
    col1.metric("Pronóstico", f"{miles(siguiente['valor'])} TEU")
    col2.metric("Rango probable (95%)",
                f"{miles(siguiente['li_95'])} – {miles(siguiente['ls_95'])}")
    st.markdown(
        f"> En {siguiente['mes']} esperamos alrededor de **{miles(siguiente['valor'])} TEU**. "
        f"Si el puerto mantiene el comportamiento de los meses anteriores, lo más probable "
        f"es que el movimiento real quede entre **{miles(siguiente['li_95'])}** y "
        f"**{miles(siguiente['ls_95'])}** (rango del 95% según el modelo; no es una "
        f"garantía). Úsalo para planear flota y contratos del mes; no reemplaza el aviso de "
        f"tu cliente para la operación de cada día."
    )

    # --- La evidencia -----------------------------------------------------------------------
    st.subheader("TEU por mes: real y pronóstico")
    st.altair_chart(grafica(datos), width="stretch")
    st.caption(
        f"Línea sólida: TEU reales desde {hist['mes'].iloc[0]}. Línea punteada: pronóstico de "
        f"los próximos {len(pron)} meses; la franja sombreada es el rango probable al 95%. "
        f"Modelo: {siguiente['modelo']}."
    )
    with st.expander("Ver los datos en tabla"):
        def celda(n) -> str:
            return "—" if pd.isna(n) or n == "" else miles(float(n))

        tabla = pd.DataFrame({
            "Mes": datos["mes"],
            "Tipo": datos["tipo"].map({"historico": "Real", "pronostico": "Pronóstico"}),
            "TEU": datos["valor"].map(celda),
            "Mínimo probable (95%)": datos["li_95"].map(celda),
            "Máximo probable (95%)": datos["ls_95"].map(celda),
        })
        st.dataframe(tabla.iloc[::-1], hide_index=True, width="stretch")

    mostrar_geografia()

    # --- La confianza -----------------------------------------------------------------------
    st.subheader("¿Por qué confiar en estas cifras?")
    resumen = cargar_json(RESUMEN, firma(RESUMEN))
    fiab = cargar_json(FIABILIDAD, firma(FIABILIDAD))
    c1, c2, c3 = st.columns(3)
    if resumen:
        a = resumen["asipona"]
        c1.metric("Registros del puerto aceptados", f"{a['aceptados']} de {a['entrada']}")
        c2.metric("Apartados en cuarentena", f"{a['rechazados']}")
    if fiab and fiab["programadas"]["tasa_exito"] is not None:
        cal = fiab["calendario"]
        c3.metric("Días con captura exitosa",
                  f"{cal['dias_con_exito']} de {cal['dias_periodo']}")

    if resumen and resumen.get("rechazos_por_motivo"):
        # un registro puede tener varios motivos ("a; b"): se cuenta en cada uno
        conteo: dict[str, int] = {}
        for motivo, n in resumen["rechazos_por_motivo"].items():
            for parte in motivo.split(";"):
                conteo[parte.strip()] = conteo.get(parte.strip(), 0) + n
        renglones = "\n".join(
            f"- **{n}** · {MOTIVOS.get(m, m)}"
            for m, n in sorted(conteo.items(), key=lambda par: -par[1]))
        st.markdown("Cada dato pasa por una **puerta de calidad** automática. Lo que no cumple "
                    "las reglas no se borra: se aparta con su motivo. Un registro puede tener "
                    "más de un motivo.\n\n" + renglones)

    st.markdown(
        "**Fuentes:** Estadística Mensual de "
        "[ASIPONA Manzanillo](https://www.puertomanzanillo.com.mx/esps/0000209/estadisticas.html) "
        "y tipo de cambio FIX del [Banco de México](https://www.banxico.org.mx/SieAPIRest/). "
        f"Código, datos y metodología: [repositorio del proyecto]({REPO})."
    )
    st.caption("Proyecto Integrador Trusted Data Lab · TecNM, Instituto Tecnológico de Colima · "
               "Sello TDL: en evaluación.")


main()
