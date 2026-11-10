"""E1 reproducible y sin red. Uso: python -m src.limpieza [--raiz RUTA]."""

from __future__ import annotations

import argparse
import csv
import hashlib
import importlib.metadata
import json
import os
import tempfile
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd
import pandera.pandas as pa

from src.calidad import (
    CUARENTENA_COLUMNAS,
    TERMINALES,
    aplicar_puerta,
    esquema_asipona,
    esquema_banxico,
    serializar,
)
from src.preprocesamiento import imputar_causal, marcar_atipicos, preparar_caracteristicas

ASIPONA = "data/bronce/asipona/em_mensual.csv"
BANXICO = "data/bronce/banxico/tipo_cambio_fix.csv"
CAMPOS_ASIPONA = {
    "anio",
    "mes",
    "variable",
    "valor",
    "publicado",
    "mes_reporte",
    "acumulado_reportado",
    "suma_meses",
    "cuadra",
    "diferencia",
    "archivo_origen",
    "url_origen",
    "fecha_captura_utc",
}
CAMPOS_BANXICO = {"fecha", "serie", "valor", "valor_crudo", "url_origen", "fecha_captura_utc"}


def sha256(ruta: Path) -> str:
    return hashlib.sha256(ruta.read_bytes()).hexdigest()


def rechazar(fuente, identificador, motivo, original, etapa="preparacion") -> dict:
    return {
        "fuente": fuente,
        "etapa": etapa,
        "id_origen": identificador,
        "motivo": motivo,
        "registro_original_json": serializar(original),
        "registro_normalizado_json": "{}",
    }


def numero(valor) -> float:
    return float(pd.to_numeric(valor, errors="coerce")) if str(valor).strip() else np.nan


def normalizar(datos: pd.DataFrame, fuente: str):
    """Normaliza tipos explícitamente; no confunde texto corrupto con faltantes."""
    columnas = CAMPOS_ASIPONA if fuente == "asipona" else CAMPOS_BANXICO
    originales, filas, rechazos = {}, [], []
    estructura = set(datos.columns) != columnas
    acumulados_incoherentes = set()
    if fuente == "asipona" and not estructura:
        for _, grupo in datos.reset_index(drop=True).groupby(["anio", "variable"]):
            meses = pd.to_numeric(grupo.mes, errors="coerce")
            if len(grupo) == 12 and set(meses) == set(range(1, 13)):
                suma = pd.to_numeric(grupo.valor, errors="coerce").sum(min_count=1)
                reportadas = pd.to_numeric(grupo.suma_meses, errors="coerce")
                acumuladas = pd.to_numeric(grupo.acumulado_reportado, errors="coerce")
                diferencias = pd.to_numeric(grupo.diferencia, errors="coerce")
                consistente = (
                    np.isfinite(suma)
                    and reportadas.notna().all()
                    and acumuladas.notna().all()
                    and diferencias.notna().all()
                    and reportadas.eq(suma).all()
                    and np.isclose(suma - acumuladas, diferencias, rtol=0, atol=1e-8).all()
                )
                if not consistente:
                    acumulados_incoherentes.update(grupo.index + 2)
    for posicion, original in enumerate(datos.to_dict("records"), start=2):
        identificador = f"{fuente}:{posicion}"
        originales[identificador] = original
        r = {k: str(v).strip() for k, v in original.items()}
        motivos = []
        if estructura:
            motivos.append("esquema_bronce: columnas ausentes o inesperadas")
        if posicion in acumulados_incoherentes:
            motivos.append("conflicto_suma_mensual_y_metadatos_anuales")
        captura = pd.to_datetime(r.get("fecha_captura_utc"), errors="coerce", utc=True)
        if pd.isna(captura):
            motivos.append("fecha_captura_utc_invalida")
        valor = numero(r.get("valor", ""))
        if r.get("valor", "") and pd.isna(valor):
            motivos.append("valor_no_numerico")
        fila = {
            "id_origen": identificador,
            "valor": valor,
            "url_origen": r.get("url_origen", ""),
            "fecha_captura_utc": r.get("fecha_captura_utc", ""),
            "es_atipico_iqr": False,
            "es_atipico_robusto": False,
        }
        if fuente == "asipona":
            anio, mes, reporte = (numero(r.get(k, "")) for k in ["anio", "mes", "mes_reporte"])
            calendario_valido = all(np.isfinite(x) and x == int(x) for x in [anio, mes, reporte])
            calendario_valido = (
                calendario_valido and 2021 <= anio <= 2100 and 1 <= mes <= 12 and 1 <= reporte <= 12
            )
            fecha = (
                pd.Timestamp(year=int(anio), month=int(mes), day=1) if calendario_valido else pd.NaT
            )
            publicado = r.get("publicado", "").lower()
            if not calendario_valido:
                motivos.append("calendario_invalido")
            elif publicado not in {"true", "false"} or (publicado == "true") != (mes <= reporte):
                motivos.append("estado_publicacion_incoherente")
            elif publicado == "false":
                motivos.append("periodo_no_publicado")
            if not pd.isna(fecha) and not pd.isna(captura) and fecha > captura.tz_localize(None):
                motivos.append("periodo_posterior_a_captura")
            fila.update(
                fecha=fecha,
                variable=r.get("variable", ""),
                valor_original=valor,
                imputado=False,
                metodo_imputacion="observado",
                diferencia_acumulado=numero(r.get("diferencia", "")),
                archivo_origen=r.get("archivo_origen", ""),
            )
            # Anomalía localizada en el EM 2021: ausencias representadas como cero.
            if anio == 2021 and mes in (11, 12) and fila["variable"] in TERMINALES and valor == 0:
                fila["valor"] = np.nan
        else:
            fecha = pd.to_datetime(r.get("fecha"), format="%Y-%m-%d", errors="coerce")
            crudo = numero(r.get("valor_crudo", "").replace(",", ""))
            fila.update(fecha=fecha, serie=r.get("serie", ""), valor_crudo=r.get("valor_crudo", ""))
            if pd.isna(valor) or pd.isna(crudo):
                motivos.append("cotizacion_no_disponible")
            elif not np.isclose(valor, crudo, rtol=0, atol=1e-8):
                motivos.append("conflicto_valor_y_valor_crudo")
            if not pd.isna(fecha) and not pd.isna(captura) and fecha > captura.tz_localize(None):
                motivos.append("fecha_posterior_a_captura")
        if motivos:
            rechazos.append(rechazar(fuente, identificador, "; ".join(motivos), original))
        else:
            filas.append(fila)
    esquema = esquema_asipona() if fuente == "asipona" else esquema_banxico()
    normalizados = pd.DataFrame(filas, columns=list(esquema.columns))
    if not normalizados.empty:
        normalizados["fecha"] = pd.to_datetime(normalizados["fecha"]).astype("datetime64[ns]")
        for campo in ["valor", "valor_original", "diferencia_acumulado"]:
            if campo in normalizados:
                normalizados[campo] = normalizados[campo].astype(float)
        if fuente == "asipona":
            normalizados, rechazados_previos = aplicar_puerta(
                normalizados,
                esquema_asipona(permitir_faltantes=True),
                fuente,
                originales,
                "pre_imputacion",
            )
            rechazos.extend(rechazados_previos)
            normalizados = imputar_causal(normalizados)
        normalizados, rechazados_pandera = aplicar_puerta(normalizados, esquema, fuente, originales)
        rechazos.extend(rechazados_pandera)
    return normalizados.sort_values("fecha").reset_index(drop=True), originales, rechazos


def agregar_banxico(datos: pd.DataFrame) -> pd.DataFrame:
    grupos = datos.assign(fecha=datos.fecha.dt.to_period("M").dt.to_timestamp()).groupby("fecha")
    mensual = grupos.agg(
        fix_promedio_mxn_usd=("valor", "mean"),
        fix_minimo_mxn_usd=("valor", "min"),
        fix_maximo_mxn_usd=("valor", "max"),
        fix_dias_observados=("valor", "count"),
    ).reset_index()
    ultima = datos.groupby(datos.fecha.dt.to_period("M")).fecha.max()
    mensual["fix_ultima_fecha"] = (
        mensual.fecha.dt.to_period("M").map(ultima).astype("datetime64[ns]")
    )
    captura = pd.to_datetime(datos.fecha_captura_utc, utc=True).max().tz_localize(None).normalize()
    mensual["fix_mes_completo"] = mensual.fecha.add(pd.offsets.MonthEnd(0)).le(captura)
    return mensual


def esquema_oro(caracteristicas: bool = False) -> pa.DataFrameSchema:
    fechas = {"fecha", "fix_ultima_fecha"}
    enteros = {"anio", "trimestre", "mes", "fix_dias_observados"}
    textos = {"id_origen", "actividad", "pais", "estado", "puerto", "particion"}
    booleanos = {"fix_mes_completo", "es_atipico_teu"}
    nombres = [
        "fecha",
        "teu_total",
        "ton_contenerizada",
        "buques_contenerizada",
        "fix_promedio_mxn_usd",
        "fix_minimo_mxn_usd",
        "fix_maximo_mxn_usd",
        "fix_dias_observados",
        "fix_ultima_fecha",
        "fix_mes_completo",
        "id_origen",
        "es_atipico_teu",
    ]
    if caracteristicas:
        nombres += [
            f"{variable}_{metodo}"
            for variable in [
                "teu_total",
                "ton_contenerizada",
                "buques_contenerizada",
                "fix_promedio_mxn_usd",
            ]
            for metodo in ["minmax", "zscore"]
        ]
        nombres += [
            "actividad",
            "teu_media_movil_3",
            "teu_mediana_movil_3",
            "anio",
            "trimestre",
            "mes",
            "pais",
            "estado",
            "puerto",
            "particion",
        ]
    columnas = {}
    for columna in nombres:
        if columna in fechas:
            columnas[columna] = pa.Column("datetime64[ns]")
        elif columna in enteros:
            columnas[columna] = pa.Column(int, pa.Check.ge(1))
        elif columna in textos:
            columnas[columna] = pa.Column(str, pa.Check.str_length(min_value=1))
        elif columna in booleanos:
            columnas[columna] = pa.Column(bool)
        else:
            columnas[columna] = pa.Column(float, pa.Check(np.isfinite))
    columnas["teu_total"] = pa.Column(float, pa.Check.in_range(1, 2_000_000))
    columnas["ton_contenerizada"] = pa.Column(float, pa.Check.in_range(0, 30_000_000))
    columnas["buques_contenerizada"] = pa.Column(float, pa.Check.in_range(0, 5_000))
    columnas["fix_promedio_mxn_usd"] = pa.Column(float, pa.Check.in_range(0.01, 1000))
    columnas["fix_mes_completo"] = pa.Column(bool, pa.Check.eq(True))
    if caracteristicas:
        columnas["mes"] = pa.Column(int, pa.Check.in_range(1, 12))
        columnas["trimestre"] = pa.Column(int, pa.Check.in_range(1, 4))
    return pa.DataFrameSchema(
        columnas, strict=True, coerce=False, unique=["fecha"], name="oro_mensual_v1"
    )


def integrar(asipona: pd.DataFrame, banxico_mensual: pd.DataFrame, corte: pd.Timestamp):
    ancho = asipona.pivot(index="fecha", columns="variable", values="valor")
    seleccion = ["teu_total", "ton_contenerizada", "buques_contenerizada"]
    mensual = ancho.reindex(columns=seleccion).reset_index()
    mensual = mensual.merge(banxico_mensual, on="fecha", how="left", validate="one_to_one")
    mensual["id_origen"] = "mensual:" + mensual.fecha.dt.strftime("%Y-%m")
    banderas = asipona.loc[asipona.variable.eq("teu_total")].set_index("fecha")
    mensual["es_atipico_teu"] = (
        mensual.fecha.map(banderas.es_atipico_iqr | banderas.es_atipico_robusto)
        .fillna(False)
        .astype(bool)
    )
    # La ausencia de FIX provoca rechazo por fila antes de ajustar transformaciones.
    mensual["fix_dias_observados"] = mensual.fix_dias_observados.fillna(0).astype(int)
    mensual["fix_mes_completo"] = mensual.fix_mes_completo.fillna(False).astype(bool)
    originales = {r["id_origen"]: r for r in mensual.to_dict("records")}
    mensual, rechazos = aplicar_puerta(
        mensual, esquema_oro(), "integracion", originales, "puerta_oro"
    )
    if mensual.empty:
        return mensual, {}, rechazos
    mensual, parametros = preparar_caracteristicas(mensual.sort_values("fecha"), corte)
    esquema_oro(caracteristicas=True).validate(mensual, lazy=True)
    return mensual, parametros, rechazos


def guardar_csv(datos: pd.DataFrame, ruta: Path):
    ruta.parent.mkdir(parents=True, exist_ok=True)
    datos.to_csv(
        ruta,
        index=False,
        encoding="utf-8",
        lineterminator="\n",
        float_format="%.12g",
        date_format="%Y-%m-%d",
    )


def guardar_json(objeto: dict, ruta: Path):
    ruta.parent.mkdir(parents=True, exist_ok=True)
    ruta.write_text(
        json.dumps(objeto, ensure_ascii=False, indent=2, sort_keys=True, allow_nan=False) + "\n",
        encoding="utf-8",
    )


def cuarentena(raiz: Path, rechazos: list[dict], identificador: str):
    datos = pd.DataFrame(rechazos, columns=CUARENTENA_COLUMNAS)
    for fuente in ["asipona", "banxico", "integracion"]:
        guardar_csv(datos.loc[datos.fuente.eq(fuente)], raiz / f"data/cuarentena/e1/{fuente}.csv")
    historial = raiz / f"data/cuarentena/e1/historial/{identificador}.jsonl"
    historial.parent.mkdir(parents=True, exist_ok=True)
    historial.write_text("".join(serializar(r) + "\n" for r in rechazos), encoding="utf-8")


def ejecutar(raiz: Path) -> dict:
    raiz = raiz.resolve()
    inicio = datetime.now(timezone.utc)
    entradas = {p: sha256(raiz / p) if (raiz / p).is_file() else None for p in [ASIPONA, BANXICO]}
    codigo = {p.name: sha256(p) for p in Path(__file__).parent.glob("*.py")}
    versiones = {
        p: importlib.metadata.version(p) for p in ["pandas", "numpy", "pandera", "pyarrow"]
    }
    identificador = hashlib.sha256(
        serializar({"entradas": entradas, "codigo": codigo, "versiones": versiones}).encode()
    ).hexdigest()[:16]
    rechazos = []
    estado, error = "falla", ""
    resumen = {
        "ejecucion_id": identificador,
        "entradas_sha256": entradas,
        "codigo_sha256": codigo,
        "versiones": versiones,
    }
    try:
        fuentes = {}
        originales = {}
        for fuente, ruta in [("asipona", ASIPONA), ("banxico", BANXICO)]:
            crudos = pd.read_csv(
                raiz / ruta, dtype=str, keep_default_na=False, skip_blank_lines=False
            )
            limpios, originales[fuente], rechazados = normalizar(crudos, fuente)
            rechazos.extend(rechazados)
            fuentes[fuente] = limpios
            resumen[fuente] = {
                "entrada": len(crudos),
                "aceptados": len(limpios),
                "rechazados": len(rechazados),
                "imputados": int(limpios.imputado.sum()) if fuente == "asipona" else 0,
            }
            if len(crudos) != len(limpios) + len(rechazados):
                raise ValueError(f"{fuente}: no se conserva el balance de filas")
            if limpios.empty:
                raise ValueError(f"{fuente}: ninguna fila superó la puerta de calidad")
        fechas = fuentes["asipona"].loc[lambda d: d.variable.eq("teu_total"), "fecha"].sort_values()
        if len(fechas) < 36 or len(pd.date_range(fechas.min(), fechas.max(), freq="MS")) != len(
            fechas
        ):
            raise ValueError("La serie objetivo requiere al menos 36 meses consecutivos sin huecos")
        corte = fechas.iloc[-7]
        fuentes["asipona"], pa_asipona = marcar_atipicos(fuentes["asipona"], corte)
        corte_diario = corte + pd.offsets.MonthEnd(0)
        fuentes["banxico"], pa_banxico = marcar_atipicos(
            fuentes["banxico"], corte_diario, por_variable=False
        )
        esquema_asipona().validate(fuentes["asipona"], lazy=True)
        esquema_banxico().validate(fuentes["banxico"], lazy=True)
        mensual_fix = agregar_banxico(fuentes["banxico"])
        oro, parametros, rechazados = integrar(fuentes["asipona"], mensual_fix, corte)
        rechazos.extend(rechazados)
        if len(oro) < 36:
            raise ValueError("Menos de 36 meses superaron la integración de fuentes")
        if len(pd.date_range(oro.fecha.min(), oro.fecha.max(), freq="MS")) != len(oro):
            raise ValueError("La integración dejó huecos en la serie mensual; revisar cuarentena")
        terminales = fuentes["asipona"].loc[lambda d: d.variable.isin(TERMINALES)].copy()
        terminales = terminales.merge(
            oro[["fecha", "teu_total"]], on="fecha", validate="many_to_one"
        )
        terminales["terminal"] = terminales.variable.str.removeprefix("teu_").str.upper()
        terminales["participacion_pct"] = 100 * terminales.valor / terminales.teu_total
        if not terminales.participacion_pct.between(0, 100).all():
            raise ValueError("Participación por terminal fuera de 0 a 100%")
        resumen.update(
            {
                "estado": "ok",
                "corte_entrenamiento": corte.strftime("%Y-%m-%d"),
                "meses_oro": len(oro),
                "meses_entrenamiento": int(oro.particion.eq("entrenamiento").sum()),
                "meses_prueba": int(oro.particion.eq("prueba").sum()),
                "terminales_mes": len(terminales),
                "meses_banxico": len(mensual_fix),
                "reduccion_banxico_pct": round(
                    100 * (1 - len(mensual_fix) / len(fuentes["banxico"])), 4
                ),
                "meses_fix_sin_asipona": sorted(
                    set(mensual_fix.fecha.dt.strftime("%Y-%m"))
                    - set(oro.fecha.dt.strftime("%Y-%m"))
                ),
                "rechazos_por_motivo": dict(Counter(r["motivo"] for r in rechazos)),
                "atipicos": {
                    f: {k: int(d[k].sum()) for k in ["es_atipico_iqr", "es_atipico_robusto"]}
                    for f, d in fuentes.items()
                },
            }
        )
        temporal = raiz / "data/_tmp"
        temporal.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(dir=temporal, prefix="e1-") as carpeta:
            preparado = Path(carpeta)
            productos = {
                "data/plata/asipona_mensual.csv": fuentes["asipona"],
                "data/plata/banxico_diario.csv": fuentes["banxico"],
                "data/plata/banxico_mensual.csv": mensual_fix,
                "data/oro/mensual_integrado.csv": oro,
                "data/oro/terminales_mes.csv": terminales,
            }
            for ruta, datos in productos.items():
                guardar_csv(datos, preparado / ruta)
            parquet = preparado / "data/oro/mensual_integrado.parquet"
            oro.to_parquet(parquet, index=False)
            guardar_json(
                {
                    "ajuste_hasta": resumen["corte_entrenamiento"],
                    "oro": parametros,
                    "asipona": pa_asipona,
                    "banxico": pa_banxico,
                },
                preparado / "data/oro/parametros_transformacion.json",
            )
            if entradas != {p: sha256(raiz / p) for p in entradas}:
                raise ValueError(
                    "Bronce cambió durante el procesamiento; no se publican resultados"
                )
            for ruta in preparado.rglob("*"):
                if ruta.is_file():
                    destino = raiz / ruta.relative_to(preparado)
                    destino.parent.mkdir(parents=True, exist_ok=True)
                    os.replace(ruta, destino)
        estado = "ok"
        return resumen
    except Exception as exc:
        error = f"{type(exc).__name__}: {exc}"
        resumen.update(estado="falla", error=error)
        raise
    finally:
        cuarentena(raiz, rechazos, identificador)
        guardar_json(resumen, raiz / "calidad/e1/resumen.json")
        fin = datetime.now(timezone.utc)
        bitacora = raiz / "calidad/bitacora_pipeline.csv"
        bitacora.parent.mkdir(parents=True, exist_ok=True)
        existe = bitacora.exists()
        campos = [
            "ejecucion_id",
            "inicio_utc",
            "fin_utc",
            "duracion_s",
            "estado",
            "rechazados",
            "disparador",
            "error",
        ]
        with bitacora.open("a", newline="", encoding="utf-8") as archivo:
            escritor = csv.DictWriter(archivo, fieldnames=campos)
            if not existe:
                escritor.writeheader()
            escritor.writerow(
                dict(
                    zip(
                        campos,
                        [
                            identificador,
                            inicio.isoformat(),
                            fin.isoformat(),
                            round((fin - inicio).total_seconds(), 3),
                            estado,
                            len(rechazos),
                            os.environ.get("GITHUB_EVENT_NAME", "manual-local"),
                            error,
                        ],
                    )
                )
            )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--raiz", type=Path, default=Path(__file__).resolve().parents[1])
    argumentos = parser.parse_args()
    print(json.dumps(ejecutar(argumentos.raiz), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
