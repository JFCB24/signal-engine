import os
import sys
from datetime import datetime, timedelta

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from config.settings import NOTICIAS_TERMINOS

def obtener_noticias(ticker):
    termino = NOTICIAS_TERMINOS.get(ticker, ticker)

    try:
        from dotenv import load_dotenv
        load_dotenv()
        api_key = os.getenv("NEWSAPI_KEY")

        if api_key:
            from newsapi import NewsApiClient
            newsapi = NewsApiClient(api_key=api_key)
            fecha_desde = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
            respuesta = newsapi.get_everything(
                q=termino,
                from_param=fecha_desde,
                language="en",
                sort_by="publishedAt",
                page_size=10
            )
            if respuesta["status"] == "ok" and respuesta["articles"]:
                titulares = [a["title"] for a in respuesta["articles"]
                             if a["title"] and a["title"] != "[Removed]"]
                return titulares
    except Exception as e:
        print(f"NewsAPI no disponible: {e}")

    # Noticias de ejemplo
    noticias_ejemplo = {
        "BTC-USD": [
            "Bitcoin surges as institutional investors increase holdings",
            "Crypto market faces regulatory uncertainty from SEC",
            "Bitcoin mining difficulty reaches all time high",
            "Major bank announces Bitcoin custody services",
            "Bitcoin price consolidates after recent volatility",
        ],
        "ETH-USD": [
            "Ethereum network upgrade improves transaction speed",
            "DeFi protocols see record volume on Ethereum",
            "Ethereum staking rewards attract institutional interest",
        ],
    }
    return noticias_ejemplo.get(ticker, [
        f"{termino} shows market activity",
        f"Analysts review {termino} performance",
        f"{termino} trading volume remains stable",
    ])


def analizar_sentimiento(titulares):
    """
    Análisis de sentimiento liviano sin FinBERT.
    Usa diccionario financiero de palabras positivas y negativas.
    No requiere torch ni transformers — funciona en Streamlit Cloud gratis.
    """
    if not titulares:
        return 0.0, "neutral"

    palabras_positivas = {
        "surge", "surges", "gain", "gains", "rise", "rises", "up", "high",
        "record", "growth", "strong", "beat", "beats", "exceed", "exceeds",
        "profit", "profits", "rally", "rallies", "bull", "bullish", "boost",
        "boosts", "positive", "outperform", "upgrade", "buy", "expand",
        "expands", "increase", "increases", "improved", "improves", "higher",
        "announces", "launches", "wins", "success", "opportunity", "recover",
        "recovers", "accelerate", "accelerates", "above", "attractive",
    }

    palabras_negativas = {
        "fall", "falls", "drop", "drops", "decline", "declines", "down",
        "low", "loss", "losses", "weak", "miss", "misses", "below", "bear",
        "bearish", "risk", "risks", "concern", "concerns", "uncertainty",
        "crash", "crashes", "sell", "fear", "fears", "negative", "downgrade",
        "cut", "cuts", "reduce", "reduces", "decrease", "decreases", "lower",
        "problem", "problems", "issue", "issues", "warning", "scrutiny",
        "denied", "fail", "fails", "halt", "halts", "suspend", "suspends",
    }

    score_total = 0
    palabras_analizadas = 0

    for titular in titulares[:5]:
        palabras = titular.lower().split()
        for palabra in palabras:
            palabra_limpia = palabra.strip(".,!?;:")
            if palabra_limpia in palabras_positivas:
                score_total += 1
                palabras_analizadas += 1
            elif palabra_limpia in palabras_negativas:
                score_total -= 1
                palabras_analizadas += 1

    if palabras_analizadas == 0:
        return 0.0, "neutral"

    score = score_total / max(palabras_analizadas, 1)
    score = max(-1.0, min(1.0, score))

    if score > 0.1:    etiqueta = "positivo"
    elif score < -0.1: etiqueta = "negativo"
    else:              etiqueta = "neutral"

    return round(score, 4), etiqueta


if __name__ == "__main__":
    ticker = "BTC-USD"
    titulares = obtener_noticias(ticker)
    print(f"Titulares:")
    for t in titulares:
        print(f"  - {t}")
    score, etiqueta = analizar_sentimiento(titulares)
    print(f"\nSentimiento: {etiqueta} ({score})")