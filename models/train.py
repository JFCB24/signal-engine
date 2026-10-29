import pandas as pd
import lightgbm as lgb
import pickle
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from config.settings import TICKER, FEATURES

RUTA_MODELO = "models/modelo_lgbm.pkl"


def crear_modelo():
    """Hiperparámetros compartidos por entrenamiento y evaluación."""
    return lgb.LGBMClassifier(
        n_estimators=300,
        learning_rate=0.02,
        max_depth=3,
        min_child_samples=40,
        num_leaves=15,
        subsample=0.8,
        colsample_bytree=0.7,
        reg_alpha=0.1,
        reg_lambda=0.1,
        random_state=42,
        verbose=-1
    )


def cargar_features(ticker=TICKER):
    """Lee el CSV procesado y devuelve (df, features) sin filas sin etiqueta."""
    ruta = f"data/processed/{ticker.replace('-', '_')}_features.csv"
    if not os.path.exists(ruta):
        raise FileNotFoundError(f"No existe {ruta}. Ejecuta feature_engineering.py")

    df = pd.read_csv(ruta, index_col="Date", parse_dates=True)
    # La última fila no tiene día siguiente y su label es NaN: no se entrena con ella
    df = df.dropna(subset=["label"])
    features_disponibles = [f for f in FEATURES if f in df.columns]
    return df, features_disponibles


def entrenar_modelo():
    df, features = cargar_features()
    print(f"Filas con etiqueta: {len(df)} | Features usados: {len(features)}")

    # Modelo de producción: todos los datos etiquetados.
    # La precisión honesta se mide en models/evaluar.py (walk-forward).
    modelo = crear_modelo()
    modelo.fit(df[features], df["label"].astype(int))

    os.makedirs("models", exist_ok=True)
    with open(RUTA_MODELO, "wb") as f:
        pickle.dump(modelo, f)

    print(f"Modelo guardado en: {RUTA_MODELO}")
    return modelo, features


if __name__ == "__main__":
    entrenar_modelo()
