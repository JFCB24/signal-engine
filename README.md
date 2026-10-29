# 📈 Signal Engine (LatixIA)

> Herramienta de análisis técnico educativo, con una prueba en vivo de un modelo de probabilidad para BTC-USD.

🔗 **[Aplicación en vivo](https://latixia.streamlit.app)**

> ⚠️ **No es una recomendación de compra ni de venta, ni asesoría financiera.** El modelo no ha demostrado una ventaja predictiva. Ver [Estado actual](#estado-actual).

---

## Qué hace

**1. Análisis técnico (dashboard)**
Para cualquier activo del catálogo muestra precio, tendencia, volatilidad, RSI, MACD, posición en Bandas de Bollinger y volumen relativo, cada uno con una explicación de qué significa. También muestra titulares recientes.

**2. Prueba en vivo de BTC-USD**
Cada día, un proceso automático:
1. descarga precios diarios,
2. recalcula los indicadores y reentrena el modelo,
3. registra la probabilidad de subida de mañana **antes** de conocer el resultado,
4. califica las señales que ya tienen día siguiente.

El registro está en `data/registro_senales.csv`. Es la única medición de rendimiento real del proyecto.

## Estado actual

| Pregunta | Respuesta honesta |
|---|---|
| ¿El modelo predice mejor que el azar? | **No se ha demostrado.** La accuracy fuera de muestra es 59.3% con 10 años de datos, pero una regla simple de reversión a la media acierta 52%, y una evaluación que empezaba en 2015 dio 52% para el modelo. El resultado depende del periodo que elijas. |
| ¿El backtest es un buen indicador de ganancias? | **No.** La corrida de 10 años reporta +5.999% de retorno, con 378 operaciones y un Sharpe de 3.9. Eso no es creíble como pronóstico. No lo uses para decidir. |
| ¿Qué se puede confiar? | Que los cálculos de los indicadores son correctos, que no hay fuga de datos del futuro en las features (tests), y que la prueba en vivo registra las señales antes del resultado. |
| ¿Qué falta? | Al menos 60 señales calificadas en vivo, y luego evaluar si la accuracy supera al baseline de forma estable. |

## Evaluación

`python -m models.evaluar` hace una evaluación walk-forward (5 bloques, ventana expansiva, 1 día de separación entre entrenamiento y prueba), compara contra «siempre sube» y corre un backtest long/flat con costos. El control de azar desplaza las probabilidades en el tiempo y compara con esa distribución. Los resultados se guardan en `reportes/walkforward.json`.

El backtest de `reportes/walkforward.json` no debe usarse para decidir nada: su retorno es demasiado alto para ser un pronóstico real. Sirve para verificar que el código de costos y posiciones funciona, no para medir ganancias.

## Instalación

```bash
git clone https://github.com/JFCB24/signal-engine.git
cd signal-engine

python -m venv venv
venv\Scripts\activate        # Windows
source venv/bin/activate     # Mac/Linux

pip install -r requirements.txt
```

No hace falta ninguna API key: los titulares vienen del RSS público de Yahoo Finance.

## Uso

Desde la raíz del proyecto:

```bash
python -m models.diario          # proceso diario completo (descarga, entrena, registra, califica)
python -m models.evaluar         # evaluación walk-forward y backtest
streamlit run dashboard/app.py   # dashboard
```

## Tests

```bash
python -m pytest
```

Los tests no usan red. Verifican que:
- las features no usen información futura (cambiar precios posteriores no altera features anteriores),
- la última fila conserve datos para la inferencia,
- el costo del backtest se cobre por cada cambio de posición,
- el registro no duplique señales y califique con el cierre siguiente.

`test_sistema.py` es una prueba de humo manual que usa la red para los titulares.

## Automatización

`.github/workflows/diario.yml` corre el proceso diario a las 00:30 UTC y guarda el registro en el repo. Se activa al subir el repo a GitHub.

## Estructura

```
├── config/settings.py              # Activos, umbrales y parámetros
├── data/
│   ├── collectors/                 # precios (yfinance) y titulares (RSS)
│   ├── processors/feature_engineering.py
│   └── registro_senales.csv        # prueba en vivo
├── models/
│   ├── train.py                    # modelo LightGBM
│   ├── predict.py                  # probabilidad del último día
│   ├── evaluar.py                  # walk-forward, baselines y backtest
│   ├── registro.py                 # registro y calificación
│   └── diario.py                   # proceso diario
├── backtesting/engine.py           # backtest long/flat con costos
├── dashboard/app.py                # interfaz Streamlit
├── reportes/walkforward.json       # última evaluación
├── tests/                          # pytest, sin red
└── .github/workflows/              # CI y proceso diario
```

## Limitaciones conocidas

- El modelo se entrena solo con BTC-USD. El dashboard no lo usa para otros activos.
- El catálogo tiene al menos un ticker que Yahoo ya no reconoce (`ENIA`).
- El sentimiento de titulares cuenta palabras positivas y negativas. No predice precios.
- La precisión del modelo se diagnosticó con `python -m models.diagnostico` (resultado en `reportes/diagnostico.txt`). No se encontró fuga de datos ni un error de código, pero tampoco se explica de dónde sale la ventaja.

## Licencia

MIT License — © 2026 JFCB24. Ver [LICENSE](LICENSE).

## Autor

**Juan Felipe Castellanos Bran** — [GitHub @JFCB24](https://github.com/JFCB24)

## Disclaimer

Herramienta educativa. Las probabilidades se basan en patrones históricos y no garantizan resultados futuros. No tomes decisiones financieras basadas solo en esta herramienta.
