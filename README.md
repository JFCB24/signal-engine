# 📈 Signal Engine

> Plataforma de inteligencia artificial que analiza datos del mercado y noticias financieras para generar señales de inversión con probabilidad.

🔗 **[Ver aplicación en vivo](https://latixia.streamlit.app)**

---

## ¿Qué hace?

Signal Engine analiza más de 40 activos financieros en 7 mercados y genera señales como:

- **68% alcista** — con nivel de confianza y riesgo
- **Factores explicados** — RSI, MACD, Bollinger Bands, volumen
- **Sentimiento de noticias** — análisis con FinBERT (IA de lenguaje financiero)
- **Recomendación adaptada** — según tu perfil (conservador, moderado, agresivo)

> ⚠️ Herramienta educativa. No constituye asesoría financiera.

---

## Mercados disponibles

| Mercado | Activos |
|---|---|
| 🪙 Criptomonedas | Bitcoin, Ethereum, Solana, BNB, Cardano, XRP |
| 🇺🇸 Estados Unidos | Apple, Tesla, Microsoft, NVIDIA, Amazon, Google |
| 🇨🇴 Colombia | Bancolombia, Ecopetrol |
| 🇲🇽 México | America Movil, Cemex, Coca-Cola FEMSA |
| 🇧🇷 Brasil | Petrobras, Vale, MercadoLibre, Nubank |
| 🇦🇷 Argentina | YPF, Globant, Pampa Energia |
| 🌍 Materias primas | Oro, Plata, Petróleo, Cobre, Trigo |

---

## ¿Cómo funciona?
Datos históricos (yfinance)
↓
Indicadores técnicos (RSI, MACD, Bollinger, ATR, Volumen)
↓
Noticias financieras → FinBERT (análisis de sentimiento)
↓
Modelo LightGBM (entrenado con 3 años de datos)
↓
Señal: 68% alcista | Confianza: Media | Riesgo: Bajo
---

## Stack tecnológico

- **Python 3.14**
- **LightGBM** — modelo de machine learning
- **FinBERT** — modelo NLP para análisis de sentimiento financiero
- **yfinance** — datos históricos de mercado
- **Streamlit** — dashboard interactivo
- **pandas / numpy** — procesamiento de datos
- **ta** — indicadores técnicos

---

## Instalación local
```bash
# Clonar repositorio
git clone https://github.com/JFCB24/signal-engine.git
cd signal-engine

# Crear entorno virtual
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Mac/Linux

# Instalar dependencias
pip install -r requirements.txt

# Configurar API key (opcional)
cp .env.example .env
# Edita .env y agrega tu NEWSAPI_KEY

# Entrenar modelo
python -m data.collectors.price_collector
python -m data.processors.feature_engineering
python -m models.train

# Ejecutar dashboard
streamlit run dashboard/app.py
```

---
## Estructura del proyecto
├── config/
│   └── settings.py          # Configuración y catálogo de activos
├── data/
│   ├── collectors/
│   │   ├── price_collector.py   # Descarga datos de Yahoo Finance
│   │   └── news_collector.py    # Obtiene y analiza noticias con FinBERT
│   └── processors/
│       └── feature_engineering.py  # Calcula indicadores técnicos
├── models/
│   ├── train.py             # Entrena modelo LightGBM
│   └── predict.py           # Genera señal de inversión
├── dashboard/
│   └── app.py               # Interfaz visual en Streamlit
├── backtesting/
│   └── engine.py            # Evaluación histórica del modelo
├── test_sistema.py          # Test automático del sistema
└── requirements.txt
---

## Autor

**Juan Felipe Castellanos Bran**
Estudiante de Ingeniería de Datos — 17 años
🇨🇴 Colombia

[![GitHub](https://img.shields.io/badge/GitHub-JFCB24-black?logo=github)](https://github.com/JFCB24)

---

## Disclaimer

Este proyecto es una herramienta educativa. Las señales generadas se basan en patrones históricos y no garantizan resultados futuros. No tomes decisiones financieras basadas únicamente en esta herramienta. Siempre investiga por tu cuenta.
## Licencia

MIT License — © 2026 JFCB24

Este proyecto es de código abierto bajo los términos de la licencia MIT.