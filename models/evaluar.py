"""
Evaluación honesta: walk-forward con ventana expansiva.

Para cada bloque de prueba, el modelo se entrena solo con datos anteriores
(dejando 1 día de separación para que la etiqueta no toque el bloque).
Luego se compara contra baselines y se corre un backtest sobre las
predicciones fuera de muestra.

Uso (desde la raíz del proyecto):
    python -m models.evaluar
"""

import json
import os
import sys

import numpy as np
import pandas as pd

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from config.settings import TICKER, UMBRAL_SENAL, COSTO_OPERACION
from backtesting.engine import backtest
from models.train import cargar_features, crear_modelo

FRACCION_INICIAL = 0.50   # primera mitad solo para entrenar
N_BLOQUES = 5             # bloques de prueba consecutivos
RUTA_REPORTE = "reportes/walkforward.json"


def control_azar(precio, p_serie, repeticiones=500, semilla=42):
    """
    Desplaza circularmente las probabilidades una cantidad aleatoria de días.
    Así se conserva la distribución y las rachas de señal (y por tanto el
    número de operaciones y costos), pero se rompe la alineación con el precio.
    Si la estrategia real no supera a la mayoría de los desplazados, su
    resultado se explica por la exposición y no por la señal.
    """
    real = backtest(precio, p_serie, umbral=UMBRAL_SENAL,
                    costo=COSTO_OPERACION)["estrategia"]["retorno_total"]
    rng = np.random.default_rng(semilla)
    valores = p_serie.values
    n = len(valores)
    simulados = []
    for _ in range(repeticiones):
        desplazamiento = int(rng.integers(30, n - 30))
        p_desplazado = pd.Series(np.roll(valores, desplazamiento), index=p_serie.index)
        simulados.append(backtest(precio, p_desplazado, umbral=UMBRAL_SENAL,
                                  costo=COSTO_OPERACION)["estrategia"]["retorno_total"])
    simulados = np.array(simulados)
    return {
        "repeticiones": repeticiones,
        "retorno_real": float(real),
        "retorno_azar_mediana": float(np.median(simulados)),
        "retorno_azar_p95": float(np.percentile(simulados, 95)),
        "p_valor": float((simulados >= real).mean()),
    }


def evaluar_walkforward(ticker=TICKER):
    df, features = cargar_features(ticker)
    n = len(df)
    inicio = int(n * FRACCION_INICIAL)
    tamano_bloque = (n - inicio) // N_BLOQUES

    bloques = []
    predicciones = []

    for k in range(N_BLOQUES):
        prueba_ini = inicio + k * tamano_bloque
        prueba_fin = n if k == N_BLOQUES - 1 else prueba_ini + tamano_bloque
        # 1 día de separación: la etiqueta de train_fin usa el cierre de prueba_ini
        train_fin = prueba_ini - 1

        X_train = df[features].iloc[:train_fin]
        y_train = df["label"].iloc[:train_fin].astype(int)
        X_test = df[features].iloc[prueba_ini:prueba_fin]
        y_test = df["label"].iloc[prueba_ini:prueba_fin].astype(int)

        modelo = crear_modelo()
        modelo.fit(X_train, y_train)
        p_alcista = modelo.predict_proba(X_test)[:, 1]
        predicciones.append(p_alcista)

        acc_modelo = float(((p_alcista >= 0.5).astype(int) == y_test.values).mean())
        acc_siempre_sube = float((y_test == 1).mean())
        acc_mayoria_train = float((y_test == y_train.mode()[0]).mean())

        bloques.append({
            "bloque": k + 1,
            "desde": str(X_test.index[0].date()),
            "hasta": str(X_test.index[-1].date()),
            "filas_prueba": int(len(y_test)),
            "accuracy_modelo": round(acc_modelo, 4),
            "baseline_siempre_sube": round(acc_siempre_sube, 4),
            "baseline_mayoria_train": round(acc_mayoria_train, 4),
        })

    # Predicciones fuera de muestra concatenadas para el backtest
    p_oos = np.concatenate(predicciones)
    indices_oos = df.index[inicio:][: len(p_oos)]
    p_serie = pd.Series(p_oos, index=indices_oos)
    precio = df["close"]

    resultados_bt = backtest(precio, p_serie, umbral=UMBRAL_SENAL,
                             costo=COSTO_OPERACION)
    resultados_bt["control_azar"] = control_azar(precio, p_serie)

    accs = [b["accuracy_modelo"] for b in bloques]
    base = [b["baseline_siempre_sube"] for b in bloques]
    resumen = {
        "ticker": ticker,
        "bloques": N_BLOQUES,
        "accuracy_modelo_media": round(float(np.mean(accs)), 4),
        "accuracy_modelo_desv": round(float(np.std(accs)), 4),
        "baseline_siempre_sube_media": round(float(np.mean(base)), 4),
        "umbral_senal": UMBRAL_SENAL,
        "costo_operacion": COSTO_OPERACION,
    }
    reporte = {"resumen": resumen, "bloques": bloques, "backtest": resultados_bt}

    os.makedirs(os.path.dirname(RUTA_REPORTE), exist_ok=True)
    with open(RUTA_REPORTE, "w", encoding="utf-8") as f:
        json.dump(reporte, f, indent=2, ensure_ascii=False)
    return reporte


def _imprimir(reporte):
    r = reporte["resumen"]
    print(f"Walk-forward {r['ticker']} — {r['bloques']} bloques")
    print(f"{'bloque':>6} {'desde':>11} {'hasta':>11} {'modelo':>8} {'siempre sube':>13}")
    for b in reporte["bloques"]:
        print(f"{b['bloque']:>6} {b['desde']:>11} {b['hasta']:>11} "
              f"{b['accuracy_modelo']:>8.1%} {b['baseline_siempre_sube']:>13.1%}")
    print(f"\nAccuracy modelo: {r['accuracy_modelo_media']:.1%} "
          f"± {r['accuracy_modelo_desv']:.1%}")
    print(f"Baseline siempre sube: {r['baseline_siempre_sube_media']:.1%}")

    print(f"\nBacktest fuera de muestra (umbral {r['umbral_senal']:.0%}, "
          f"costo {r['costo_operacion']:.2%} por cambio):")
    for nombre in ("estrategia", "comprar_y_mantener"):
        m = reporte["backtest"][nombre]
        print(f"  {nombre:<20} retorno total {m['retorno_total']:>8.1%}  "
              f"Sharpe {m['sharpe']:>5.2f}  max DD {m['max_drawdown']:>7.1%}")
    e = reporte["backtest"]["estrategia"]
    print(f"  estrategia: {e['operaciones']} operaciones, "
          f"{e['dias_en_mercado']:.0%} de los días en mercado")
    c = reporte["backtest"]["control_azar"]
    print(f"\nControl de azar ({c['repeticiones']} desplazamientos, misma exposición):")
    print(f"  real {c['retorno_real']:.1%} | mediana azar {c['retorno_azar_mediana']:.1%} "
          f"| p95 azar {c['retorno_azar_p95']:.1%} | p-valor {c['p_valor']:.3f}")
    print(f"\nReporte guardado en {RUTA_REPORTE}")


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    _imprimir(evaluar_walkforward())
