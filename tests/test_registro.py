import pandas as pd

from models import registro


def _senal(fecha, senal="ALCISTA", ticker="BTC-USD"):
    return {"fecha": fecha, "ticker": ticker, "precio": 100.0, "senal": senal,
            "prob_alcista": 0.7, "prob_bajista": 0.3, "confianza": "ALTA"}


def test_no_duplica_la_misma_fecha(tmp_path, monkeypatch):
    monkeypatch.setattr(registro, "RUTA_REGISTRO", str(tmp_path / "r.csv"))
    assert registro.registrar_senal(_senal("2026-01-01")) is True
    assert registro.registrar_senal(_senal("2026-01-01")) is False
    assert len(pd.read_csv(registro.RUTA_REGISTRO)) == 1


def test_califica_con_el_cierre_siguiente(tmp_path, monkeypatch):
    monkeypatch.setattr(registro, "RUTA_REGISTRO", str(tmp_path / "r.csv"))
    registro.registrar_senal(_senal("2026-01-01", "ALCISTA"))
    registro.registrar_senal(_senal("2026-01-02", "BAJISTA"))
    registro.registrar_senal(_senal("2026-01-03", "NEUTRAL"))
    precios = {"BTC-USD": pd.Series(
        [100.0, 110.0, 105.0, 120.0],
        index=["2026-01-01", "2026-01-02", "2026-01-03", "2026-01-04"])}
    resumen = registro.calificar_registro(precios)
    # 01-01 ALCISTA, sube 110 > 100 -> acierto
    # 01-02 BAJISTA, baja 105 < 110 -> acierto
    # 01-03 NEUTRAL -> no cuenta
    assert resumen["calificadas"] == 2
    assert resumen["aciertos"] == 2
    assert resumen["accuracy"] == 1.0
