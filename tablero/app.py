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
import streamlit as st

RAIZ = Path(__file__).resolve().parents[1]
PRONOSTICO = RAIZ / "data/oro/pronostico_teu.csv"
PRONOSTICO_EJEMPLO = RAIZ / "tablero/datos_ejemplo/pronostico_teu.csv"
ORO = RAIZ / "data/oro/mensual_integrado.csv"
RESUMEN = RAIZ / "calidad/e1/resumen.json"
FIABILIDAD = RAIZ / "calidad/e1/fiabilidad.json"
REPO = "https://github.com/gabeMoran05-coder/TDL-MANZADOCKER"
COLUMNAS = ["fecha", "tipo", "valor", "li_95", "ls_95", "modelo"]

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
