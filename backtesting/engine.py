"""
Backtest simple de una estrategia long/flat sobre probabilidades fuera de muestra.

Reglas:
- La decisión del día t se toma con el cierre de t (usa solo información hasta t).
- Si p_alcista(t) >= umbral, la posición es 1 (comprado); si no, 0 (fuera del mercado).
- El retorno de la posición se gana entre el cierre de t y el cierre de t+1.
- Cada cambio de posición cuesta `costo` (comisión + slippage).
"""

import numpy as np
import pandas as pd


def _max_drawdown(curva):
    pico = curva.cummax()
    return float((curva / pico - 1).min())


def _metricas(retornos, posiciones=None, dias_anio=365):
    retornos = retornos.dropna()
    if len(retornos) == 0:
        return {}
    curva = (1 + retornos).cumprod()
    desv = retornos.std()
    metricas = {
        "dias": int(len(retornos)),
        "retorno_total": float(curva.iloc[-1] - 1),
        "retorno_anual": float(curva.iloc[-1] ** (dias_anio / len(retornos)) - 1),
        "sharpe": float(retornos.mean() / desv * np.sqrt(dias_anio)) if desv > 0 else 0.0,
        "max_drawdown": _max_drawdown(curva),
    }
    if posiciones is not None:
        cambios = posiciones.diff().abs().fillna(0)
        metricas["operaciones"] = int((cambios > 0).sum())
        metricas["dias_en_mercado"] = float(posiciones.mean())
    return metricas


def backtest(precio, p_alcista, umbral=0.60, costo=0.001, dias_anio=365):
    """
    precio:     Serie de cierres indexada por fecha.
    p_alcista:  Serie de probabilidades (fuera de muestra) alineada con precio.
    Devuelve dict con métricas de la estrategia y de comprar-y-mantener.
    """
    datos = pd.DataFrame({"precio": precio, "p": p_alcista}).dropna()
    # retorno que se gana desde t hasta t+1
    ret_siguiente = datos["precio"].shift(-1) / datos["precio"] - 1

    posicion = (datos["p"] >= umbral).astype(float)
    # costo en cada día en que cambia la posición, incluida la entrada inicial
    costos = posicion.diff().abs().fillna(posicion.iloc[0]) * costo
    ret_estrategia = (posicion * ret_siguiente - costos).iloc[:-1]
    ret_mantener = ret_siguiente.iloc[:-1]

    metricas_estrategia = _metricas(ret_estrategia, posicion.iloc[:-1], dias_anio)
    # operaciones = días con costo dentro de la ventana, para que coincida con lo cobrado
    metricas_estrategia["operaciones"] = int((costos.iloc[:-1] > 0).sum())

    return {
        "estrategia": metricas_estrategia,
        "comprar_y_mantener": _metricas(ret_mantener, None, dias_anio),
    }
