"""Pruebas del evaluador y fuentes de datos."""

import unittest
from unittest.mock import patch

from data_sources import CBDC_ECOSYSTEM, format_snapshot_text
from evaluator import build_live_methods, run_ecosystem_evaluation
from agent import _should_run_full_evaluation


MOCK_SNAPSHOT = {
    "fetched_at": "2026-06-25T12:00:00+00:00",
    "market": {
        "ok": True,
        "source": "CoinGecko",
        "bitcoin": {
            "price_usd": 95000,
            "change_24h_pct": 2.1,
            "change_7d_pct": 12.5,
            "market_cap_usd": 1.8e12,
        },
        "stablecoins": {
            "usdt_cap_b": 120.0,
            "usdc_cap_b": 45.0,
            "dai_cap_b": 5.0,
            "total_cap_b": 170.0,
        },
        "global_crypto_cap_b": 2800.0,
    },
    "cbdc": CBDC_ECOSYSTEM,
    "ai_payments": {"tendencia": "test", "agentes_comerciales": ["OpenAI API"]},
}


class TestEvaluator(unittest.TestCase):
    def test_build_live_methods_returns_four(self) -> None:
        methods = build_live_methods(MOCK_SNAPSHOT)
        self.assertEqual(len(methods), 4)

    def test_bitcoin_volatility_reduces_stability(self) -> None:
        methods = build_live_methods(MOCK_SNAPSHOT)
        bitcoin = next(m for m in methods if m.id == "bitcoin")
        self.assertLessEqual(bitcoin.scores["estabilidad_financiera"], 2)

    def test_stablecoins_boost_with_high_cap(self) -> None:
        methods = build_live_methods(MOCK_SNAPSHOT)
        stable = next(m for m in methods if m.id == "stablecoins")
        self.assertGreaterEqual(stable.scores["compatibilidad_ia"], 9)

    def test_evaluation_report_structure(self) -> None:
        report = run_ecosystem_evaluation(MOCK_SNAPSHOT)
        self.assertEqual(report["mode"], "agent_evaluation")
        self.assertEqual(len(report["ranking"]), 4)
        self.assertEqual(len(report["winners"]), 2)
        self.assertIn("live_data_text", report)

    def test_format_snapshot_contains_bitcoin(self) -> None:
        text = format_snapshot_text(MOCK_SNAPSHOT)
        self.assertIn("Bitcoin", text)
        self.assertIn("Stablecoins", text)


class TestAgentTriggers(unittest.TestCase):
    def test_evaluation_trigger(self) -> None:
        self.assertTrue(_should_run_full_evaluation("Evalúa el ecosistema de pagos"))
        self.assertTrue(_should_run_full_evaluation("Analiza el mercado actual"))

    def test_chat_no_trigger(self) -> None:
        self.assertFalse(_should_run_full_evaluation("¿Qué es una stablecoin?"))


if __name__ == "__main__":
    unittest.main()
