import pandas as pd
import numpy as np
import lightgbm as lgb
import pickle
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from config.settings import TICKER, TRAIN_SPLIT, FEATURES

def entrenar_modelo():

    ruta = f"data/processed/{TICKER.replace('-', '_')}_features.csv"

    if not os.path.exists(ruta):
        print("Error: primero ejecuta feature_engineering.py")
        return None

    print("Cargando datos procesados...")
    df = pd.read_csv(ruta, index_col="Date", parse_dates=True)

    # Separar features y label
    features_disponibles = [f for f in FEATURES if f in df.columns]
    X = df[features_disponibles]
    y = df["label"]

    print(f"Features usados: {len(features_disponibles)}")

    # Walk-forward split
    corte = int(len(df) * TRAIN_SPLIT)
    X_train, X_test = X.iloc[:corte], X.iloc[corte:]
    y_train, y_test = y.iloc[:corte], y.iloc[corte:]

    print(f"Entrenamiento: {len(X_train)} filas")
    print(f"Prueba:        {len(X_test)} filas")

    # Baseline
    clase_mayoritaria = y_train.mode()[0]
    baseline_acc = (y_test == clase_mayoritaria).mean()
    print(f"\nBaseline (predecir siempre {clase_mayoritaria}): {baseline_acc:.1%}")

    # Entrenar LightGBM con regularización para reducir overfitting
    print("\nEntrenando modelo LightGBM...")
    modelo = lgb.LGBMClassifier(
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
    modelo.fit(X_train, y_train)

    # Evaluar
    acc_train = modelo.score(X_train, y_train)
    acc_test  = modelo.score(X_test, y_test)

    print(f"\nResultados:")
    print(f"  Accuracy entrenamiento : {acc_train:.1%}")
    print(f"  Accuracy prueba        : {acc_test:.1%}")
    print(f"  Baseline               : {baseline_acc:.1%}")

    if acc_test > baseline_acc:
        print(f"\n  El modelo SUPERA el baseline por {acc_test - baseline_acc:.1%}")
    else:
        print(f"\n  El modelo NO supera el baseline — revisar features")

    # Importancia de features
    print("\nImportancia de cada feature:")
    importancias = pd.Series(
        modelo.feature_importances_,
        index=features_disponibles
    ).sort_values(ascending=False)

    for feature, valor in importancias.items():
        if valor > 0:
            barra = "█" * int(valor / importancias.max() * 20)
            print(f"  {feature:<20} {barra} {valor}")

    # Guardar modelo
    os.makedirs("models", exist_ok=True)
    ruta_modelo = "models/modelo_lgbm.pkl"
    with open(ruta_modelo, "wb") as f:
        pickle.dump(modelo, f)

    print(f"\nModelo guardado en: {ruta_modelo}")
    return modelo, features_disponibles


if __name__ == "__main__":
    entrenar_modelo()