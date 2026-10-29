# 📈 Signal Engine

> Herramienta que combina indicadores técnicos, un modelo LightGBM y el sentimiento de titulares para estimar la probabilidad de que un activo suba al día siguiente.

🔗 **[Ver aplicación en vivo](https://latixia.streamlit.app)**

> ⚠️ **Herramienta educativa. No es asesoría financiera.** Las probabilidades salen de patrones históricos y no garantizan resultados. Ver la sección de [Evaluación](#evaluación-honesta) antes de usarla para decidir algo.

---

## ¿Qué hace?

- **Probabilidad alcista/bajista** del día siguiente, con nivel de confianza.
- **Indicadores técnicos** calculados sobre precios diarios: RSI, MACD, Bandas de Bollinger, ATR, volumen, medias móviles, OBV, VWAP y más (34 features usados por el modelo).
- **Sentimiento de titulares** (RSS de Yahoo Finance) con un léxico de palabras positivas y negativas. No usa modelos de lenguaje.
- **Registro diario de señales** para llevar una prueba hacia adelante (ver abajo).

## Catálogo de activos

El catálogo (`config/settings.py`) tiene 66 activos en 9 categorías: criptomonedas, acciones de EE. UU., Colombia, México, Brasil, Argentina, China, materias primas y otros. El dashboard solo permite elegir los que Yahoo Finance devuelve con datos suficientes.

> **Limitación actual:** el modelo se entrena con **BTC-USD** y ese mismo modelo se aplica a todos los activos del dashboard. Para otros activos la probabilidad no está validada.

---

## Instalación

```bash
# Clonar y entrar
git clone https://github.com/JFCB24/signal-engine.git
cd signal-engine

# Entorno virtual
python -m venv venv
venv\Scripts\activate        # Windows
source venv/bin/activate     # Mac/Linux

pip install -r requirements.txt
```

No hace falta ninguna API key: los titulares se leen del RSS público de Yahoo Finance.

## Uso

Desde la raíz del proyecto, en este orden:

```bash
python -m data.collectors.price_collector        # descarga precios diarios
python -m data.processors.feature_engineering    # calcula features
python -m models.train                           # entrena el modelo de producción
python -m models.predict                         # señal de hoy (y la registra)
python -m models.evaluar                         # evaluación walk-forward + backtest
streamlit run dashboard/app.py                   # dashboard
```

## Evaluación honesta

`python -m models.evaluar` hace lo siguiente:

1. **Walk-forward con ventana expansiva:** 5 bloques de prueba consecutivos. Cada bloque se predice con un modelo entrenado solo con datos anteriores, dejando un día de separación.
2. **Baselines:** "siempre sube" y la clase mayoritaria del entrenamiento.
3. **Backtest long/flat** sobre las predicciones fuera de muestra: compra cuando la probabilidad alcista supera el umbral, con costo por cada cambio de posición.
4. **Control de azar:** desplaza las probabilidades aleatoriamente (conserva la exposición y las rachas de señal, rompe la alineación con el precio) y compara el retorno real con esa distribución.

Los resultados se guardan en `reportes/walkforward.json`. Los números que muestra el reporte son la referencia; no hay cifras fijas en este README.

> El backtest cubre una sola ventana de tiempo. Un buen resultado ahí no garantiza nada hacia adelante.

## Registro de señales en vivo

`models/predict.py` guarda cada señal en `data/registro_senales.csv`, una por activo y fecha, **antes** de conocer el resultado. `models/registro.py` puede calificarlas con el cierre del día siguiente. A diferencia de un backtest, este registro no se puede rehacer después.

## Tests

```bash
python -m pytest
```

Los tests de `tests/` no usan red. Verifican que:

- las features no usen información futura (cambiar precios posteriores no altera features anteriores),
- la última fila conserve datos para la inferencia,
- el costo del backtest se cobre por cada cambio de posición,
- el registro no duplique señales y califique con el cierre siguiente.

`test_sistema.py` es una prueba de humo manual: comprueba archivos, datos, modelo y una predicción real, y usa la red para los titulares.

---

## Estructura del proyecto

```
├── config/
│   └── settings.py                 # Activos, umbrales y parámetros
├── data/
│   ├── collectors/
│   │   ├── price_collector.py      # Precios diarios (yfinance)
│   │   └── news_collector.py       # Titulares (RSS) y sentimiento por léxico
│   └── processors/
│       └── feature_engineering.py  # Indicadores técnicos y etiqueta
├── models/
│   ├── train.py                    # Modelo LightGBM de producción
│   ├── predict.py                  # Señal del último día
│   ├── evaluar.py                  # Walk-forward, baselines y backtest
│   └── registro.py                 # Registro y calificación de señales
├── backtesting/
│   └── engine.py                   # Backtest long/flat con costos
├── dashboard/
│   └── app.py                      # Interfaz Streamlit
├── tests/                          # pytest, sin red
└── test_sistema.py                 # Prueba de humo manual
```

## Licencia

MIT License — © 2026 JFCB24. Ver [LICENSE](LICENSE).

## Autor

**Juan Felipe Castellanos Bran** — [GitHub @JFCB24](https://github.com/JFCB24)

## Disclaimer

Este proyecto es una herramienta educativa. Las señales se basan en patrones históricos y no garantizan resultados futuros. No tomes decisiones financieras basadas únicamente en esta herramienta.
