import pandas as pd
import numpy as np
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from config.settings import TICKER

def calcular_features(df):
    """
    Recibe el DataFrame de precios y agrega columnas
    con indicadores técnicos como nuevas features.
    """

    # --- RSI (Relative Strength Index) ---
    # Mide si el activo está sobrecomprado (>70) o sobrevendido (<30)
    delta = df["close"].diff()
    ganancia = delta.clip(lower=0)
    perdida = -delta.clip(upper=0)
    media_ganancia = ganancia.rolling(window=14).mean()
    media_perdida = perdida.rolling(window=14).mean()
    rs = media_ganancia / media_perdida
    df["rsi"] = 100 - (100 / (1 + rs))

    # --- MACD (Moving Average Convergence Divergence) ---
    # Detecta cambios de tendencia
    ema12 = df["close"].ewm(span=12, adjust=False).mean()
    ema26 = df["close"].ewm(span=26, adjust=False).mean()
    df["macd"] = ema12 - ema26
    df["macd_signal"] = df["macd"].ewm(span=9, adjust=False).mean()
    df["macd_hist"] = df["macd"] - df["macd_signal"]

    # --- Bollinger Bands ---
    # Mide si el precio está alto o bajo respecto a su promedio reciente
    media20 = df["close"].rolling(window=20).mean()
    std20 = df["close"].rolling(window=20).std()
    df["bb_upper"] = media20 + (2 * std20)
    df["bb_lower"] = media20 - (2 * std20)
    df["bb_position"] = (df["close"] - df["bb_lower"]) / (df["bb_upper"] - df["bb_lower"])

    # --- Volumen relativo ---
    # Compara el volumen de hoy vs el promedio de los últimos 20 días
    df["volume_ratio"] = df["volume"] / df["volume"].rolling(window=20).mean()

    # --- ATR (Average True Range) ---
    # Mide la volatilidad del activo
    high_low = df["high"] - df["low"]
    high_close = (df["high"] - df["close"].shift()).abs()
    low_close = (df["low"] - df["close"].shift()).abs()
    true_range = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
    df["atr"] = true_range.rolling(window=14).mean()

    # --- Label (lo que el modelo intenta predecir) ---
    # 1 = el precio subió al día siguiente, 0 = bajó
    df["label"] = (df["close"].shift(-1) > df["close"]).astype(int)

    # Eliminar filas con valores vacíos (primeras filas sin suficiente historial)
    df.dropna(inplace=True)

    return df


def procesar_datos():
    # Cargar CSV crudo
    ruta_raw = f"data/raw/{TICKER.replace('-', '_')}_precios.csv"

    if not os.path.exists(ruta_raw):
        print(f"Error: no existe {ruta_raw}")
        print("Primero ejecuta price_collector.py")
        return None

    print(f"Cargando datos de {ruta_raw}...")
    df = pd.read_csv(ruta_raw, index_col="Date", parse_dates=True)

    # Limpiar columnas multi-nivel que genera yfinance
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    df.columns = df.columns.str.lower().str.strip()

    print(f"Filas cargadas: {len(df)}")

    # Calcular features
    df = calcular_features(df)

    # Guardar CSV procesado
    os.makedirs("data/processed", exist_ok=True)
    ruta_out = f"data/processed/{TICKER.replace('-', '_')}_features.csv"
    df.to_csv(ruta_out)

    print(f"Features guardados en: {ruta_out}")
    print(f"Filas finales: {len(df)}")
    print(f"Columnas: {list(df.columns)}")
    print(df.tail(3))

    return df


if __name__ == "__main__":
    procesar_datos()