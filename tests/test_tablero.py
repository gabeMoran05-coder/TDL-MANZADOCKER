"""Prueba funcional del tablero y escenario sintético, sin enviar datos a servicios."""

import json
from pathlib import Path

from streamlit.testing.v1 import AppTest

RAIZ = Path(__file__).resolve().parents[1]


def test_tablero_con_entradas_propias_y_mapa():
    app = AppTest.from_file(str(RAIZ / "tablero/app.py"), default_timeout=30).run()
    assert not app.exception
    assert len(app.number_input) == 8
    entradas = {
        "Servicios solicitados en el mes": 100,
        "Capacidad mensual en servicios": 80,
        "Ingreso cobrado por servicio (MXN, sin IVA)": 1000.0,
        "Costo variable por servicio, sin esperas (MXN)": 600.0,
        "Horas de espera por servicio": 2.0,
        "Costo por hora de espera (MXN)": 100.0,
        "Costos fijos mensuales asignados (MXN)": 1000.0,
        "Costo mensual de la app a evaluar (MXN)": 500.0,
    }
    for campo in app.number_input:
        assert campo.value is None
        campo.set_value(entradas[campo.label])
    app.run()
    assert not app.exception
    metricas = {m.label: m.value for m in app.metric}
    assert metricas["Servicios atendibles"] == "80"
    assert metricas["Costo de esperas estimado"] == "$16,000.00"
    assert metricas["Resultado operativo estimado"] == "$14,500.00"
    assert any("id_denue" in d.value.columns for d in app.dataframe)
    # Las entradas del usuario no se deben guardar: solo este caso sintético de QA.
    evidencia = RAIZ / "calidad/e2/validacion_tablero.json"
    if evidencia.parent.exists():
        evidencia.write_text(json.dumps({
            "estado": "ok", "tipo": "prueba sintética automática, no datos de un cliente",
            "excepciones": 0, "entradas": entradas,
            "resultado_operativo_esperado": 14500, "resultado_observado": metricas,
        }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
