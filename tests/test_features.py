import numpy as np
import pandas as pd

from data.processors.feature_engineering import calcular_features


def _precios_sinteticos(n=400, semilla=0):
    rng = np.random.default_rng(semilla)
    cierre = 100 * np.exp(np.cumsum(rng.normal(0, 0.02, n)))
    fechas = pd.date_range("2022-01-01", periods=n, freq="D")
    return pd.DataFrame({
        "open": cierre * (1 + rng.normal(0, 0.005, n)),
        "high": cierre * (1 + np.abs(rng.normal(0, 0.01, n))),
        "low": cierre * (1 - np.abs(rng.normal(0, 0.01, n))),
        "close": cierre,
        "volume": rng.uniform(1e6, 5e6, n),
    }, index=fechas)


def test_features_no_usan_informacion_futura():
    """Cambiar precios posteriores a T no debe alterar ninguna feature en T o antes."""
    base = _precios_sinteticos()
    T = 300
    alterado = base.copy()
    alterado.iloc[T + 1:, :] = alterado.iloc[T + 1:, :] * 3.7

    f_base = calcular_features(base.copy())
    f_alt = calcular_features(alterado.copy())

    columnas = [c for c in f_base.columns if c != "label"]
    hasta_T = f_base.index <= base.index[T]
    antes = f_base.loc[hasta_T, columnas]
    despues = f_alt.loc[f_alt.index <= base.index[T], columnas]
    pd.testing.assert_frame_equal(antes, despues, check_like=False)


def test_label_ultima_fila_es_nan_y_no_se_descarta():
    df = calcular_features(_precios_sinteticos())
    assert pd.isna(df["label"].iloc[-1]), "la última fila no tiene día siguiente"
    assert df["label"].iloc[:-1].isin([0, 1]).all()


def test_ultima_fila_disponible_para_inferencia():
    datos = _precios_sinteticos()
    df = calcular_features(datos.copy())
    assert df.index[-1] == datos.index[-1]
    assert not df.drop(columns="label").iloc[-1].isna().any()
