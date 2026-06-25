"""Pruebas unitarias para la evaluación de medios de pago."""

import unittest

from main import (
    EXPECTED_WINNERS,
    PAYMENT_METHODS,
    build_evaluation_report,
    get_payment_method,
    get_winners,
    rank_payment_methods,
)


class TestPaymentEvaluation(unittest.TestCase):
    def test_all_methods_have_three_criteria(self) -> None:
        for method in PAYMENT_METHODS:
            self.assertEqual(len(method.scores), 3)
            for score in method.scores.values():
                self.assertGreaterEqual(score, 0)
                self.assertLessEqual(score, 10)

    def test_ranking_contains_all_methods(self) -> None:
        ranking = rank_payment_methods()
        self.assertEqual(len(ranking), 4)
        self.assertEqual(
            {method.id for method in ranking},
            {method.id for method in PAYMENT_METHODS},
        )

    def test_deposit_tokens_lead_ranking(self) -> None:
        ranking = rank_payment_methods()
        self.assertEqual(ranking[0].id, "deposit_tokens")

    def test_bitcoin_ranks_last(self) -> None:
        ranking = rank_payment_methods()
        self.assertEqual(ranking[-1].id, "bitcoin")

    def test_winners_are_stablecoins_and_deposit_tokens(self) -> None:
        winners = get_winners()
        winner_ids = {winner.id for winner in winners}
        self.assertEqual(winner_ids, set(EXPECTED_WINNERS))

    def test_winners_beat_bitcoin(self) -> None:
        """Los híbridos superan a Bitcoin en todos los criterios salvo volatilidad."""
        bitcoin = get_payment_method("bitcoin")
        self.assertIsNotNone(bitcoin)
        assert bitcoin is not None

        for winner in get_winners():
            self.assertGreater(winner.total_score(), bitcoin.total_score())

    def test_cbdc_scores_high_but_is_not_strategic_winner(self) -> None:
        """La CBDC puntúa alto, pero el artículo prioriza modelos híbridos vendibles."""
        cbdc = get_payment_method("cbdc")
        stablecoins = get_payment_method("stablecoins")
        self.assertIsNotNone(cbdc)
        self.assertIsNotNone(stablecoins)
        assert cbdc is not None and stablecoins is not None

        self.assertGreater(cbdc.total_score(), stablecoins.total_score())
        winner_ids = {winner.id for winner in get_winners()}
        self.assertIn("stablecoins", winner_ids)
        self.assertNotIn("cbdc", winner_ids)

    def test_get_payment_method_lookup(self) -> None:
        method = get_payment_method("stablecoins")
        self.assertIsNotNone(method)
        assert method is not None
        self.assertEqual(method.name, "Stablecoins")
        self.assertIsNone(get_payment_method("unknown"))

    def test_build_evaluation_report_structure(self) -> None:
        report = build_evaluation_report()
        self.assertIn("ranking", report)
        self.assertIn("winners", report)
        self.assertIn("conclusion", report)
        self.assertEqual(len(report["ranking"]), 4)
        self.assertEqual(len(report["winners"]), 2)

    def test_total_score_is_sum_of_criteria(self) -> None:
        for method in PAYMENT_METHODS:
            self.assertEqual(method.total_score(), sum(method.scores.values()))


if __name__ == "__main__":
    unittest.main()
