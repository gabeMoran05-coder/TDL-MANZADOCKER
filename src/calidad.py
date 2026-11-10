"""Contratos Pandera y separación explícita de registros inválidos."""

from __future__ import annotations

import json
from collections import defaultdict

import numpy as np
import pandas as pd
import pandera.pandas as pa

VARIABLES = (
    "teu_total",
    "teu_ssa",
    "teu_contecon",
    "teu_ocupa",
    "teu_timsa",
    "teu_importacion",
    "teu_exportacion",
    "teu_transbordo_entrada",
    "teu_transbordo_salida",
    "ton_contenerizada",
    "buques_contenerizada",
)
TERMINALES = ("teu_ssa", "teu_contecon", "teu_ocupa", "teu_timsa")
MAXIMOS = {v: 2_000_000.0 for v in VARIABLES}
MAXIMOS.update(ton_contenerizada=30_000_000.0, buques_contenerizada=5_000.0)
CUARENTENA_COLUMNAS = [
    "fuente",
    "etapa",
    "id_origen",
    "motivo",
    "registro_original_json",
    "registro_normalizado_json",
]


def serializar(fila: dict) -> str:
    """JSON válido, incluso con NaT, NA, numpy y valores no finitos."""

    def limpio(valor):
        if isinstance(valor, dict):
            return {str(k): limpio(v) for k, v in valor.items()}
        if isinstance(valor, (list, tuple)):
            return [limpio(v) for v in valor]
        if valor is None or pd.isna(valor):
            return None
        if isinstance(valor, (pd.Timestamp, np.datetime64)):
            return pd.Timestamp(valor).isoformat()
        if isinstance(valor, np.generic):
            valor = valor.item()
        if isinstance(valor, float) and not np.isfinite(valor):
            return str(valor)
        return valor

    return json.dumps(limpio(fila), ensure_ascii=False, sort_keys=True, allow_nan=False)


def columnas_comunes() -> dict:
    return {
        "id_origen": pa.Column(str, pa.Check.str_length(min_value=1)),
        "fecha": pa.Column("datetime64[ns]"),
        "url_origen": pa.Column(str, pa.Check.str_matches(r"^https?://\S+$")),
        "fecha_captura_utc": pa.Column(
            str, pa.Check.str_matches(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$")
        ),
    }


def esquema_asipona(permitir_faltantes: bool = False) -> pa.DataFrameSchema:
    columnas = columnas_comunes()
    columnas.update(
        {
            "variable": pa.Column(str, pa.Check.isin(VARIABLES)),
            "valor": pa.Column(
                float, [pa.Check.ge(0), pa.Check(np.isfinite)], nullable=permitir_faltantes
            ),
            "valor_original": pa.Column(float, nullable=True),
            "imputado": pa.Column(bool),
            "metodo_imputacion": pa.Column(
                str, pa.Check.isin(["observado", "mediana_3_observados_previos"])
            ),
            "es_atipico_iqr": pa.Column(bool),
            "es_atipico_robusto": pa.Column(bool),
            "diferencia_acumulado": pa.Column(float, pa.Check.in_range(-2, 2)),
            "archivo_origen": pa.Column(str, pa.Check.str_matches(r"^data/bronce/.+\.pdf$")),
        }
    )
    return pa.DataFrameSchema(
        columnas,
        strict=True,
        coerce=False,
        unique=["fecha", "variable"],
        checks=[
            pa.Check(lambda d: d.fecha.dt.day.eq(1), name="primer_dia_del_mes"),
            pa.Check(
                lambda d: d.valor.isna() | d.valor.le(d.variable.map(MAXIMOS)),
                name="maximo_por_variable",
            ),
            pa.Check(
                lambda d: d.valor.isna() | ~d.variable.eq("teu_total") | d.valor.gt(0),
                name="teu_total_positivo",
            ),
            pa.Check(
                lambda d: d.imputado.eq(d.metodo_imputacion.ne("observado")),
                name="imputacion_trazable",
            ),
        ],
        name="asipona_plata_v1",
    )


def esquema_banxico() -> pa.DataFrameSchema:
    columnas = columnas_comunes()
    columnas.update(
        {
            "serie": pa.Column(str, pa.Check.eq("SF43718")),
            "valor": pa.Column(float, [pa.Check.in_range(0.01, 1000), pa.Check(np.isfinite)]),
            "valor_crudo": pa.Column(str, pa.Check.str_length(min_value=1)),
            "es_atipico_iqr": pa.Column(bool),
            "es_atipico_robusto": pa.Column(bool),
        }
    )
    return pa.DataFrameSchema(
        columnas,
        strict=True,
        coerce=False,
        unique=["fecha", "serie"],
        checks=[pa.Check(lambda d: d.fecha.eq(d.fecha.dt.normalize()), name="fecha_sin_hora")],
        name="banxico_plata_v1",
    )


def aplicar_puerta(
    datos: pd.DataFrame,
    esquema: pa.DataFrameSchema,
    fuente: str,
    originales: dict[str, dict],
    etapa: str = "puerta_plata",
) -> tuple[pd.DataFrame, list[dict]]:
    """Nunca usa drop_invalid_rows: cada rechazo conserva contenido y motivo.

    Un error estructural sin índice (columna ausente/extra o dtype incorrecto)
    rechaza todo el lote. Los errores por fila aíslan solo esas filas.
    """
    datos = datos.reset_index(drop=True)
    motivos: dict[int, set[str]] = defaultdict(set)
    try:
        esquema.validate(datos, lazy=True)
        return datos, []
    except pa.errors.SchemaErrors as error:
        for caso in error.failure_cases.to_dict("records"):
            motivo = f"{caso.get('column') or 'fila'}: {caso['check']}"
            indice = caso.get("index")
            indices = datos.index if pd.isna(indice) else [int(indice)]
            for i in indices:
                motivos[i].add(motivo)
    rechazos = []
    for indice in sorted(motivos):
        fila = datos.loc[indice].to_dict()
        identificador = str(fila.get("id_origen", f"{fuente}:{indice + 2}"))
        rechazos.append(
            {
                "fuente": fuente,
                "etapa": etapa,
                "id_origen": identificador,
                "motivo": "; ".join(sorted(motivos[indice])),
                "registro_original_json": serializar(originales.get(identificador, fila)),
                "registro_normalizado_json": serializar(fila),
            }
        )
    aceptados = datos.drop(index=list(motivos)).reset_index(drop=True)
    if not aceptados.empty:
        esquema.validate(aceptados, lazy=True)
    return aceptados, rechazos
