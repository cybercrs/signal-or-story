"""Streamlit rendering smoke test."""

import unittest
from pathlib import Path

from streamlit.testing.v1 import AppTest


class StreamlitSmokeTests(unittest.TestCase):
    def test_setup_screen_renders_without_exception(self):
        app = AppTest.from_file("streamlit_app.py").run(timeout=15)

        self.assertEqual(len(app.exception), 0)
        self.assertEqual(len(app.text_input), 0)
        self.assertEqual(len(app.text_area), 0)
        self.assertEqual(len(app.number_input), 1)
        self.assertEqual(app.number_input[0].value, 1)
        self.assertTrue(any(button.label == "Open your case" for button in app.button))
        visible_markdown = "\n".join(item.value for item in app.markdown)
        self.assertNotIn("Choose your roles", visible_markdown)
        self.assertNotIn("Option reader", visible_markdown)
        self.assertIn("zero, one, or two questions", visible_markdown)
        self.assertIn("six-token investigation budget", visible_markdown)
        self.assertIn("Every investigative action costs one token", visible_markdown)
        self.assertIn("A second question plus a second source", visible_markdown)
        self.assertIn("all three sources are available", visible_markdown)
        self.assertIn("does not connect to a question you asked", visible_markdown)

    def test_team_one_opens_without_internal_route_code_or_free_text(self):
        app = AppTest.from_file("streamlit_app.py").run(timeout=15)
        open_button = next(button for button in app.button if button.label == "Open your case")
        app = open_button.click().run(timeout=15)

        self.assertEqual(len(app.exception), 0)
        self.assertEqual(len(app.text_input), 0)
        self.assertEqual(len(app.text_area), 0)
        visible_markdown = "\n".join(item.value for item in app.markdown)
        self.assertNotIn("ASTER", visible_markdown)
        self.assertIn("Your assignment", visible_markdown)
        self.assertIn("does not display unique override IDs", visible_markdown)
        self.assertIn("38 dashboard rows overstate", visible_markdown)
        self.assertIn("6 OF 6 TOKENS LEFT", visible_markdown)
        self.assertTrue(any(button.label == "Begin the interview" for button in app.button))

    def test_all_sources_are_available_but_unprepared_evidence_is_less_useful(self):
        app = AppTest.from_file("streamlit_app.py").run(timeout=15)
        app = next(button for button in app.button if button.label == "Open your case").click().run(timeout=15)
        app = next(button for button in app.button if button.label == "Begin the interview").click().run(timeout=15)
        self.assertTrue(any(button.label == "Skip questions and move to evidence" for button in app.button))
        app.radio[0].set_value("trace")
        app = next(
            button for button in app.button if button.label == "Ask the selected question · 1 token"
        ).click().run(timeout=15)
        app = next(button for button in app.button if button.label == "Move to evidence").click().run(timeout=15)

        self.assertEqual(len(app.radio[0].options), 3)
        self.assertTrue(any("Interview context established" in option for option in app.radio[0].options))
        self.assertEqual(
            sum("No matching interview context" in option for option in app.radio[0].options),
            2,
        )

        app.radio[0].set_value("transform")
        app = next(
            button for button in app.button if button.label == "Obtain selected source · 1 token"
        ).click().run(timeout=15)
        first_result = app.session_state["evidence_history"][0]
        self.assertFalse(first_result["prepared"])
        self.assertEqual(first_result["impact"], "limited")
        self.assertIn("has not established which dashboard count", first_result["result"])
        self.assertNotIn("seven pairs of duplicates", first_result["result"])
        self.assertIn("before first asking", first_result["preparation_note"])

        app.radio[0].set_value("raw_log")
        app = next(
            button for button in app.button if button.label == "Obtain selected source · 1 token"
        ).click().run(timeout=15)
        second_result = app.session_state["evidence_history"][1]
        self.assertTrue(second_result["prepared"])
        self.assertEqual(second_result["impact"], "mixed")
        self.assertIn("Fourteen near-dispatch dashboard rows", second_result["result"])
        self.assertEqual(len(app.radio), 0)
        self.assertTrue(any("two-source limit" in item.value for item in app.info))

    def test_interview_can_be_skipped_without_hiding_evidence(self):
        app = AppTest.from_file("streamlit_app.py").run(timeout=15)
        app = next(button for button in app.button if button.label == "Open your case").click().run(timeout=15)
        app = next(button for button in app.button if button.label == "Begin the interview").click().run(timeout=15)
        app = next(
            button for button in app.button if button.label == "Skip questions and move to evidence"
        ).click().run(timeout=15)

        self.assertEqual(len(app.radio[0].options), 3)
        self.assertTrue(all("No matching interview context" in option for option in app.radio[0].options))
        app.radio[0].set_value("raw_log")
        app = next(
            button for button in app.button if button.label == "Obtain selected source · 1 token"
        ).click().run(timeout=15)
        result = app.session_state["evidence_history"][0]
        self.assertFalse(result["prepared"])
        self.assertEqual(result["impact"], "limited")

    def test_navigation_copy_and_scroll_resets_stop_after_student_input(self):
        source = Path("streamlit_app.py").read_text(encoding="utf-8")
        self.assertIn("scroll_pending", source)
        self.assertIn("scroll_request_id", source)
        self.assertIn("__SCROLL_REQUEST_ID__", source)
        self.assertIn("cancelledByStudent", source)
        self.assertIn("addEventListener('wheel'", source)
        self.assertEqual(source.count("scroller.scrollTo"), 1)
        self.assertNotIn("[75, 250, 600, 1000, 1500]", source)
        self.assertNotIn("Be ready to compare routes", source)
        self.assertNotIn("Current interview access", source)
        self.assertNotIn("Combined evidence position", source)
        self.assertNotIn("Evidence unlocked", source)
        self.assertNotIn("Sources unlocked", source)

    def test_student_copy_uses_plain_reporting_language(self):
        source = Path("streamlit_app.py").read_text(encoding="utf-8")
        content = Path("case_content.py").read_text(encoding="utf-8")
        unfamiliar_term = "arti" + "fact"
        self.assertNotIn(unfamiliar_term, f"{source}\n{content}".lower())


if __name__ == "__main__":
    unittest.main()
