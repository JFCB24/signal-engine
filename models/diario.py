"""
Proceso diario de la prueba en vivo.

Descarga precios, recalcula features, reentrena el modelo, registra la señal
de hoy y califica las señales anteriores que ya tienen día siguiente.

Uso (desde la raíz del proyecto):
    python -m models.diario
"""

import os
import sys

import pandas as pd

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from config.settings import TICKER
from data.collectors.price_collector import descargar_precios
from data.processors.feature_engineering import procesar_datos
from models.train import entrenar_modelo
from models.predict import generar_senal
from models.registro import calificar_registro


def precios_para_calificar(ticker=TICKER):
    """Cierres indexados por fecha en texto, como los guarda el registro."""
    ruta = f"data/processed/{ticker.replace('-', '_')}_features.csv"
    df = pd.read_csv(ruta, index_col="Date", parse_dates=True)
    cierres = df["close"].copy()
    cierres.index = cierres.index.strftime("%Y-%m-%d")
    return {ticker: cierres}


def ejecutar_diario():
    if descargar_precios() is None:
        print("No se pudieron descargar precios. Se cancela el proceso de hoy.")
        return 1

    procesar_datos()
    entrenar_modelo()
    generar_senal(registrar=True)

    resumen = calificar_registro(precios_para_calificar())
    print(f"\nPrueba en vivo: {resumen['calificadas']} señales calificadas, "
          f"{resumen['aciertos']} aciertos, "
          f"accuracy {resumen['accuracy'] if resumen['accuracy'] is not None else 'sin datos'}")
    return 0


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.exit(ejecutar_diario())
