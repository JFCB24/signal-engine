import pandas as pd
import numpy as np
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from config.settings import TICKER

def calcular_features(df):
    """
    Calcula todos los indicadores técnicos avanzados.
    """

    # ── Indicadores básicos ──────────────────────────────────

    # RSI
    delta = df["close"].diff()
    ganancia = delta.clip(lower=0)
    perdida = -delta.clip(upper=0)
    media_ganancia = ganancia.rolling(window=14).mean()
    media_perdida = perdida.rolling(window=14).mean()
    rs = media_ganancia / media_perdida
    df["rsi"] = 100 - (100 / (1 + rs))

    # MACD
    ema12 = df["close"].ewm(span=12, adjust=False).mean()
    ema26 = df["close"].ewm(span=26, adjust=False).mean()
    df["macd"] = ema12 - ema26
    df["macd_signal"] = df["macd"].ewm(span=9, adjust=False).mean()
    df["macd_hist"] = df["macd"] - df["macd_signal"]

    # Bollinger Bands
    media20 = df["close"].rolling(window=20).mean()
    std20 = df["close"].rolling(window=20).std()
    df["bb_upper"] = media20 + (2 * std20)
    df["bb_lower"] = media20 - (2 * std20)
    df["bb_position"] = (df["close"] - df["bb_lower"]) / (df["bb_upper"] - df["bb_lower"])

    # Volumen relativo
    df["volume_ratio"] = df["volume"] / df["volume"].rolling(window=20).mean()

    # ATR
    high_low = df["high"] - df["low"]
    high_close = (df["high"] - df["close"].shift()).abs()
    low_close = (df["low"] - df["close"].shift()).abs()
    true_range = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
    df["atr"] = true_range.rolling(window=14).mean()

    # ── Tendencia ────────────────────────────────────────────

    # Medias móviles
    df["sma20"]  = df["close"].rolling(20).mean()
    df["sma50"]  = df["close"].rolling(50).mean()
    df["sma200"] = df["close"].rolling(200).mean()

    # Tendencia alcista si sma50 > sma200
    df["tendencia"] = (df["sma50"] > df["sma200"]).astype(int)

    # Precio relativo a medias
    df["precio_vs_sma20"]  = df["close"] / df["sma20"]
    df["precio_vs_sma50"]  = df["close"] / df["sma50"]

    # EMAs para cruce
    df["ema9"]  = df["close"].ewm(span=9, adjust=False).mean()
    df["ema21"] = df["close"].ewm(span=21, adjust=False).mean()
    df["cruce_ema"] = (df["ema9"] > df["ema21"]).astype(int)

    # Fuerza de tendencia
    df["tendencia_fuerza"] = df["close"].pct_change().rolling(14).std()

    # ── Volumen avanzado ─────────────────────────────────────

    # OBV — On Balance Volume
    obv = [0]
    for i in range(1, len(df)):
        if df["close"].iloc[i] > df["close"].iloc[i-1]:
            obv.append(obv[-1] + df["volume"].iloc[i])
        elif df["close"].iloc[i] < df["close"].iloc[i-1]:
            obv.append(obv[-1] - df["volume"].iloc[i])
        else:
            obv.append(obv[-1])
    df["obv"] = obv
    df["obv_trend"] = df["obv"].rolling(10).mean()
    df["obv_ratio"] = df["obv"] / df["obv_trend"]

    # VWAP
    df["vwap"] = (df["close"] * df["volume"]).cumsum() / df["volume"].cumsum()
    df["precio_vs_vwap"] = df["close"] / df["vwap"]

    # Volumen spike — volumen anormalmente alto
    df["volume_spike"] = (df["volume"] > df["volume"].rolling(20).mean() * 2).astype(int)

    # ── Temporalidad ─────────────────────────────────────────

    df["dia_semana"]  = df.index.dayofweek
    df["es_lunes"]    = (df["dia_semana"] == 0).astype(int)
    df["es_viernes"]  = (df["dia_semana"] == 4).astype(int)
    df["mes"]         = df.index.month
    df["es_enero"]    = (df["mes"] == 1).astype(int)
    df["fin_de_mes"]  = (df.index.day >= 25).astype(int)
    df["trimestre"]   = df.index.quarter

    # ── Especulación / Momentum ──────────────────────────────

    # ROC — Rate of Change
    df["roc5"]  = df["close"].pct_change(5)  * 100
    df["roc10"] = df["close"].pct_change(10) * 100
    df["roc20"] = df["close"].pct_change(20) * 100

    # Stochastic RSI
    rsi = df["rsi"]
    rsi_min = rsi.rolling(14).min()
    rsi_max = rsi.rolling(14).max()
    denom = (rsi_max - rsi_min)
    df["stoch_rsi"] = ((rsi - rsi_min) / denom.replace(0, np.nan)).fillna(0.5)

    # Williams %R
    high14 = df["high"].rolling(14).max()
    low14  = df["low"].rolling(14).min()
    denom_w = (high14 - low14)
    df["williams_r"] = ((high14 - df["close"]) / denom_w.replace(0, np.nan) * -100).fillna(-50)

    # ── Dirección / Soporte y Resistencia ────────────────────

    # Distancia a máximo y mínimo de 20 días
    df["dist_max_20"] = (df["high"].rolling(20).max() - df["close"]) / df["close"]
    df["dist_min_20"] = (df["close"] - df["low"].rolling(20).min()) / df["close"]

    # Distancia a máximo y mínimo de 52 semanas
    df["dist_max_52w"] = (df["high"].rolling(252).max() - df["close"]) / df["close"]
    df["dist_min_52w"] = (df["close"] - df["low"].rolling(252).min()) / df["close"]

    # Momentum de precio
    df["momentum_5"]  = df["close"] / df["close"].shift(5)  - 1
    df["momentum_10"] = df["close"] / df["close"].shift(10) - 1
    df["momentum_20"] = df["close"] / df["close"].shift(20) - 1

    # ── Label ────────────────────────────────────────────────
    df["label"] = (df["close"].shift(-1) > df["close"]).astype(int)

    # Eliminar filas con NaN
    df.dropna(inplace=True)

    return df


def procesar_datos():
    ruta_raw = f"data/raw/{TICKER.replace('-', '_')}_precios.csv"

    if not os.path.exists(ruta_raw):
        print(f"Error: no existe {ruta_raw}")
        print("Primero ejecuta price_collector.py")
        return None

    print(f"Cargando datos de {ruta_raw}...")
    df = pd.read_csv(ruta_raw, index_col="Date", parse_dates=True)

    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    df.columns = df.columns.str.lower().str.strip()

    print(f"Filas cargadas: {len(df)}")
    df = calcular_features(df)

    os.makedirs("data/processed", exist_ok=True)
    ruta_out = f"data/processed/{TICKER.replace('-', '_')}_features.csv"
    df.to_csv(ruta_out)

    print(f"Features guardados en: {ruta_out}")
    print(f"Filas finales: {len(df)}")
    print(f"Total features: {len(df.columns)}")

    return df


if __name__ == "__main__":
    procesar_datos()