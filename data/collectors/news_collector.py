import os
import sys
from datetime import datetime, timedelta

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from config.settings import NOTICIAS_TERMINOS

def obtener_noticias(ticker):
    """
    Obtiene noticias recientes del activo.
    Usa NewsAPI si hay key disponible, sino usa noticias de ejemplo.
    """

    termino = NOTICIAS_TERMINOS.get(ticker, ticker)

    # Intentar con NewsAPI
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
                print(f"Noticias obtenidas de NewsAPI: {len(titulares)}")
                return titulares

    except Exception as e:
        print(f"NewsAPI no disponible: {e}")

    # Noticias de ejemplo por categoría
    print("Usando noticias de ejemplo...")

    noticias_ejemplo = {
        # Criptos
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
            "Ethereum developers announce new roadmap update",
            "ETH price rises amid growing developer activity",
        ],
        "SOL-USD": [
            "Solana network processes record transactions per second",
            "Major DeFi project launches on Solana blockchain",
            "Solana price rallies after network upgrade",
            "Institutional interest grows in Solana ecosystem",
            "Solana outperforms market amid bullish sentiment",
        ],
        "BNB-USD": [
            "Binance expands services to new markets globally",
            "BNB token burns reach quarterly record",
            "Binance Smart Chain sees surge in DeFi activity",
            "BNB holds support level amid market uncertainty",
            "Binance announces new product launch for retail investors",
        ],
        "ADA-USD": [
            "Cardano smart contracts see growing adoption",
            "ADA price rises after successful network upgrade",
            "Cardano foundation announces new partnerships in Africa",
            "Cardano developer activity reaches new highs",
            "ADA consolidates amid broader crypto market moves",
        ],
        # USA
        "AAPL": [
            "Apple reports record iPhone sales in emerging markets",
            "Apple faces antitrust scrutiny in European markets",
            "Apple announces new AI features for upcoming devices",
            "Apple supply chain shows signs of improvement",
            "Apple services revenue grows faster than hardware",
        ],
        "TSLA": [
            "Tesla deliveries exceed analyst expectations this quarter",
            "Tesla faces increased competition in EV market",
            "Tesla expands supercharger network globally",
            "Tesla announces new affordable model for mass market",
            "Tesla energy division reports record revenue",
        ],
        "MSFT": [
            "Microsoft Azure cloud revenue grows above expectations",
            "Microsoft AI integration boosts enterprise sales",
            "Microsoft announces new Copilot features for Office",
            "Microsoft gaming division expands with new titles",
            "Microsoft reports strong quarterly earnings results",
        ],
        "GOOGL": [
            "Google advertising revenue recovers amid market growth",
            "Google Cloud gains market share from competitors",
            "Google announces new AI model for search improvement",
            "Alphabet reports strong earnings beating estimates",
            "Google faces regulatory challenges in multiple markets",
        ],
        "AMZN": [
            "Amazon AWS cloud services see accelerating growth",
            "Amazon Prime membership reaches new global record",
            "Amazon logistics network expansion drives efficiency",
            "Amazon advertising business grows faster than expected",
            "Amazon announces new AI tools for enterprise customers",
        ],
        # Colombia
        "CIB": [
            "Bancolombia reports strong loan growth in Colombia",
            "Bancolombia digital banking users surpass 10 million",
            "Colombia banking sector shows resilience amid rate changes",
            "Bancolombia expands operations in Central America",
            "Bancolombia profits rise on higher interest margins",
        ],
        "EC": [
            "Ecopetrol increases oil production targets for the year",
            "Ecopetrol announces new offshore exploration contracts",
            "Colombia oil sector benefits from higher crude prices",
            "Ecopetrol invests in renewable energy transition",
            "Ecopetrol reports strong quarterly financial results",
        ],
        "NUTRESA.CL": [
            "Grupo Nutresa expands product lines across Latin America",
            "Nutresa reports steady revenue growth in food segment",
            "Colombia consumer goods sector shows strong demand",
            "Nutresa announces strategic acquisitions in the region",
            "Nutresa dividend yield attracts long term investors",
        ],
        "GRUPOSURA.CL": [
            "Grupo Sura reports strong insurance and pension results",
            "Sura expands financial services across Latin America",
            "Colombia financial conglomerate shows stable earnings",
            "Grupo Sura diversifies portfolio amid market volatility",
            "Sura announces digital transformation strategy",
        ],
        "CEMARGOS.CL": [
            "Cemargos benefits from infrastructure spending in Colombia",
            "Cement demand rises amid construction sector growth",
            "Cemargos reports improved margins on cost efficiencies",
            "Colombia infrastructure projects drive cement demand",
            "Cemargos expands capacity to meet regional demand",
        ],
        # México
        "AMXL.MX": [
            "America Movil adds subscribers across Latin America",
            "AMX expands 5G network coverage in major cities",
            "America Movil reports steady revenue from telecom services",
            "AMX announces new digital services for enterprise clients",
            "America Movil benefits from growing mobile data demand",
        ],
        "FEMSAUBD.MX": [
            "FEMSA Coca Cola reports record volume in Mexico",
            "FEMSA expands OXXO convenience stores across region",
            "FEMSA reports strong quarterly earnings above estimates",
            "FEMSA logistics division shows improving margins",
            "FEMSA announces new strategic investments in retail",
        ],
        "CEMEXCPO.MX": [
            "Cemex benefits from US infrastructure spending boom",
            "Cemex reports improved pricing across all regions",
            "Cemex reduces debt ahead of schedule this quarter",
            "Cemex announces sustainable cement production targets",
            "Cemex wins major infrastructure contracts in Europe",
        ],
        "BIMBOA.MX": [
            "Grupo Bimbo expands bakery operations in Asia",
            "Bimbo reports steady revenue growth in North America",
            "Bimbo launches new healthy product lines globally",
            "Grupo Bimbo announces acquisition in European market",
            "Bimbo benefits from premiumization trend in food sector",
        ],
        "WALMEX.MX": [
            "Walmart Mexico reports strong same store sales growth",
            "Walmex ecommerce penetration continues to accelerate",
            "Walmart Mexico expands store network in smaller cities",
            "Walmex reports record quarterly revenue in Mexico",
            "Walmart Mexico benefits from consumer spending recovery",
        ],
        # Brasil
        "PBR": [
            "Petrobras increases dividend payout to shareholders",
            "Petrobras reports record oil production in pre-salt fields",
            "Brazil oil sector benefits from higher global crude prices",
            "Petrobras announces new deepwater exploration program",
            "Petrobras reduces debt while maintaining production growth",
        ],
        "VALE": [
            "Vale iron ore shipments exceed quarterly expectations",
            "Vale reports strong nickel demand from EV battery makers",
            "Brazil mining sector shows resilience amid China slowdown",
            "Vale announces new copper projects for energy transition",
            "Vale reduces environmental liabilities ahead of schedule",
        ],
        "ITUB": [
            "Itau Unibanco reports strong loan growth in Brazil",
            "Itau digital banking platform surpasses 60 million users",
            "Brazil banking sector shows improving credit quality",
            "Itau expands operations across Latin American markets",
            "Itau reports record net income beating analyst estimates",
        ],
        "BBD": [
            "Bradesco reports improved efficiency ratio this quarter",
            "Bradesco digital transformation drives cost reduction",
            "Brazil consumer credit demand shows signs of recovery",
            "Bradesco insurance division reports record premiums",
            "Bradesco announces new digital banking features",
        ],
        "ERJ": [
            "Embraer delivers record number of jets this quarter",
            "Embraer wins new regional jet orders from Asian airlines",
            "Embraer executive jet division reports strong backlog",
            "Brazil aerospace sector benefits from travel recovery",
            "Embraer announces new sustainable aviation fuel program",
        ],
    }

    return noticias_ejemplo.get(ticker, [
        f"{termino} shows market activity",
        f"Analysts review {termino} performance",
        f"{termino} trading volume remains stable",
    ])


def analizar_sentimiento(titulares):
    """
    Usa FinBERT para analizar el sentimiento de los titulares.
    Devuelve un score entre -1 (muy negativo) y +1 (muy positivo).
    """

    if not titulares:
        return 0.0, "neutral"

    print("Cargando modelo FinBERT...")

    try:
        from transformers import pipeline

        sentimiento_pipeline = pipeline(
            "text-classification",
            model="ProsusAI/finbert",
            tokenizer="ProsusAI/finbert",
            top_k=None
        )

        scores_positivos = []
        scores_negativos = []

        for titular in titulares[:5]:
            try:
                resultado = sentimiento_pipeline(titular[:512])[0]
                for item in resultado:
                    if item["label"] == "positive":
                        scores_positivos.append(item["score"])
                    elif item["label"] == "negative":
                        scores_negativos.append(item["score"])
            except:
                continue

        if not scores_positivos and not scores_negativos:
            return 0.0, "neutral"

        avg_pos = sum(scores_positivos) / len(scores_positivos) if scores_positivos else 0
        avg_neg = sum(scores_negativos) / len(scores_negativos) if scores_negativos else 0

        score = avg_pos - avg_neg

        if score > 0.2:    etiqueta = "positivo"
        elif score < -0.2: etiqueta = "negativo"
        else:              etiqueta = "neutral"

        print(f"Sentimiento: {etiqueta} (score: {score:.3f})")
        return round(score, 4), etiqueta

    except Exception as e:
        print(f"Error en FinBERT: {e}")
        return 0.0, "neutral"


if __name__ == "__main__":
    ticker = "EC"
    print(f"Analizando sentimiento para {ticker}...")
    titulares = obtener_noticias(ticker)
    print(f"\nTitulares encontrados:")
    for t in titulares:
        print(f"  - {t}")
    score, etiqueta = analizar_sentimiento(titulares)
    print(f"\nResultado: {etiqueta} ({score})")