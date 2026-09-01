"""Structural and behavior tests for the branching activity."""

import unittest

from case_content import EVIDENCE_GUIDANCE, FOLLOW_UP_OPTIONS, LENSES, ROUTE_EVIDENCE, TEAM_ROUTES
from case_logic import (
    ACTION_COSTS,
    TOTAL_INVESTIGATION_TOKENS,
    aggregate_evidence_impact,
    assess_evidence_request,
    assess_question,
    assess_risk_statement,
    build_aggregate_conclusion_choices,
    build_conclusion_choices,
    can_afford_action,
    evidence_profile,
    get_evidence,
    get_interpretation_choices,
    get_route,
    interview_effect,
    prepared_evidence_ids,
    pressure_feedback,
    takeaway_for_impact,
)


class RouteStructureTests(unittest.TestCase):
    def test_twelve_unique_team_routes_exist(self):
        self.assertEqual(set(TEAM_ROUTES), set(range(1, 13)))
        codes = [route["code"] for route in TEAM_ROUTES.values()]
        self.assertEqual(len(codes), len(set(codes)))

    def test_each_route_resolves_to_a_valid_lens_and_evidence_set(self):
        for team_number in TEAM_ROUTES:
            route = get_route(team_number)
            lens = route["lens_content"]
            self.assertIn(route["lens"], LENSES)
            self.assertEqual(set(lens["evidence_options"]), set(route["evidence_results"]))
            self.assertEqual(set(lens["evidence_options"]), set(EVIDENCE_GUIDANCE[route["lens"]]))
            self.assertEqual(len(lens["question_tactics"]), 3)

    def test_routes_cycle_evenly_across_four_lenses(self):
        counts = {lens: 0 for lens in LENSES}
        for route in TEAM_ROUTES.values():
            counts[route["lens"]] += 1
        self.assertEqual(set(counts.values()), {3})

    def test_every_evidence_result_has_valid_impact_and_substance(self):
        valid_impacts = {"decrease", "mixed", "increase", "limited"}
        for route_results in ROUTE_EVIDENCE.values():
            for result in route_results.values():
                self.assertIn(result["impact"], valid_impacts)
                self.assertGreater(len(result["result"]), 45)

    def test_invalid_team_and_evidence_are_rejected(self):
        with self.assertRaises(ValueError):
            get_route(0)
        with self.assertRaises(ValueError):
            get_evidence("ASTER", "not-a-source")


class CoachingTests(unittest.TestCase):
    def test_neutral_evidence_question_receives_positive_feedback(self):
        feedback = assess_question(
            "Walk me through which audit-log records preserve the original approval and timestamp."
        )
        strong_titles = {item["title"] for item in feedback if item["status"] == "strong"}
        self.assertIn("Neutral opening", strong_titles)
        self.assertIn("Evidence connection", strong_titles)

    def test_accusatory_question_is_flagged(self):
        feedback = assess_question("Isn't double-counting just an excuse for the override spike?")
        self.assertTrue(any(item["title"] == "The wording assumes the conclusion" for item in feedback))

    def test_neutral_risk_statement_is_recognized(self):
        statement = (
            "Based on the approval log, we cannot yet determine whether independent approval "
            "occurred before dispatch for all sampled overrides. We will obtain the immutable "
            "approval history and timestamps for the four-week period to assess the sequence."
        )
        feedback = assess_risk_statement(statement)
        strong_titles = {item["title"] for item in feedback if item["status"] == "strong"}
        self.assertIn("Uncertainty is stated precisely", strong_titles)
        self.assertIn("Evidence is connected to the conclusion", strong_titles)

    def test_specific_evidence_request_is_recognized(self):
        feedback = assess_evidence_request(
            "Provide the approval log with user IDs and timestamps for the 15 sampled overrides."
        )
        self.assertTrue(all(item["status"] == "strong" for item in feedback))

    def test_pressure_feedback_changes_with_evidence_impact(self):
        close_mixed = pressure_feedback("close", "mixed")
        close_decrease = pressure_feedback("close", "decrease")
        self.assertNotEqual(close_mixed["message"], close_decrease["message"])

    def test_interpretation_and_conclusion_are_tied_to_evidence_impact(self):
        route = get_route(1)
        result = get_evidence("ASTER", "raw_log")
        interpretations = get_interpretation_choices(result["impact"])
        conclusions = build_conclusion_choices(route, result)

        self.assertEqual(set(interpretations), {"bounded", "average", "all_fail"})
        self.assertIn(result["result"], conclusions["bounded"]["label"])
        self.assertEqual(conclusions["bounded"]["status"], "strong")

    def test_each_lens_has_three_follow_up_choices(self):
        for lens_id in LENSES:
            self.assertEqual(len(FOLLOW_UP_OPTIONS[lens_id]), 3)

    def test_predictions_do_not_repeat_the_conditional_prompt(self):
        for lens_guidance in EVIDENCE_GUIDANCE.values():
            for source in lens_guidance.values():
                self.assertFalse(source["prediction"].lower().startswith("if "))
                self.assertGreater(len(source["without_context"]), 80)
                self.assertTrue(source["preparation_prompt"].endswith("?"))

    def test_interview_choices_prepare_matching_sources_without_gating_others(self):
        route = get_route(1)
        self.assertEqual(prepared_evidence_ids(route, ["trace"]), ["raw_log"])
        self.assertEqual(prepared_evidence_ids(route, ["scope", "trace"]), ["transform", "raw_log"])
        self.assertEqual(len(route["lens_content"]["evidence_options"]), 3)
        self.assertEqual(evidence_profile(route, "raw_log")["cost"], 1)
        self.assertEqual(evidence_profile(route, "summary")["strength_label"], "Limited")

    def test_shared_budget_forces_breadth_or_revision_tradeoff(self):
        self.assertEqual(TOTAL_INVESTIGATION_TOKENS, 6)
        self.assertEqual(set(ACTION_COSTS.values()), {1})
        broad_route = (
            ACTION_COSTS["interview_question"] * 2
            + ACTION_COSTS["evidence_source"] * 2
            + ACTION_COSTS["pressure_response"]
            + ACTION_COSTS["judgment_test"]
        )
        revision_route = (
            ACTION_COSTS["interview_question"]
            + ACTION_COSTS["evidence_source"]
            + ACTION_COSTS["pressure_response"]
            + ACTION_COSTS["pressure_revision"]
            + ACTION_COSTS["judgment_test"]
            + ACTION_COSTS["judgment_revision"]
        )
        self.assertEqual(broad_route, TOTAL_INVESTIGATION_TOKENS)
        self.assertEqual(revision_route, TOTAL_INVESTIGATION_TOKENS)
        self.assertTrue(can_afford_action(4, "evidence_source", reserve=2))
        self.assertFalse(can_afford_action(2, "evidence_source", reserve=2))

    def test_interview_tone_changes_access(self):
        self.assertEqual(interview_effect(["trace"])["relationship"], "Open")
        self.assertEqual(interview_effect(["challenge"])["relationship"], "Strained")
        self.assertEqual(interview_effect(["challenge", "trace"])["relationship"], "Stable")

    def test_multiple_sources_preserve_conflicting_results(self):
        route = get_route(1)
        history = [
            {
                "label": "Dashboard transformation logic",
                "result": get_evidence("ASTER", "transform")["result"],
                "impact": "decrease",
                "strength": 2,
            },
            {
                "label": "Raw override log",
                "result": get_evidence("ASTER", "raw_log")["result"],
                "impact": "mixed",
                "strength": 3,
            },
        ]
        self.assertEqual(aggregate_evidence_impact(history), "mixed")
        choices = build_aggregate_conclusion_choices(route, history)
        self.assertEqual(choices["bounded"]["status"], "strong")
        self.assertIn(history[1]["result"], choices["bounded"]["label"])
        self.assertIn("narrow the conclusion", takeaway_for_impact("mixed"))


if __name__ == "__main__":
    unittest.main()
