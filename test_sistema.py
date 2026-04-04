# test_sistema.py
# Ejecuta: py test_sistema.py

import sys
import os

sys.path.append(os.path.dirname(__file__))

VERDE = "\033[92m"
ROJO  = "\033[91m"
RESET = "\033[0m"
BOLD  = "\033[1m"

def ok(msg):
    print(f"  {VERDE}✓{RESET} {msg}")

def error(msg):
    print(f"  {ROJO}✗{RESET} {msg}")
    sys.exit(1)

print(f"\n{BOLD}═══════════════════════════════════════")
print("   Signal Engine — Test automático")
print(f"═══════════════════════════════════════{RESET}\n")

# ── Test 1: Librerías ─────────────────────────────────────
print(f"{BOLD}1. Librerías instaladas{RESET}")
librerias = [
    "pandas", "yfinance", "lightgbm",
    "sklearn", "streamlit", "transformers"
]
for lib in librerias:
    try:
        __import__(lib)
        ok(lib)
    except ImportError:
        error(f"{lib} no está instalado — ejecuta: pip install {lib}")

# ── Test 2: Archivos del proyecto ─────────────────────────
print(f"\n{BOLD}2. Archivos del proyecto{RESET}")
archivos = [
    "config/settings.py",
    "data/collectors/price_collector.py",
    "data/collectors/news_collector.py",
    "data/processors/feature_engineering.py",
    "models/train.py",
    "models/predict.py",
    "dashboard/app.py",
]
for archivo in archivos:
    if os.path.exists(archivo):
        ok(archivo)
    else:
        error(f"No existe: {archivo}")

# ── Test 3: Datos descargados ─────────────────────────────
print(f"\n{BOLD}3. Datos históricos{RESET}")
from config.settings import TICKER
import pandas as pd

ruta_raw = f"data/raw/{TICKER.replace('-', '_')}_precios.csv"
ruta_proc = f"data/processed/{TICKER.replace('-', '_')}_features.csv"

if os.path.exists(ruta_raw):
    df = pd.read_csv(ruta_raw)
    ok(f"Datos crudos: {len(df)} filas")
else:
    error(f"No existe {ruta_raw} — ejecuta: py -m data.collectors.price_collector")

if os.path.exists(ruta_proc):
    df = pd.read_csv(ruta_proc)
    ok(f"Datos procesados: {len(df)} filas, {len(df.columns)} columnas")
else:
    error(f"No existe {ruta_proc} — ejecuta: py -m data.processors.feature_engineering")

# ── Test 4: Modelo entrenado ──────────────────────────────
print(f"\n{BOLD}4. Modelo entrenado{RESET}")
import pickle

ruta_modelo = "models/modelo_lgbm.pkl"
if os.path.exists(ruta_modelo):
    with open(ruta_modelo, "rb") as f:
        modelo = pickle.load(f)
    ok(f"Modelo cargado correctamente")
else:
    error("No existe el modelo — ejecuta: py -m models.train")

# ── Test 5: Predicción real ───────────────────────────────
print(f"\n{BOLD}5. Predicción de señal{RESET}")
from config.settings import FEATURES
from data.processors.feature_engineering import calcular_features

df = pd.read_csv(ruta_proc, index_col="Date", parse_dates=True)
features_disponibles = [f for f in FEATURES if f in df.columns]
ultima_fila = df[features_disponibles].iloc[-1:]
probabilidades = modelo.predict_proba(ultima_fila)[0]
prob_alcista = probabilidades[1]
prob_bajista = probabilidades[0]

if prob_alcista >= 0.58:   señal = "ALCISTA ▲"
elif prob_bajista >= 0.58: señal = "BAJISTA ▼"
else:                       señal = "NEUTRAL ◆"

ok(f"Señal generada: {señal}")
ok(f"Prob. alcista: {prob_alcista:.1%} | Prob. bajista: {prob_bajista:.1%}")

# ── Test 6: Sentimiento ───────────────────────────────────
print(f"\n{BOLD}6. Análisis de sentimiento{RESET}")
from data.collectors.news_collector import obtener_noticias, analizar_sentimiento

titulares = obtener_noticias(TICKER)
score, etiqueta = analizar_sentimiento(titulares)
ok(f"Noticias analizadas: {len(titulares)} titulares")
ok(f"Sentimiento: {etiqueta} (score: {score:+.3f})")

# ── Resumen ───────────────────────────────────────────────
print(f"\n{BOLD}═══════════════════════════════════════")
print(f"{VERDE}  Todo OK — el sistema está listo{RESET}{BOLD}")
print(f"  Ejecuta: streamlit run dashboard/app.py")
print(f"═══════════════════════════════════════{RESET}\n")