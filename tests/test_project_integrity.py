import unittest

from compliance_engine import audit_green_claims, check_workforce_scheduling
from config_loader import load_config
from consumer_psychology_model import GermanConsumer
from scenario_runner import (
    build_city_portfolio,
    build_decision_matrix,
    run_replication_engine,
    summarize_replication_results,
)


class ProjectIntegrityTests(unittest.TestCase):
    def test_consumer_marketing_threshold(self):
        cfg = load_config(use_refresh=False)
        consumer = GermanConsumer(cfg)

        weak = consumer.count_information_cues("High quality and low price")
        strong = consumer.count_information_cues(
            "Bio milk 1L, EUR 1.29/L, ISO 22000, DIN EN tested, 3.5% fat, class A, 12-month shelf, protein 3.4g"
        )

        self.assertEqual(weak.decision, "REJECT")
        self.assertEqual(strong.decision, "CONSIDER")

    def test_compliance_flags_trigger(self):
        green = audit_green_claims([
            "Climate Neutral cleaner",
            "Eco-friendly soap ISO 14067 certified",
        ])
        workforce = check_workforce_scheduling([
            {
                "warehouse": "Berlin",
                "notice_period_days": 3,
                "monitoring_type": "individual_performance_tracking",
            }
        ])

        green_statuses = {row["status"] for row in green}
        self.assertIn("VIOLATION", green_statuses)
        self.assertIn("WORKS_COUNCIL_ALERT", workforce[0]["alerts"])
        self.assertIn("GDPR_BETRIEBSRAT_VIOLATION", workforce[0]["alerts"])

    def test_city_portfolio_outputs(self):
        cfg = load_config(use_refresh=False)
        # Fast test run settings.
        cfg["simulation"]["n_replications"] = 3
        cfg["simulation"]["n_households_monte_carlo"] = 500
        cfg["simulation"]["random_seed"] = 123

        consumer = GermanConsumer(cfg)
        replication_df, _ = run_replication_engine(cfg, consumer)
        summary_df = summarize_replication_results(replication_df, cfg)
        decision_df = build_decision_matrix(summary_df, cfg)

        city_strategy_df, city_reco_df, city_plan_df = build_city_portfolio(cfg, summary_df, decision_df)

        self.assertGreater(len(city_strategy_df), 0)
        self.assertGreater(len(city_reco_df), 0)
        self.assertEqual(city_reco_df["city"].nunique(), len(city_reco_df))
        self.assertTrue(city_plan_df["launch_wave"].isin(["Wave 1 Pilot", "Wave 2 Scale", "Wave 3 Option", "Hold"]).all())


if __name__ == "__main__":
    unittest.main()
