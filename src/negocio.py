"""Escenarios mensuales del transportista; no convierte TEU en viajes ni en ingresos."""

import math


def escenario(*, solicitados: int, capacidad: int, tarifa: float, costo_variable: float,
              horas_espera: float, costo_hora: float, costos_fijos: float,
              suscripcion: float) -> dict:
    valores = [solicitados, capacidad, tarifa, costo_variable, horas_espera,
               costo_hora, costos_fijos, suscripcion]
    if any(not math.isfinite(v) or v < 0 for v in valores):
        raise ValueError("Las entradas deben ser números finitos no negativos")
    if solicitados != int(solicitados) or capacidad != int(capacidad):
        raise ValueError("Servicios y capacidad deben ser cantidades enteras")
    servicios = min(solicitados, capacidad)
    espera_unitaria = horas_espera * costo_hora
    margen = tarifa - costo_variable - espera_unitaria
    return {
        "servicios_atendibles": servicios,
        "servicios_sin_capacidad": max(0, solicitados - capacidad),
        "ingresos_estimados": servicios * tarifa,
        "costo_esperas_estimado": servicios * espera_unitaria,
        "margen_contribucion_por_servicio": margen,
        "resultado_operativo_estimado": servicios * margen - costos_fijos - suscripcion,
    }
