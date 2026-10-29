"""
Registro de señales en vivo (prueba hacia adelante).

- registrar_senal(): guarda una señal por activo y fecha, ANTES de conocer el
  resultado. Si ya existe esa fecha para ese activo, no la sobrescribe.
- calificar_registro(): cuando ya hay cierre del día siguiente, marca si la
  señal acertó. NEUTRAL no cuenta como acierto ni fallo.
"""

import os

import pandas as pd

RUTA_REGISTRO = "data/registro_senales.csv"
COLUMNAS = ["fecha", "ticker", "precio", "senal", "prob_alcista",
            "prob_bajista", "confianza", "resultado", "acierto"]


TIPOS_TEXTO = {"fecha": str, "ticker": str, "senal": str, "confianza": str,
               "resultado": str, "acierto": str}


def _leer():
    if os.path.exists(RUTA_REGISTRO):
        return pd.read_csv(RUTA_REGISTRO, dtype=TIPOS_TEXTO, keep_default_na=True)
    return pd.DataFrame(columns=COLUMNAS).astype(object)


def registrar_senal(senal):
    """senal: dict con fecha, ticker, precio, senal, prob_alcista, prob_bajista, confianza."""
    registro = _leer()
    ya_existe = ((registro["fecha"] == senal["fecha"]) &
                 (registro["ticker"] == senal["ticker"])).any()
    if ya_existe:
        return False

    fila = {c: senal.get(c, "") for c in COLUMNAS}
    fila["resultado"] = ""
    fila["acierto"] = ""
    registro = pd.concat([registro, pd.DataFrame([fila])], ignore_index=True)
    os.makedirs(os.path.dirname(RUTA_REGISTRO), exist_ok=True)
    registro.to_csv(RUTA_REGISTRO, index=False)
    return True


def calificar_registro(precios_por_ticker):
    """
    precios_por_ticker: dict {ticker: Serie de cierres indexada por fecha (str YYYY-MM-DD)}.
    Califica las señales ALCISTA/BAJISTA cuyo día siguiente ya existe.
    Devuelve un resumen con el número de señales calificadas y aciertos.
    """
    registro = _leer()
    if registro.empty:
        return {"calificadas": 0, "aciertos": 0, "accuracy": None}

    for idx, fila in registro.iterrows():
        if fila["acierto"] in ("True", "False"):
            continue  # ya calificada
        serie = precios_por_ticker.get(fila["ticker"])
        if serie is None or fila["senal"] == "NEUTRAL":
            continue
        fechas = list(serie.index)
        if fila["fecha"] not in fechas:
            continue
        pos = fechas.index(fila["fecha"])
        if pos + 1 >= len(fechas):
            continue  # aún no hay día siguiente

        sube = serie.iloc[pos + 1] > serie.iloc[pos]
        acierto = (fila["senal"] == "ALCISTA" and sube) or \
                  (fila["senal"] == "BAJISTA" and not sube)
        registro.at[idx, "resultado"] = "SUBE" if sube else "BAJA"
        registro.at[idx, "acierto"] = str(bool(acierto))

    registro.to_csv(RUTA_REGISTRO, index=False)

    calificadas = registro[registro["acierto"].isin(["True", "False"])]
    total = len(calificadas)
    aciertos = int((calificadas["acierto"] == "True").sum())
    return {
        "calificadas": total,
        "aciertos": aciertos,
        "accuracy": round(aciertos / total, 4) if total else None,
    }
