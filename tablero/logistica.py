"""Comparador de trayectos públicos y costos de sesión."""

from pathlib import Path

import pandas as pd
import requests
import streamlit as st

from src.rutas import cargar_catalogo, consultar_ruta, costear


@st.cache_data(ttl=86400, max_entries=100, show_spinner=False)
def ruta_vial(lat_a: float, lon_a: float, lat_b: float, lon_b: float, regreso: bool):
    return consultar_ruta({"lat": lat_a, "lon": lon_a}, {"lat": lat_b, "lon": lon_b}, regreso)


def aplicar_costo(valor: float) -> None:
    st.session_state["negocio_costo_variable"] = round(valor, 2)
    st.session_state["aviso_costo_ruta"] = True


def mostrar_comparador(raiz: Path) -> tuple[list[dict], list[dict]]:
    catalogo = cargar_catalogo(raiz)
    por_id = {r["id_denue"]: r for r in catalogo}
    def etiqueta(k):
        return f'{por_id[k]["nombre"]} · {por_id[k]["tipo"]}'
    st.markdown("**Compara recorridos y costos por servicio**")
    st.caption("Ubicaciones públicas del DENUE: referencias de establecimientos, no puertas "
               "de acceso certificadas. Confirma acceso, horario y condiciones con cada operador.")
    ids = list(por_id)
    inicial = next((i for i, k in enumerate(ids) if por_id[k]["tipo"] == "Terminal portuaria"), 0)
    origen_id = st.selectbox("Origen del servicio", ids, index=inicial, format_func=etiqueta)
    disponibles = [k for k in ids if k != origen_id]
    preferidos = [k for k in ["6860189", "344488"] if k in disponibles]
    destinos = st.multiselect("Destinos a comparar", disponibles, default=preferidos[:2],
                             max_selections=2, format_func=etiqueta)
    regreso = st.checkbox("Incluir regreso al origen", value=False)
    modo = st.radio("Distancia para el cálculo", ["Consultar referencia vial", "Ingresar km validados"],
                    horizontal=True)
    rutas = []
    if modo == "Consultar referencia vial":
        firma = (origen_id, tuple(destinos), regreso)
        if st.button("Consultar recorridos", disabled=not destinos):
            obtenidas, errores = [], []
            with st.spinner("Consultando distancias viales de referencia…"):
                for identificador in destinos:
                    a, b = por_id[origen_id], por_id[identificador]
                    try:
                        ruta = ruta_vial(a["lat"], a["lon"], b["lat"], b["lon"], regreso)
                        obtenidas.append({**ruta, "destino_id": identificador,
                                          "destino": b["nombre"]})
                    except (requests.RequestException, ValueError, KeyError, TypeError, RuntimeError, OSError):
                        errores.append(b["nombre"])
            st.session_state["consulta_trayectos"] = (firma, obtenidas, errores)
        anterior = st.session_state.get("consulta_trayectos")
        if anterior and anterior[0] == firma:
            rutas = anterior[1]
            for nombre in anterior[2]:
                st.warning(f"No se obtuvo recorrido para {nombre}. Puedes ingresar km validados.")
        st.caption("OSRM/FOSSGIS calcula un recorrido para automóvil, sin tráfico en tiempo real. "
                   "No valida pesos, alturas ni permisos para tractocamión. Uso para planeación; "
                   "confirma los km de tu operación antes de cotizar.")
        st.markdown("[Fuente y condiciones del motor](https://routing.openstreetmap.de/about.html) · "
                    "[Corregir cartografía OSM](https://www.openstreetmap.org/fixthemap)")
    elif destinos:
        elegido = st.selectbox("Destino de los km validados", destinos, format_func=etiqueta)
        km = st.number_input("Kilómetros totales del servicio validado", min_value=0.1,
                             value=None, help="Incluye el regreso si lo seleccionaste; no se duplican los km.")
        if km is not None:
            rutas = [{"distancia_km": km, "destino_id": elegido, "destino": por_id[elegido]["nombre"],
                      "coordenadas": None, "regreso": regreso, "fuente": "Km ingresados por el usuario"}]
    c1, c2 = st.columns(2)
    costo_km = c1.number_input("Costo variable por kilómetro (MXN, sin esperas)", min_value=0.0, value=None)
    extras = c2.number_input("Otros costos del servicio (MXN)", min_value=0.0, value=0.0,
                            help="Casetas o maniobras que pague tu empresa. Cero si no aplican.")
    st.caption("Usa costos de tu unidad. Excluye del costo/km las partidas ya incluidas en costos "
               "fijos mensuales. La espera y el cobro se toman del escenario de operación de arriba.")
    filas, costos = [], {}
    for ruta in rutas:
        fila = {"Destino": ruta["destino"], "Distancia del servicio (km)": round(ruta["distancia_km"], 3),
                "Recorrido": "Ida y regreso" if regreso else "Solo ida"}
        if costo_km is not None:
            costo = costear(ruta["distancia_km"], costo_km, extras,
                            st.session_state.get("negocio_horas"), st.session_state.get("negocio_costo_hora"),
                            st.session_state.get("negocio_tarifa"))
            costos[ruta["destino_id"]] = costo
            fila.update({"Costo sin esperas (MXN)": round(costo["costo_sin_esperas"], 2),
                         "Costo con esperas (MXN)": costo["costo_con_espera"],
                         "Margen antes de costos fijos (MXN)": costo["margen_contribucion"]})
        filas.append(fila)
        if ruta.get("fecha_consulta_utc"):
            st.caption(f'{ruta["destino"]} · consulta UTC: {ruta["fecha_consulta_utc"]} · '
                       f'ajuste máximo a red vial: {max(ruta["ajustes_m"], default=0):.1f} m.')
    if filas:
        st.dataframe(pd.DataFrame(filas), hide_index=True, width="stretch")
        if costo_km is None:
            st.info("Ingresa el costo por kilómetro de tu unidad para comparar costos.")
        elif costos:
            elegido = st.selectbox("Destino para el escenario mensual", list(costos), format_func=etiqueta)
            st.button("Usar este costo sin esperas en el escenario mensual",
                      on_click=aplicar_costo, args=(costos[elegido]["costo_sin_esperas"],))
            st.caption("Copia únicamente el costo variable sin esperas; las esperas se calculan "
                       "por separado para evitar contarlas dos veces. Los costos son escenarios, no cotizaciones.")
    with st.expander("Ubicaciones y procedencia del catálogo"):
        st.dataframe(pd.DataFrame(catalogo)[["nombre", "tipo", "id_denue", "lat", "lon",
                                             "fecha_captura_utc", "registro_csv_origen"]], hide_index=True)
        st.markdown("[Fuente: INEGI, DENUE Colima](https://www.inegi.org.mx/contenidos/masiva/denue/denue_06_csv.zip)")
    return catalogo, [r for r in rutas if r.get("coordenadas")]
