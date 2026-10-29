import numpy as np
import pandas as pd

from backtesting.engine import backtest

COSTO = 0.001


def _serie(n=50, semilla=1):
    rng = np.random.default_rng(semilla)
    precio = pd.Series(100 * np.cumprod(1 + rng.normal(0.001, 0.02, n)),
                       index=pd.date_range("2024-01-01", periods=n, freq="D"))
    return precio


def test_sin_senal_no_hay_retorno_ni_operaciones():
    precio = _serie()
    p = pd.Series(0.1, index=precio.index)  # siempre bajista -> fuera del mercado
    r = backtest(precio, p, umbral=0.6, costo=COSTO)["estrategia"]
    assert r["retorno_total"] == 0.0
    assert r["operaciones"] == 0
    assert r["dias_en_mercado"] == 0.0


def test_siempre_comprado_paga_costo_una_sola_vez():
    precio = _serie()
    p = pd.Series(0.9, index=precio.index)  # siempre alcista -> comprado todo el tiempo
    resultado = backtest(precio, p, umbral=0.6, costo=COSTO)
    ret = precio.shift(-1) / precio - 1
    ret = ret.iloc[:-1]
    esperado = (1 + ret.iloc[0] - COSTO) * np.prod(1 + ret.iloc[1:].values) - 1
    assert np.isclose(resultado["estrategia"]["retorno_total"], esperado)
    assert resultado["estrategia"]["operaciones"] == 1
    assert np.isclose(resultado["comprar_y_mantener"]["retorno_total"],
                      np.prod(1 + ret.values) - 1)


def test_cada_cambio_de_posicion_cuesta():
    precio = _serie(n=6)
    p = pd.Series([0.9, 0.1, 0.9, 0.1, 0.9, 0.1], index=precio.index)
    r = backtest(precio, p, umbral=0.6, costo=COSTO)["estrategia"]
    assert r["operaciones"] == 5
