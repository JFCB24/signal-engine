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

# ── Catálogo completo de activos ────────────────────────────
ACTIVOS = {

    # Criptomonedas
    "🪙 Criptomonedas": {
        "Bitcoin":  "BTC-USD",
        "Ethereum": "ETH-USD",
        "Solana":   "SOL-USD",
        "BNB":      "BNB-USD",
        "Cardano":  "ADA-USD",
    },

    # Acciones USA
    "🇺🇸 Estados Unidos": {
        "Apple":    "AAPL",
        "Tesla":    "TSLA",
        "Microsoft":"MSFT",
        "Google":   "GOOGL",
        "Amazon":   "AMZN",
    },

    # Colombia — BVC
    "🇨🇴 Colombia (BVC)": {
        "Bancolombia":      "CIB",
        "Ecopetrol":        "EC",
        "Grupo Nutresa":    "NUTRESA.CL",
        "Grupo Sura":       "GRUPOSURA.CL",
        "Cemargos":         "CEMARGOS.CL",
    },

    # México — BMV
    "🇲🇽 México (BMV)": {
        "America Movil":    "AMXL.MX",
        "FEMSA":            "FEMSAUBD.MX",
        "Cemex":            "CEMEXCPO.MX",
        "Grupo Bimbo":      "BIMBOA.MX",
        "Walmex":           "WALMEX.MX",
    },

    # Brasil — B3
    "🇧🇷 Brasil (B3)": {
        "Petrobras":        "PBR",
        "Vale":             "VALE",
        "Itau Unibanco":    "ITUB",
        "Bradesco":         "BBD",
        "Embraer":          "ERJ",
    },
}

# Términos de búsqueda para noticias por ticker
NOTICIAS_TERMINOS = {
    "BTC-USD":          "Bitcoin",
    "ETH-USD":          "Ethereum",
    "SOL-USD":          "Solana crypto",
    "BNB-USD":          "Binance BNB crypto",
    "ADA-USD":          "Cardano ADA crypto",
    "AAPL":             "Apple stock",
    "TSLA":             "Tesla stock",
    "MSFT":             "Microsoft stock",
    "GOOGL":            "Google Alphabet stock",
    "AMZN":             "Amazon stock",
    "CIB":              "Bancolombia",
    "EC":               "Ecopetrol Colombia",
    "NUTRESA.CL":       "Grupo Nutresa Colombia",
    "GRUPOSURA.CL":     "Grupo Sura Colombia",
    "CEMARGOS.CL":      "Cemargos Colombia",
    "AMXL.MX":          "America Movil Mexico",
    "FEMSAUBD.MX":      "FEMSA Mexico",
    "CEMEXCPO.MX":      "Cemex Mexico",
    "BIMBOA.MX":        "Grupo Bimbo Mexico",
    "WALMEX.MX":        "Walmart Mexico Walmex",
    "PBR":              "Petrobras Brazil",
    "VALE":             "Vale mining Brazil",
    "ITUB":             "Itau Unibanco Brazil",
    "BBD":              "Bradesco Brazil",
    "ERJ":              "Embraer Brazil",
}