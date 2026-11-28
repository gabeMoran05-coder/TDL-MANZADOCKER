"""MANOVA E3: ¿las cuatro terminales difieren en tamaño y perfil de tráfico?

Unidad: terminal-año (data/plata/terminal_trafico_anual.csv, 4 terminales x 7 años).
Respuestas:
  ln_total          ln(TEU total)                      tamaño
  lr_expo_impo      ln(exportación / importación)      perfil exportador
  lr_trans_impo     ln(transbordo / importación)       perfil de transbordo
Las participaciones suman 1, así que se usan razones logarítmicas (Aitchison) en lugar
de porcentajes. Cabotaje es 0 salvo 178 TEU de TIMSA en 2020 y se omite.
Modelo: respuestas ~ terminal + año (el año es bloque; absorbe que 2026 sea ene-oct).

Además de Wilks y Pillai con su F aproximada (statsmodels), se calcula una prueba de
permutación que permuta las etiquetas de terminal dentro de cada año; no depende de la
normalidad multivariada. Se revisan supuestos: Mardia sobre residuos, M de Box entre
terminales y ANOVA separados para contrastar.

Uso: python -m scripts.manova_e3   ->  calidad/e3/manova.json
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

RAIZ = Path(__file__).resolve().parents[1]
ENTRADA = RAIZ / "data/plata/terminal_trafico_anual.csv"
SALIDA = RAIZ / "calidad/e3/manova.json"
RESPUESTAS = ["ln_total", "lr_expo_impo", "lr_trans_impo"]
PERMUTACIONES = 9999
SEMILLA = 20261127


def preparar(datos: pd.DataFrame) -> pd.DataFrame:
    d = datos.copy()
    if (d[["teu_total", "teu_importacion", "teu_exportacion", "teu_transbordo"]] <= 0).any().any():
        raise ValueError("Hay TEU no positivos: la razón logarítmica no está definida")
    d["ln_total"] = np.log(d.teu_total)
    d["lr_expo_impo"] = np.log(d.teu_exportacion / d.teu_importacion)
    d["lr_trans_impo"] = np.log(d.teu_transbordo / d.teu_importacion)
    return d


def _diseno(d: pd.DataFrame, con_terminal: bool) -> np.ndarray:
    columnas = [np.ones(len(d))]
    columnas += [(d.anio == a).astype(float).to_numpy() for a in sorted(d.anio.unique())[1:]]
    if con_terminal:
        columnas += [(d.terminal == t).astype(float).to_numpy()
                     for t in sorted(d.terminal.unique())[1:]]
    return np.column_stack(columnas)


def _sscp_residual(x: np.ndarray, y: np.ndarray) -> np.ndarray:
    beta, *_ = np.linalg.lstsq(x, y, rcond=None)
    r = y - x @ beta
    return r.T @ r


def estadisticos(d: pd.DataFrame, terminal: pd.Series | None = None) -> dict:
    """Wilks y Pillai del efecto terminal ajustando por año (SSCP hipótesis vs. error)."""
    d = d if terminal is None else d.assign(terminal=terminal.to_numpy())
    y = d[RESPUESTAS].to_numpy(dtype=float)
    e = _sscp_residual(_diseno(d, True), y)
    h = _sscp_residual(_diseno(d, False), y) - e
    return {"wilks": float(np.linalg.det(e) / np.linalg.det(h + e)),
            "pillai": float(np.trace(h @ np.linalg.inv(h + e)))}


def permutacion(d: pd.DataFrame, n: int = PERMUTACIONES, semilla: int = SEMILLA) -> dict:
    """Permuta terminales dentro de cada año; p = (1 + #{Pillai* >= Pillai}) / (n + 1)."""
    rng = np.random.default_rng(semilla)
    observado = estadisticos(d)
    grupos = [np.flatnonzero(d.anio.to_numpy() == a) for a in sorted(d.anio.unique())]
    etiquetas = d.terminal.to_numpy()
    mayores_pillai = menores_wilks = 0
    for _ in range(n):
        nuevas = etiquetas.copy()
        for g in grupos:
            nuevas[g] = rng.permutation(etiquetas[g])
        s = estadisticos(d, pd.Series(nuevas))
        mayores_pillai += s["pillai"] >= observado["pillai"] - 1e-12
        menores_wilks += s["wilks"] <= observado["wilks"] + 1e-12
    return {"permutaciones": n, "semilla": semilla, "esquema": "terminales permutadas dentro de cada año",
            "p_pillai": (1 + mayores_pillai) / (n + 1), "p_wilks": (1 + menores_wilks) / (n + 1)}


def mardia(residuos: np.ndarray) -> dict:
    n, p = residuos.shape
    z = residuos - residuos.mean(axis=0)
    s = z.T @ z / n
    g = z @ np.linalg.inv(s) @ z.T
    b1, b2 = float(np.mean(g ** 3)), float(np.mean(np.diag(g) ** 2))
    chi, gl = n * b1 / 6, p * (p + 1) * (p + 2) / 6
    zk = (b2 - p * (p + 2)) / np.sqrt(8 * p * (p + 2) / n)
    return {"asimetria_b1": b1, "chi2": float(chi), "gl": gl, "p_asimetria": float(stats.chi2.sf(chi, gl)),
            "curtosis_b2": b2, "z": float(zk), "p_curtosis": float(2 * stats.norm.sf(abs(zk)))}


def box_m(residuos: np.ndarray, grupos: np.ndarray) -> dict:
    """M de Box sobre residuos del modelo con aproximación chi-cuadrada."""
    etiquetas = sorted(set(grupos))
    p, k = residuos.shape[1], len(etiquetas)
    covs, ns = [], []
    for g in etiquetas:
        r = residuos[grupos == g]
        covs.append(np.cov(r, rowvar=False, ddof=1))
        ns.append(len(r))
    ns = np.array(ns)
    combinada = sum((n - 1) * c for n, c in zip(ns, covs)) / (ns.sum() - k)
    m = (ns.sum() - k) * np.log(np.linalg.det(combinada)) - sum(
        (n - 1) * np.log(np.linalg.det(c)) for n, c in zip(ns, covs))
    c1 = (np.sum(1 / (ns - 1)) - 1 / (ns.sum() - k)) * (2 * p ** 2 + 3 * p - 1) / (6 * (p + 1) * (k - 1))
    chi, gl = m * (1 - c1), p * (p + 1) * (k - 1) / 2
    return {"M": float(m), "chi2": float(chi), "gl": gl, "p": float(stats.chi2.sf(chi, gl)),
            "n_por_grupo": dict(zip(etiquetas, ns.tolist()))}


def analizar(datos: pd.DataFrame, permutaciones: int = PERMUTACIONES) -> dict:
    from statsmodels.formula.api import ols
    from statsmodels.multivariate.manova import MANOVA
    from statsmodels.stats.anova import anova_lm

    d = preparar(datos)
    prueba = MANOVA.from_formula(" + ".join(RESPUESTAS) + " ~ C(terminal) + C(anio)", data=d).mv_test()
    tabla = prueba.results["C(terminal)"]["stat"]
    parametrica = {fila: {"valor": float(tabla.loc[fila, "Value"]), "F": float(tabla.loc[fila, "F Value"]),
                          "gl_num": float(tabla.loc[fila, "Num DF"]), "gl_den": float(tabla.loc[fila, "Den DF"]),
                          "p": float(tabla.loc[fila, "Pr > F"])}
                   for fila in ("Wilks' lambda", "Pillai's trace")}
    y = d[RESPUESTAS].to_numpy(dtype=float)
    x = _diseno(d, True)
    beta, *_ = np.linalg.lstsq(x, y, rcond=None)
    residuos = y - x @ beta
    anovas = {}
    for r in RESPUESTAS:
        a = anova_lm(ols(f"{r} ~ C(terminal) + C(anio)", data=d).fit(), typ=2)
        p = float(a.loc["C(terminal)", "PR(>F)"])
        anovas[r] = {"F": float(a.loc["C(terminal)", "F"]), "p": p,
                     "p_bonferroni": min(1.0, p * len(RESPUESTAS))}
    medias = (d.groupby("terminal")[["teu_importacion", "teu_exportacion", "teu_transbordo"]].sum()
              .pipe(lambda m: m.div(m.sum(axis=1), axis=0) * 100).round(1))
    return {
        "entrada": {"archivo": ENTRADA.relative_to(RAIZ).as_posix(),
                    "sha256": hashlib.sha256(ENTRADA.read_bytes()).hexdigest() if ENTRADA.exists() else None,
                    "observaciones": len(d), "terminales": sorted(d.terminal.unique().tolist()),
                    "anios": sorted(int(a) for a in d.anio.unique())},
        "modelo": "ln_total + lr_expo_impo + lr_trans_impo ~ C(terminal) + C(anio)",
        "manova_terminal": parametrica,
        "permutacion": permutacion(d, permutaciones),
        "supuestos": {"mardia_residuos": mardia(residuos),
                      "box_m_residuos": box_m(residuos, d.terminal.to_numpy()),
                      "independencia": ("Las mismas terminales se observan cada año; el bloque año "
                                        "absorbe choques comunes, pero puede quedar correlación "
                                        "serial dentro de cada terminal.")},
        "anova_separados": anovas,
        "perfil_promedio_pct": {t: fila.to_dict() for t, fila in medias.iterrows()},
    }


if __name__ == "__main__":
    resultado = analizar(pd.read_csv(ENTRADA))
    SALIDA.write_text(json.dumps(resultado, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({k: resultado[k] for k in ("manova_terminal", "permutacion", "anova_separados")},
                     indent=1, ensure_ascii=False))
    s = resultado["supuestos"]
    print("Mardia p asim/curt:", round(s["mardia_residuos"]["p_asimetria"], 4),
          round(s["mardia_residuos"]["p_curtosis"], 4), "| Box M p:", round(s["box_m_residuos"]["p"], 4))
    print(resultado["perfil_promedio_pct"])
