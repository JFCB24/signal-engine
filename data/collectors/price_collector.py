# data/collectors/price_collector.py

import yfinance as yf
import pandas as pd
import os
from config.settings import TICKER, LOOKBACK_YEARS

def descargar_precios():
    """
    Descarga datos históricos de precios y los guarda en un CSV.
    OHLCV = Open, High, Low, Close, Volume
    """

    print(f"Descargando datos de {TICKER}...")

    # Calcular fecha de inicio según los años configurados
    fecha_fin   = pd.Timestamp.today()
    fecha_inicio = fecha_fin - pd.DateOffset(years=LOOKBACK_YEARS)

    # Descargar datos con yfinance
    datos = yf.download(
        tickers   = TICKER,
        start     = fecha_inicio.strftime("%Y-%m-%d"),
        end       = fecha_fin.strftime("%Y-%m-%d"),
        interval  = "1d",       # datos diarios
        auto_adjust = True      # ajusta splits y dividendos automáticamente
    )

    # Verificar que se descargaron datos
    if datos.empty:
        print("Error: no se descargaron datos. Verifica el ticker.")
        return None

    # Limpiar nombres de columnas
    datos.columns = ["open", "high", "low", "close", "volume"]

    # Eliminar filas con valores vacíos
    datos.dropna(inplace=True)

    # Crear carpeta si no existe
    os.makedirs("data/raw", exist_ok=True)

    # Guardar en CSV
    ruta = f"data/raw/{TICKER.replace('-', '_')}_precios.csv"
    datos.to_csv(ruta)

    print(f"Datos guardados en: {ruta}")
    print(f"Total de filas: {len(datos)}")
    print(f"Desde: {datos.index[0].date()} hasta: {datos.index[-1].date()}")
    print(datos.tail(3))  # muestra las últimas 3 filas como verificación

    return datos


if __name__ == "__main__":
    descargar_precios()