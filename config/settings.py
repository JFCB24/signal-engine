# config/settings.py

TICKER = "BTC-USD"
LOOKBACK_YEARS = 3
TRAIN_SPLIT = 0.80
HORIZON_HOURS = 24

FEATURES = [
    "rsi",
    "macd",
    "macd_signal",
    "bb_upper",
    "bb_lower",
    "bb_position",
    "volume_ratio",
    "atr",
]

ACTIVOS = {

    "🪙 Criptomonedas": {
        "Bitcoin":          "BTC-USD",
        "Ethereum":         "ETH-USD",
        "Solana":           "SOL-USD",
        "BNB":              "BNB-USD",
        "Cardano":          "ADA-USD",
        "XRP":              "XRP-USD",
        "Avalanche":        "AVAX-USD",
        "Polkadot":         "DOT-USD",
    },

    "🇺🇸 Estados Unidos": {
        # Tecnología
        "Apple":            "AAPL",
        "Microsoft":        "MSFT",
        "Google":           "GOOGL",
        "Amazon":           "AMZN",
        "Meta":             "META",
        "Tesla":            "TSLA",
        "NVIDIA":           "NVDA",
        # Finanzas
        "JPMorgan":         "JPM",
        "Goldman Sachs":    "GS",
        "Berkshire":        "BRK-B",
        # Energia
        "ExxonMobil":       "XOM",
        "Chevron":          "CVX",
        # ETFs índices
        "S&P 500 ETF":      "SPY",
        "Nasdaq ETF":       "QQQ",
        "Dow Jones ETF":    "DIA",
    },

    "🇨🇴 Colombia": {
        # ADR en NYSE — datos confiables en Yahoo Finance
        "Bancolombia":      "CIB",
        "Ecopetrol":        "EC",
        # ETF Colombia
        "ETF Colombia":     "GXG",
    },

    "🇲🇽 México": {
        # ADR en NYSE
        "America Movil":    "AMX",
        "Cemex":            "CX",
        "Coca-Cola FEMSA":  "KOF",
        "Grupo Televisa":   "TV",
        "Grupo TMM":        "GTMAY",
        # ETF México
        "ETF México":       "EWW",
    },

    "🇧🇷 Brasil": {
        # ADR en NYSE
        "Petrobras":        "PBR",
        "Vale":             "VALE",
        "Itau Unibanco":    "ITUB",
        "Bradesco":         "BBD",
        "Embraer":          "ERJ",
        "Nubank":           "NU",
        "MercadoLibre":     "MELI",
        # ETF Brasil
        "ETF Brasil":       "EWZ",
    },

    "🇦🇷 Argentina": {
        # ADR en NYSE
        "MercadoLibre":     "MELI",
        "Globant":          "GLOB",
        "Loma Negra":       "LOMA",
        "Pampa Energia":    "PAM",
        "YPF":              "YPF",
        # ETF Argentina
        "ETF Argentina":    "ARGT",
    },

    "🇨🇱 Chile": {
        # ADR en NYSE
        "Banco Chile":      "BCH",
        "Banco Santander Chile": "BSAC",
        "Enersis":          "ENIA",
        "ETF Chile":        "ECH",
    },

    "🌍 Materias primas": {
        "Oro":              "GLD",
        "Plata":            "SLV",
        "Petróleo WTI":     "USO",
        "Gas Natural":      "UNG",
        "Cobre":            "CPER",
        "Maíz":             "CORN",
        "Soja":             "SOYB",
        "Trigo":            "WEAT",
    },
}

NOTICIAS_TERMINOS = {
    # Criptos
    "BTC-USD":      "Bitcoin",
    "ETH-USD":      "Ethereum",
    "SOL-USD":      "Solana crypto",
    "BNB-USD":      "Binance BNB",
    "ADA-USD":      "Cardano ADA",
    "XRP-USD":      "XRP Ripple",
    "AVAX-USD":     "Avalanche crypto",
    "DOT-USD":      "Polkadot crypto",
    # USA Tech
    "AAPL":         "Apple stock",
    "MSFT":         "Microsoft stock",
    "GOOGL":        "Google Alphabet",
    "AMZN":         "Amazon stock",
    "META":         "Meta Facebook stock",
    "TSLA":         "Tesla stock",
    "NVDA":         "NVIDIA stock",
    # USA Finanzas
    "JPM":          "JPMorgan Chase",
    "GS":           "Goldman Sachs",
    "BRK-B":        "Berkshire Hathaway",
    # USA Energia
    "XOM":          "ExxonMobil",
    "CVX":          "Chevron",
    # ETFs
    "SPY":          "S&P 500 market",
    "QQQ":          "Nasdaq technology",
    "DIA":          "Dow Jones market",
    # Colombia
    "CIB":          "Bancolombia",
    "EC":           "Ecopetrol Colombia oil",
    "GXG":          "Colombia market economy",
    # México
    "AMX":          "America Movil Mexico",
    "CX":           "Cemex Mexico construction",
    "KOF":          "Coca Cola FEMSA Mexico",
    "TV":           "Televisa Mexico media",
    "GTMAY":        "Grupo TMM Mexico",
    "EWW":          "Mexico market economy",
    # Brasil
    "PBR":          "Petrobras Brazil oil",
    "VALE":         "Vale mining Brazil",
    "ITUB":         "Itau Unibanco Brazil",
    "BBD":          "Bradesco Brazil bank",
    "ERJ":          "Embraer Brazil aerospace",
    "NU":           "Nubank Brazil fintech",
    "MELI":         "MercadoLibre ecommerce",
    "EWZ":          "Brazil market economy",
    # Argentina
    "GLOB":         "Globant Argentina tech",
    "LOMA":         "Loma Negra Argentina cement",
    "PAM":          "Pampa Energia Argentina",
    "YPF":          "YPF Argentina oil",
    "ARGT":         "Argentina market economy",
    # Chile
    "BCH":          "Banco de Chile",
    "BSAC":         "Banco Santander Chile",
    "ENIA":         "Enersis Chile energy",
    "ECH":          "Chile market economy",
    # Materias primas
    "GLD":          "gold price commodities",
    "SLV":          "silver price commodities",
    "USO":          "crude oil WTI price",
    "UNG":          "natural gas price",
    "CPER":         "copper price commodities",
    "CORN":         "corn price agriculture",
    "SOYB":         "soybean price agriculture",
    "WEAT":         "wheat price agriculture",
}