"""
Diagnóstico del modelo: pruebas para entender de dónde sale la precisión
fuera de muestra. No cambia nada; solo imprime resultados.

Uso (desde la raíz del proyecto):
    python -m models.diagnostico
"""

import os
import sys

import numpy as np
import pandas as pd

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from models.train import cargar_features, crear_modelo

GRUPO_VOLUMEN = ["volume_ratio", "obv", "obv_trend", "obv_ratio", "vwap",
                 "precio_vs_vwap", "volume_spike"]
GRUPO_TIEMPO_Y_MEDIAS = ["dia_semana", "mes", "trimestre", "es_lunes", "es_viernes",
                         "es_enero", "fin_de_mes", "tendencia", "cruce_ema",
                         "precio_vs_sma20", "precio_vs_sma50"]


def precision_oos(X, y, etiquetas_barajadas=False, semilla=7):
    """Precisión por bloque con la misma partición walk-forward que evaluar.py."""
    n = len(X)
    inicio = int(n * 0.5)
    tamano = (n - inicio) // 5
    precisiones = []
    rng = np.random.default_rng(semilla)
    for k in range(5):
        pi = inicio + k * tamano
        pf = n if k == 4 else pi + tamano
        y_train = y.iloc[:pi - 1].astype(int).values
        if etiquetas_barajadas:
            y_train = rng.permutation(y_train)
        modelo = crear_modelo()
        modelo.fit(X.iloc[:pi - 1], y_train)
        pred = (modelo.predict_proba(X.iloc[pi:pf])[:, 1] >= 0.5).astype(int)
        precisiones.append(float((pred == y.iloc[pi:pf].astype(int).values).mean()))
    return float(np.mean(precisiones)), [round(p, 3) for p in precisiones]


def tasa_subida_por_retorno_hoy(df, desde="2022-03-01"):
    """Probabilidad de subida al día siguiente según el retorno de hoy."""
    c = df["close"]
    d = pd.DataFrame({"r": c.pct_change(), "sube": (c.shift(-1) > c).astype(float)}).dropna()
    d = d[d.index >= desde]
    d["tramo"] = pd.cut(d["r"], [-1, -0.05, -0.02, 0, 0.02, 0.05, 1])
    return d.groupby("tramo", observed=True)["sube"].agg(["mean", "count"])


def main():
    df, features = cargar_features()
    y = df["label"]

    print("1. Precisión fuera de muestra con las 34 features")
    media, bloques = precision_oos(df[features], y)
    print(f"   media {media:.3f} · bloques {bloques}\n")

    print("2. Control: etiquetas barajadas (debe quedar cerca de 0.50)")
    media, bloques = precision_oos(df[features], y, etiquetas_barajadas=True)
    print(f"   media {media:.3f} · bloques {bloques}\n")

    print("3. Sin features de volumen")
    sin_volumen = [f for f in features if f not in GRUPO_VOLUMEN]
    media, bloques = precision_oos(df[sin_volumen], y)
    print(f"   media {media:.3f} · bloques {bloques}\n")

    print("4. Solo tiempo y medias (sin indicadores de precio)")
    solo_tiempo = [f for f in features if f in GRUPO_TIEMPO_Y_MEDIAS]
    media, bloques = precision_oos(df[solo_tiempo], y)
    print(f"   media {media:.3f} · bloques {bloques}\n")

    print("5. Probabilidad de subida al día siguiente según el retorno de hoy (desde 2022)")
    print(tasa_subida_por_retorno_hoy(df).round(3).to_string())


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    main()
