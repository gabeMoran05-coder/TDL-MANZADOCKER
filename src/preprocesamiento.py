"""Imputación causal, diagnóstico de atípicos y escalas sin fuga temporal."""

from __future__ import annotations

import numpy as np
import pandas as pd


def imputar_causal(datos: pd.DataFrame) -> pd.DataFrame:
    """Solo valores ausentes; nunca corrige negativos, texto corrupto o infinitos.

    Usa hasta tres observaciones reales anteriores de la misma variable. Los
    valores imputados no alimentan otra imputación y el objetivo no se inventa.
    """
    resultado = datos.copy()
    for _, grupo in datos.groupby("variable", sort=True):
        anteriores: list[float] = []
        for indice in grupo.sort_values("fecha").index:
            valor = datos.at[indice, "valor"]
            if pd.isna(valor):
                if datos.at[indice, "variable"] != "teu_total" and anteriores:
                    resultado.at[indice, "valor"] = float(np.median(anteriores[-3:]))
                    resultado.at[indice, "imputado"] = True
                    resultado.at[indice, "metodo_imputacion"] = "mediana_3_observados_previos"
            elif np.isfinite(valor) and valor >= 0:
                anteriores.append(float(valor))
    return resultado


def ajustar(serie: pd.Series) -> dict[str, float]:
    valores = serie.dropna().astype(float)
    if valores.empty or not np.isfinite(valores).all():
        raise ValueError("No hay observaciones finitas para ajustar las escalas")
    q1, q3 = valores.quantile([0.25, 0.75])
    mediana = float(valores.median())
    return {
        "n": int(len(valores)),
        "min": float(valores.min()),
        "max": float(valores.max()),
        "media": float(valores.mean()),
        "std_poblacional": float(valores.std(ddof=0)),
        "mediana": mediana,
        "mad": float((valores - mediana).abs().median()),
        "iqr_inferior": float(q1 - 1.5 * (q3 - q1)),
        "iqr_superior": float(q3 + 1.5 * (q3 - q1)),
        "q33": float(valores.quantile(1 / 3)),
        "q67": float(valores.quantile(2 / 3)),
    }


def escalar(serie: pd.Series, parametros: dict) -> tuple[pd.Series, pd.Series]:
    rango = parametros["max"] - parametros["min"]
    minimo_maximo = (serie - parametros["min"]) / rango if rango else serie * 0.0
    z = (
        (serie - parametros["media"]) / parametros["std_poblacional"]
        if parametros["std_poblacional"]
        else serie * 0.0
    )
    return minimo_maximo, z


def marcar_atipicos(datos: pd.DataFrame, corte: pd.Timestamp, por_variable=True):
    resultado = datos.copy()
    parametros = {}
    grupos = datos.groupby("variable", sort=True) if por_variable else [("fix", datos)]
    for variable, grupo in grupos:
        entrenamiento = grupo.loc[grupo.fecha.le(corte), "valor"]
        p = ajustar(entrenamiento)
        parametros[variable] = p
        valores = grupo.valor
        resultado.loc[grupo.index, "es_atipico_iqr"] = valores.lt(p["iqr_inferior"]) | valores.gt(
            p["iqr_superior"]
        )
        resultado.loc[grupo.index, "es_atipico_robusto"] = (
            (0.67448975 * (valores - p["mediana"]) / p["mad"]).abs().gt(3.5)
            if p["mad"]
            else valores.ne(p["mediana"])
        )
    return resultado, parametros


def preparar_caracteristicas(mensual: pd.DataFrame, corte: pd.Timestamp):
    resultado = mensual.copy()
    columnas = ["teu_total", "ton_contenerizada", "buques_contenerizada", "fix_promedio_mxn_usd"]
    parametros = {}
    for columna in columnas:
        p = ajustar(resultado.loc[resultado.fecha.le(corte), columna])
        parametros[columna] = p
        resultado[f"{columna}_minmax"], resultado[f"{columna}_zscore"] = escalar(
            resultado[columna], p
        )
    p = parametros["teu_total"]
    resultado["actividad"] = np.select(
        [resultado.teu_total.le(p["q33"]), resultado.teu_total.le(p["q67"])],
        ["baja", "media"],
        default="alta",
    )
    resultado["teu_media_movil_3"] = resultado.teu_total.rolling(3, min_periods=1).mean()
    resultado["teu_mediana_movil_3"] = resultado.teu_total.rolling(3, min_periods=1).median()
    resultado["anio"] = resultado.fecha.dt.year.astype("int64")
    resultado["trimestre"] = resultado.fecha.dt.quarter.astype("int64")
    resultado["mes"] = resultado.fecha.dt.month.astype("int64")
    resultado["pais"] = "México"
    resultado["estado"] = "Colima"
    resultado["puerto"] = "Manzanillo"
    resultado["particion"] = np.where(resultado.fecha.le(corte), "entrenamiento", "prueba")
    return resultado, parametros
