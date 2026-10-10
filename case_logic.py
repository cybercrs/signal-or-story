"""Pure logic for the Signal or Story Streamlit activity."""

from __future__ import annotations

import re
from typing import Any

from case_content import (
    INTERPRETATION_CHOICES,
    LENSES,
    PRESSURE_CHOICES,
    ROUTE_EVIDENCE,
    TEAM_ROUTES,
    UNRESOLVED_QUESTIONS,
)


TOTAL_INVESTIGATION_TOKENS = 6
ACTION_COSTS = {
    "interview_question": 1,
    "evidence_source": 1,
    "pressure_response": 1,
    "pressure_revision": 1,
    "judgment_test": 1,
    "judgment_revision": 1,
}


def can_afford_action(remaining: int, action_id: str, reserve: int = 0) -> bool:
    """Return whether an action fits while preserving required future capacity."""
    if action_id not in ACTION_COSTS:
        raise ValueError(f"Unknown investigation action: {action_id}")
    if remaining < 0 or reserve < 0:
        raise ValueError("Budget values cannot be negative.")
    return remaining - ACTION_COSTS[action_id] >= reserve


ACCUSATORY_TERMS = (
    "lied",
    "lying",
    "fraud",
    "cover up",
    "cover-up",
    "ignored policy",
    "violated policy",
    "because no one was watching",
    "prove you did not",
    "just an excuse",
)

NEUTRAL_CUES = (
    "walk me through",
    "what",
    "which",
    "where",
    "when",
    "how",
    "describe",
    "help us understand",
)

EVIDENCE_CUES = (
    "record",
    "log",
    "timestamp",
    "user id",
    "approval",
    "work order",
    "work-order",
    "roster",
    "telematics",
    "history",
    "source",
    "version",
)


def get_route(team_number: int) -> dict[str, Any]:
    """Return a complete, copy-safe route definition for a team number."""
    if team_number not in TEAM_ROUTES:
        raise ValueError("Team number must be between 1 and 12.")

    route = dict(TEAM_ROUTES[team_number])
    route["team_number"] = team_number
    route["lens_content"] = LENSES[route["lens"]]
    route["evidence_results"] = ROUTE_EVIDENCE[route["code"]]
    return route


def get_evidence(route_code: str, evidence_id: str) -> dict[str, str]:
    """Resolve one team's selected evidence result."""
    try:
        return ROUTE_EVIDENCE[route_code][evidence_id]
    except KeyError as exc:
        raise ValueError(f"Evidence {evidence_id!r} is not valid for route {route_code!r}.") from exc


def assess_question(question: str) -> list[dict[str, str]]:
    """Return formative, non-scored coaching on an interview question."""
    text = " ".join(question.strip().split())
    lower = text.lower()
    feedback: list[dict[str, str]] = []

    if len(text) < 18:
        feedback.append(
            {
                "status": "revise",
                "title": "Make the question more testable",
                "message": "Name the process step, record, person, or period you want the process owner to explain.",
            }
        )

    if any(term in lower for term in ACCUSATORY_TERMS):
        feedback.append(
            {
                "status": "revise",
                "title": "The wording assumes the conclusion",
                "message": "Remove the accusation or intent claim. Ask for the sequence, condition, or record that would allow the explanation to be tested.",
            }
        )
    elif any(cue in lower for cue in NEUTRAL_CUES):
        feedback.append(
            {
                "status": "strong",
                "title": "Neutral opening",
                "message": "The wording invites a process explanation without accepting it as evidence.",
            }
        )
    else:
        feedback.append(
            {
                "status": "watch",
                "title": "Check the tone",
                "message": "A neutral opening such as “walk me through,” “which,” or “how” can reduce defensiveness while preserving the test.",
            }
        )

    if text.count("?") > 1:
        feedback.append(
            {
                "status": "revise",
                "title": "One question at a time",
                "message": "Stacked questions make it hard to know which point the response addresses. Lead with the highest-value question.",
            }
        )

    if any(cue in lower for cue in EVIDENCE_CUES):
        feedback.append(
            {
                "status": "strong",
                "title": "Evidence connection",
                "message": "The question points toward a record or event that could later corroborate the answer.",
            }
        )
    else:
        feedback.append(
            {
                "status": "watch",
                "title": "Predict the record",
                "message": "After listening, identify what record should exist if the explanation is accurate.",
            }
        )

    return feedback


def assess_risk_statement(statement: str) -> list[dict[str, str]]:
    """Check whether a final statement remains neutral, bounded, and actionable."""
    text = " ".join(statement.strip().split())
    lower = text.lower()
    feedback: list[dict[str, str]] = []

    if len(text) < 80:
        feedback.append(
            {
                "status": "revise",
                "title": "Add the unresolved condition",
                "message": "Connect the observed fact, what cannot yet be determined, and the evidence needed to decide.",
            }
        )

    if any(term in lower for term in ACCUSATORY_TERMS + ("management violated", "unsafe vehicles", "proved fraud")):
        feedback.append(
            {
                "status": "revise",
                "title": "The conclusion outruns the evidence",
                "message": "State the control or evidence uncertainty without asserting intent, population-wide failure, or an outcome not established by the route.",
            }
        )
    elif any(phrase in lower for phrase in ("cannot yet determine", "remains unresolved", "may account", "until we")):
        feedback.append(
            {
                "status": "strong",
                "title": "Uncertainty is stated precisely",
                "message": "The wording distinguishes a supportable interim conclusion from a final accusation.",
            }
        )
    else:
        feedback.append(
            {
                "status": "watch",
                "title": "Make the uncertainty explicit",
                "message": "Use wording such as “cannot yet determine” or “remains unresolved,” then identify the decision-relevant test.",
            }
        )

    if any(cue in lower for cue in EVIDENCE_CUES):
        feedback.append(
            {
                "status": "strong",
                "title": "Evidence is connected to the conclusion",
                "message": "The statement identifies a source capable of reducing the stated uncertainty.",
            }
        )
    else:
        feedback.append(
            {
                "status": "watch",
                "title": "Name the responsive source",
                "message": "Replace “more evidence” with a specific record, field, owner, and relevant period.",
            }
        )

    return feedback


def assess_evidence_request(request: str) -> list[dict[str, str]]:
    """Check specificity and responsiveness of a next-evidence request."""
    text = " ".join(request.strip().split())
    lower = text.lower()
    feedback: list[dict[str, str]] = []

    if any(cue in lower for cue in EVIDENCE_CUES):
        feedback.append(
            {
                "status": "strong",
                "title": "Specific source",
                "message": "The request identifies a record or data source rather than asking generally for support.",
            }
        )
    else:
        feedback.append(
            {
                "status": "revise",
                "title": "Specify the source",
                "message": "Name the record, system, field, owner, or data source that should be produced.",
            }
        )

    period_pattern = re.compile(r"\b(four[- ]week|sample|15|date|period|shift|from|through|between)\b")
    if period_pattern.search(lower):
        feedback.append(
            {
                "status": "strong",
                "title": "Bounded population or period",
                "message": "The request gives the evidence owner a usable scope.",
            }
        )
    else:
        feedback.append(
            {
                "status": "watch",
                "title": "Bound the request",
                "message": "Add the sample, population, date range, or shifts needed for the test.",
            }
        )

    return feedback


def pressure_feedback(choice_id: str, evidence_impact: str) -> dict[str, str]:
    """Return context-sensitive coaching for the team's response to pressure."""
    if choice_id not in PRESSURE_CHOICES:
        raise ValueError(f"Unknown pressure choice: {choice_id}")

    if choice_id == "narrow":
        return {
            "title": "Separate what moved from what remains",
            "message": (
                "This preserves connectivity without lowering the evidence threshold. "
                "Use the final statement to acknowledge supported context and isolate the unresolved condition."
            ),
        }
    if choice_id == "close":
        if evidence_impact == "decrease":
            detail = "The evidence supports part of the explanation, but check whether it resolves every original exception."
        else:
            detail = "The route evidence is mixed, adverse, or limited; closing now may treat inquiry or partial support as a complete test."
        return {"title": "Test the boundary before closing", "message": detail}

    if evidence_impact == "increase":
        detail = (
            "Escalation of a control exception may be proportionate, but avoid labeling intent or outcome before the relevant protocol threshold is met."
        )
    else:
        detail = (
            "Immediate escalation may outrun mixed or limited evidence. A narrower statement and targeted follow-up can preserve both urgency and fairness."
        )
    return {"title": "Calibrate the escalation", "message": detail}


def get_interpretation_choices(evidence_impact: str) -> dict[str, dict[str, str]]:
    """Return the three judgment options tied to an evidence result."""
    try:
        return INTERPRETATION_CHOICES[evidence_impact]
    except KeyError as exc:
        raise ValueError(f"Unknown evidence impact: {evidence_impact}") from exc


def prepared_evidence_ids(route: dict[str, Any], question_ids: list[str]) -> list[str]:
    """Return evidence sources the team's interview choices prepared it to interpret."""
    tactics = list(route["lens_content"]["question_tactics"])
    evidence_ids = list(route["lens_content"]["evidence_options"])
    prepared: list[str] = []
    for question_id in question_ids:
        if question_id not in tactics:
            raise ValueError(f"Unknown question tactic: {question_id}")
        evidence_id = evidence_ids[tactics.index(question_id)]
        if evidence_id not in prepared:
            prepared.append(evidence_id)
    return prepared


def interview_effect(question_ids: list[str]) -> dict[str, Any]:
    """Summarize how interview choices affected access and information yield."""
    effects = {
        "trace": {"yield": "High", "relationship": 1},
        "scope": {"yield": "Moderate", "relationship": 0},
        "challenge": {"yield": "Low", "relationship": -1},
    }
    score = 2
    for question_id in question_ids:
        if question_id not in effects:
            raise ValueError(f"Unknown question tactic: {question_id}")
        score += effects[question_id]["relationship"]

    if score >= 3:
        relationship = "Open"
    elif score == 2:
        relationship = "Stable"
    else:
        relationship = "Strained"

    latest_yield = effects[question_ids[-1]]["yield"] if question_ids else "Not tested"
    return {"relationship": relationship, "information_yield": latest_yield, "score": score}


def evidence_profile(route: dict[str, Any], evidence_id: str) -> dict[str, Any]:
    """Return the investigation cost and source strength for one evidence option."""
    evidence_ids = list(route["lens_content"]["evidence_options"])
    try:
        position = evidence_ids.index(evidence_id)
    except ValueError as exc:
        raise ValueError(f"Unknown evidence option: {evidence_id}") from exc

    profiles = (
        {
            "cost": 1,
            "strength": 3,
            "strength_label": "High",
            "source_type": "Direct source",
        },
        {
            "cost": 1,
            "strength": 2,
            "strength_label": "Moderate",
            "source_type": "Context source",
        },
        {
            "cost": 1,
            "strength": 1,
            "strength_label": "Limited",
            "source_type": "Indirect source",
        },
    )
    return profiles[position]


def aggregate_evidence_impact(evidence_history: list[dict[str, Any]]) -> str:
    """Combine multiple source results without averaging away conflicts."""
    impacts = {entry["impact"] for entry in evidence_history}
    if not impacts or impacts == {"limited"}:
        return "limited"
    if "mixed" in impacts or {"increase", "decrease"}.issubset(impacts):
        return "mixed"
    if "increase" in impacts:
        return "increase"
    if "decrease" in impacts:
        return "decrease"
    return "limited"


def strongest_evidence(evidence_history: list[dict[str, Any]]) -> dict[str, Any] | None:
    """Return the highest-strength source the team obtained."""
    if not evidence_history:
        return None
    return max(evidence_history, key=lambda entry: entry["strength"])


def build_aggregate_conclusion_choices(
    route: dict[str, Any], evidence_history: list[dict[str, Any]]
) -> dict[str, dict[str, str]]:
    """Build conclusion options from the complete evidence trail."""
    impact = aggregate_evidence_impact(evidence_history)
    anchor = strongest_evidence(evidence_history)
    if anchor is None:
        raise ValueError("At least one evidence result is required.")

    unresolved = UNRESOLVED_QUESTIONS[route["lens"]]
    if impact == "decrease":
        bridge = "This supports part of Marcus's explanation, but it does not resolve every original signal."
    elif impact == "increase":
        bridge = "This conflicts with part of Marcus's explanation, but it does not establish intent or every condition in the population."
    elif impact == "mixed":
        bridge = "Together, the sources explain some records while leaving others inconsistent or unsupported."
    else:
        bridge = "The available source is too limited to establish the relevant sequence or original record state."

    bounded = f"{anchor['result']} {bridge} We cannot yet determine {unresolved}."
    return {
        "bounded": {
            "label": bounded,
            "status": "strong",
            "feedback": "This statement anchors the judgment in the strongest source, preserves its boundary, and names the remaining decision question.",
        },
        "overclaim": {
            "label": "The evidence proves that management intentionally violated policy and that the entire override process failed.",
            "status": "revise",
            "feedback": "The statement asserts intent and population-wide failure beyond the evidence your team obtained.",
        },
        "vague": {
            "label": "Marcus's explanation may or may not be accurate. More evidence is needed.",
            "status": "revise",
            "feedback": "The statement does not identify the fact observed, the unresolved condition, or the decision that the next evidence must support.",
        },
    }


def takeaway_for_impact(evidence_impact: str) -> str:
    """Return the durable lesson for the evidence pattern a team encountered."""
    takeaways = {
        "mixed": "When evidence supports part of the story and conflicts with another part, narrow the conclusion by record—not by averaging the differences away.",
        "decrease": "Corroboration can reduce concern, but only for the claim and records the source actually tested.",
        "increase": "Conflicting evidence supports a control concern; it does not automatically establish intent.",
        "limited": "A weak source should change the next request, not the conclusion.",
    }
    try:
        return takeaways[evidence_impact]
    except KeyError as exc:
        raise ValueError(f"Unknown evidence impact: {evidence_impact}") from exc


def build_conclusion_choices(route: dict[str, Any], evidence_result: dict[str, str]) -> dict[str, dict[str, str]]:
    """Build three conclusion choices that directly incorporate the evidence seen."""
    unresolved = UNRESOLVED_QUESTIONS[route["lens"]]
    fact = evidence_result["result"]
    impact = evidence_result["impact"]

    if impact == "decrease":
        bridge = "This supports part of Marcus's explanation, but it does not resolve every original signal."
    elif impact == "increase":
        bridge = "This conflicts with part of Marcus's explanation, but it does not establish intent or every condition in the population."
    elif impact == "mixed":
        bridge = "This explains some records while leaving others inconsistent or unsupported."
    else:
        bridge = "This source is too limited to establish the relevant sequence or original record state."

    bounded = f"{fact} {bridge} We cannot yet determine {unresolved}."
    return {
        "bounded": {
            "label": bounded,
            "status": "strong",
            "feedback": "This statement uses the evidence you obtained, preserves its boundary, and names the remaining decision question.",
        },
        "overclaim": {
            "label": "The evidence proves that management intentionally violated policy and that the entire override process failed.",
            "status": "revise",
            "feedback": "The statement asserts intent and population-wide failure beyond the evidence your team obtained.",
        },
        "vague": {
            "label": "Marcus's explanation may or may not be accurate. More evidence is needed.",
            "status": "revise",
            "feedback": "The statement does not identify the fact observed, the unresolved condition, or the decision that the next evidence must support.",
        },
    }
