"""Signal or Story: an interactive team investigation for assurance students."""

from __future__ import annotations

import streamlit as st
import streamlit.components.v1 as components

from case_content import (
    COMMON_EVIDENCE,
    EVIDENCE_GUIDANCE,
    FOLLOW_UP_OPTIONS,
    PRESSURE_CHOICES,
    PROCESS_OWNER_EXPLANATION,
    SCENARIO_BRIEF,
)
from case_logic import (
    ACTION_COSTS,
    TOTAL_INVESTIGATION_TOKENS,
    aggregate_evidence_impact,
    build_aggregate_conclusion_choices,
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


st.set_page_config(
    page_title="Signal or Story?",
    page_icon="🔎",
    layout="wide",
    initial_sidebar_state="collapsed",
)


APP_CSS = """
<style>
    :root {
        --ink: #13201c;
        --paper: #f7f3e9;
        --amber-deep: #875600;
        --teal: #2f786f;
        --teal-deep: #174e49;
        --orange: #d86736;
        --line: #b8c9c1;
    }

    .stApp {
        background:
            linear-gradient(rgba(247, 243, 233, 0.96), rgba(247, 243, 233, 0.96)),
            repeating-linear-gradient(0deg, transparent, transparent 31px, rgba(47,120,111,.08) 32px);
        color: var(--ink);
    }

    header[data-testid="stHeader"] {
        background: rgba(247, 243, 233, .98);
    }

    section[data-testid="stMain"] { overflow-anchor: none; }

    .block-container {
        max-width: 1120px;
        padding-top: 10.7rem;
        padding-bottom: 3rem;
    }

    h1, h2, h3 {
        color: var(--ink) !important;
        letter-spacing: -0.025em;
    }

    .case-header {
        position: fixed;
        top: 3.55rem;
        left: 0;
        right: 0;
        z-index: 990;
        background: rgba(247, 243, 233, .98);
        border-bottom: 1px solid var(--line);
        box-shadow: 0 7px 20px rgba(19, 32, 28, .08);
        backdrop-filter: blur(10px);
    }

    .case-header-inner {
        max-width: 1120px;
        min-height: 6rem;
        margin: 0 auto;
        padding: .72rem 1rem .78rem 1rem;
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 1.4rem;
    }

    .case-kicker {
        color: var(--amber-deep);
        font-size: .72rem;
        font-weight: 850;
        letter-spacing: .14em;
        line-height: 1.25;
        text-transform: uppercase;
        margin-bottom: .18rem;
    }

    .case-title {
        color: var(--ink);
        font-size: clamp(2rem, 4vw, 2.75rem);
        font-weight: 875;
        letter-spacing: -.045em;
        line-height: 1;
        margin: 0;
    }

    .case-subtitle {
        color: #385048;
        font-size: .92rem;
        font-weight: 650;
        line-height: 1.3;
        text-align: right;
        max-width: 390px;
    }

    .route-code {
        display: inline-block;
        background: var(--teal-deep);
        color: white;
        border-radius: 999px;
        padding: .28rem .68rem;
        margin-bottom: .24rem;
        font-size: .78rem;
        font-weight: 850;
        letter-spacing: .08em;
    }

    .budget-pill {
        display: inline-block;
        background: #ffcc55;
        color: #4f3500;
        border-radius: 999px;
        padding: .28rem .68rem;
        margin: 0 0 .24rem .35rem;
        font-size: .78rem;
        font-weight: 850;
        letter-spacing: .05em;
    }

    .takeaway-card {
        border-radius: 12px;
        padding: 1.15rem 1.25rem;
        margin: .8rem 0 1.15rem 0;
        line-height: 1.55;
        background: var(--ink);
        color: #f9f6ee;
        border-left: 8px solid #ffcc55;
        font-size: 1.12rem;
    }

    .takeaway-card strong { color: #ffcc55; }

    .card-label {
        color: var(--teal-deep);
        font-size: .76rem;
        font-weight: 850;
        letter-spacing: .1em;
        text-transform: uppercase;
        margin-bottom: .42rem;
    }

    .instruction-card, .case-file, .exchange-card, .source-card, .judgment-card {
        background: rgba(255,255,255,.76);
        border: 1px solid var(--line);
        border-radius: 13px;
        padding: 1.2rem 1.3rem;
        margin: .8rem 0 1.25rem 0;
        line-height: 1.52;
        box-shadow: 0 5px 16px rgba(19,32,28,.05);
    }

    .instruction-card {
        background: #fffaf0;
        border-color: #ddc77e;
        border-left: 8px solid var(--amber-deep);
    }

    .instruction-card ol { margin: .45rem 0 .5rem 1.15rem; padding: 0; }
    .instruction-card li { margin-bottom: .55rem; padding-left: .2rem; }

    .case-file { border-left: 8px solid var(--amber-deep); }
    .case-section + .case-section {
        border-top: 1px solid #d7ddd8;
        margin-top: 1rem;
        padding-top: 1rem;
    }

    .signal-grid {
        display: grid;
        grid-template-columns: repeat(2, minmax(0, 1fr));
        gap: .75rem;
        margin-top: .65rem;
    }

    .signal-item {
        background: #fffaf0;
        border: 1px solid #e4d5a5;
        border-radius: 9px;
        padding: .8rem .9rem;
    }

    .owner-quote {
        background: var(--ink);
        color: #f9f6ee;
        border-radius: 10px;
        padding: 1rem 1.1rem;
        font-size: 1.08rem;
    }

    .exchange-card { border-left: 8px solid var(--teal); }
    .exchange-section + .exchange-section,
    .judgment-section + .judgment-section {
        border-top: 1px solid #d7ddd8;
        margin-top: .8rem;
        padding-top: .8rem;
    }

    .source-card { border-left: 8px solid var(--teal); }
    .source-meta { color: #536860; font-size: .88rem; margin-bottom: .75rem; }
    .source-section + .source-section {
        border-top: 1px solid #d7ddd8;
        margin-top: .8rem;
        padding-top: .8rem;
    }

    .feedback-line {
        border-radius: 8px;
        margin-top: .8rem;
        padding: .72rem .82rem;
    }

    .feedback-line.strong { background: #e5f1ec; color: var(--teal-deep); }
    .feedback-line.neutral { background: #edf2f0; color: #385048; }
    .feedback-line.watch { background: #fff0e9; color: #7b3416; }

    .judgment-card { border-left: 8px solid var(--orange); }

    .loop-strip {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: .55rem;
        margin: .8rem 0 1.2rem 0;
    }

    .loop-step {
        background: rgba(255,255,255,.72);
        border: 1px solid var(--line);
        border-radius: 9px;
        padding: .65rem .75rem;
        color: #385048;
        font-size: .83rem;
        font-weight: 750;
        text-align: center;
    }

    .small-note {
        color: #536860;
        font-size: .9rem;
        line-height: 1.45;
    }

    div[data-testid="stForm"] {
        background: rgba(255,255,255,.58);
        border: 1px solid var(--line);
        border-radius: 14px;
        padding: 1rem 1.1rem .35rem 1.1rem;
    }

    div[data-testid="stRadio"] label { align-items: flex-start; }
    div[data-testid="stRadio"] p { line-height: 1.42; }
    iframe[data-testid="stIFrame"] {
        position: absolute;
        width: 0 !important;
        height: 0 !important;
        min-height: 0 !important;
        border: 0;
    }
    div[data-testid="stElementContainer"]:has(iframe[data-testid="stIFrame"]) {
        height: 0 !important;
        min-height: 0 !important;
        margin: 0 !important;
        overflow: hidden;
    }
    div.stButton > button, div[data-testid="stFormSubmitButton"] > button {
        min-height: 3rem;
        border-radius: 8px;
        font-weight: 800;
    }

    @media (max-width: 760px) {
        .block-container { padding-top: 12.7rem; }
        .case-header-inner {
            min-height: 8rem;
            align-items: flex-start;
            flex-direction: column;
            gap: .4rem;
        }
        .case-subtitle { text-align: left; max-width: 100%; }
        .loop-strip { grid-template-columns: repeat(2, 1fr); }
        .signal-grid { grid-template-columns: 1fr; }
    }
</style>
"""

st.markdown(APP_CSS, unsafe_allow_html=True)


def initialize_state() -> None:
    defaults = {
        "stage": 0,
        "route": None,
        "question_history": [],
        "asking_follow_up": False,
        "evidence_history": [],
        "investigation_budget": TOTAL_INVESTIGATION_TOKENS,
        "budget_history": [],
        "pressure_history": [],
        "revising_pressure": False,
        "conclusion_history": [],
        "revising_conclusion": False,
        "scroll_pending": True,
        "scroll_request_id": 0,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value.copy() if isinstance(value, list) else value


def reset_activity() -> None:
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.rerun()


def advance_to(stage: int) -> None:
    st.session_state.stage = stage
    st.session_state.scroll_pending = True
    st.session_state.scroll_request_id += 1
    st.rerun()


def spend_token(action_id: str, label: str) -> bool:
    """Spend one investigation token and record where it went."""
    cost = ACTION_COSTS[action_id]
    if st.session_state.investigation_budget < cost:
        return False
    st.session_state.investigation_budget -= cost
    st.session_state.budget_history = st.session_state.budget_history + [
        {"action_id": action_id, "label": label, "cost": cost}
    ]
    return True


def scroll_to_top(request_id: int) -> None:
    script = """<script>
        const scrollRequestId = "__SCROLL_REQUEST_ID__";
        const scroller = window.parent.document.querySelector('section[data-testid="stMain"]');
        const parentDocument = window.parent.document;
        let cancelledByStudent = false;
        let resetTimer;

        const cleanup = () => {
            if (scroller) {
                scroller.removeEventListener('wheel', cancelReset, true);
                scroller.removeEventListener('touchstart', cancelReset, true);
            }
            parentDocument.removeEventListener('keydown', cancelForScrollKey, true);
        };
        const cancelReset = () => {
            cancelledByStudent = true;
            window.clearTimeout(resetTimer);
            cleanup();
        };
        const cancelForScrollKey = (event) => {
            if (["ArrowDown", "ArrowUp", "PageDown", "PageUp", "Home", "End", " "].includes(event.key)) {
                cancelReset();
            }
        };

        if (scroller) {
            scroller.addEventListener('wheel', cancelReset, {once: true, passive: true, capture: true});
            scroller.addEventListener('touchstart', cancelReset, {once: true, passive: true, capture: true});
        }
        parentDocument.addEventListener('keydown', cancelForScrollKey, {capture: true});

        window.requestAnimationFrame(() => window.requestAnimationFrame(() => {
            resetTimer = window.setTimeout(() => {
                if (!cancelledByStudent && scroller) {
                    scroller.scrollTo({top: 0, left: 0, behavior: 'auto'});
                }
                cleanup();
            }, 90);
        }));
        window.setTimeout(() => {
            window.clearTimeout(resetTimer);
            cleanup();
        }, 500);
        </script>""".replace("__SCROLL_REQUEST_ID__", str(request_id))
    components.html(
        script,
        height=0,
        width=0,
    )


def render_header() -> None:
    if st.session_state.route:
        route = st.session_state.route
        remaining = st.session_state.investigation_budget
        context = (
            f'<span class="route-code">TEAM {route["team_number"]:02d}</span>'
            f'<span class="budget-pill">{remaining} OF {TOTAL_INVESTIGATION_TOKENS} TOKENS LEFT</span><br>'
            f'Assigned focus · {route["lens_content"]["title"]}'
        )
    else:
        context = "A team investigation in inquiry, evidence, and judgment"

    st.markdown(
        '<div class="case-header"><div class="case-header-inner">'
        '<div><div class="case-kicker">Vela Mobility · Evidence Room</div>'
        '<div class="case-title">Signal or Story?</div></div>'
        f'<div class="case-subtitle">{context}</div>'
        '</div></div>',
        unsafe_allow_html=True,
    )


def render_progress() -> None:
    stage = st.session_state.stage
    labels = ["Setup", "Case brief", "Interview", "Evidence", "Pressure", "Judgment", "Takeaway"]
    st.progress(stage / 6, text=f"Step {stage + 1} of 7 · {labels[stage]}")


def interview_consequence(question_id: str) -> str:
    consequences = {
        "trace": "Marcus provides a testable sequence. The relationship opens.",
        "scope": "Marcus defines part of the boundary but cannot reconcile it. The relationship remains stable.",
        "challenge": "The accusation produces little detail and strains the relationship.",
    }
    return consequences[question_id]


def pressure_consequence(choice_id: str, impact: str) -> str:
    if choice_id == "narrow":
        return "Marcus agrees to preserve the requested records. Your team keeps access while clearly defining what remains open."
    if choice_id == "close":
        return "The issue is removed from active testing even though the original signals are not fully resolved. Your evidence trail will have to defend that boundary."
    if impact == "increase":
        return "Leadership opens a formal review. Marcus routes further requests through a designated contact, slowing access but preserving the issue."
    return "Leadership opens a formal review, but your team must now defend why the current mixed or limited evidence justified that escalation."


def render_evidence_entry(entry: dict[str, object], number: int) -> None:
    interpretation = get_interpretation_choices(str(entry["impact"]))["bounded"]
    preparation_html = ""
    if not entry.get("prepared", True):
        preparation_html = (
            f'<div class="feedback-line watch"><strong>Why this result is less useful</strong><br>'
            f'{entry.get("preparation_note", "")}</div>'
        )
    st.markdown(
        f'<div class="source-card">'
        f'<div class="card-label">Source {number} · Evidence result</div>'
        f'<strong>{entry["label"]}</strong>'
        f'<div class="source-meta">{entry["source_type"]} · '
        f'{entry.get("usefulness_label", entry["strength_label"] + " usefulness")} · '
        f'1 investigation token</div>'
        f'<div class="source-section"><strong>Expected if Marcus is accurate</strong><br>{entry["prediction"]}</div>'
        f'<div class="source-section"><strong>What the source shows</strong><br>{entry["result"]}</div>'
        f'{preparation_html}'
        f'<div class="feedback-line strong"><strong>What this changes</strong><br>{interpretation["feedback"]}</div>'
        f'</div>',
        unsafe_allow_html=True,
    )


def stage_setup() -> None:
    st.markdown("## Enter the evidence room")
    st.write(
        "Enter the team number you were assigned. Your number opens one audit lead and a route-specific evidence pattern."
    )
    st.markdown(
        """<div class="instruction-card">
        <div class="card-label">Your six-token investigation budget</div>
        <strong>Every investigative action costs one token:</strong> each interview question, each evidence source, your first pressure response, a pressure-response revision, your first judgment test, and a judgment revision. Reading and moving between steps cost nothing.
        <ol>
          <li><strong>Interview:</strong> you may ask zero, one, or two questions. Each costs one token and gives you context for interpreting one type of evidence.</li>
          <li><strong>Evidence:</strong> all three sources are available, and you may obtain up to two. Each costs one token. If a source does not connect to a question you asked, the result will be less useful because you did not first establish how to interpret it.</li>
          <li><strong>Pressure:</strong> your first response costs one token. <strong>Revise your response once</strong> costs another token and replaces that response after you see its consequence.</li>
          <li><strong>Judgment:</strong> your first conclusion-and-request test costs one token. <strong>Revise your judgment once</strong> costs another token; that second selection is final.</li>
        </ol>
        <strong>You cannot do everything.</strong> A second question plus a second source uses the two tokens that could fund both later revisions. Questions do not restrict which evidence you may request; they determine how useful the response will be. The app preserves enough tokens for one source, one pressure response, and one judgment. Leaving a step locks that part of the path; “Start over” resets the investigation.
        </div>""",
        unsafe_allow_html=True,
    )

    with st.form("setup_form"):
        team_number = st.number_input(
            "Your assigned team number",
            min_value=1,
            max_value=12,
            value=1,
            step=1,
        )
        submitted = st.form_submit_button("Open your case", type="primary", use_container_width=True)

    if submitted:
        st.session_state.route = get_route(int(team_number))
        advance_to(1)


def stage_briefing() -> None:
    st.markdown("## Why your team is here")
    signal_items = "".join(
        f'<div class="signal-item"><div class="card-label">{label}</div>{fact}</div>'
        for label, fact in COMMON_EVIDENCE
    )
    st.markdown(
        f'<div class="case-file">'
        f'<div class="case-section"><div class="card-label">Your assignment</div>{SCENARIO_BRIEF}</div>'
        f'<div class="case-section"><div class="card-label">Signals from the first three weeks</div>'
        f'Read these as conditions requiring explanation—not as proof of one story.'
        f'<div class="signal-grid">{signal_items}</div></div>'
        f'<div class="case-section"><div class="card-label">Marcus Hale explains</div>'
        f'<div class="owner-quote">“{PROCESS_OWNER_EXPLANATION}”</div></div>'
        f'</div>',
        unsafe_allow_html=True,
    )
    st.write(
        "Your task is to find out which parts of that explanation the records can support, which parts they contradict, and what remains unresolved."
    )
    if st.button("Begin the interview", type="primary", use_container_width=True):
        advance_to(2)


def stage_interview() -> None:
    route = st.session_state.route
    lens = route["lens_content"]
    tactics = lens["question_tactics"]
    history = st.session_state.question_history

    st.markdown(f"## Interview lead: {lens['title']}")
    st.write(lens["brief"])
    st.caption("Cost: 1 token per question. You may ask zero, one, or two. Questions prepare you to interpret related evidence; they do not restrict which sources you may request.")
    st.markdown(
        '<div class="loop-strip"><div class="loop-step">Ask</div><div class="loop-step">Hear</div>'
        '<div class="loop-step">See the effect</div><div class="loop-step">Adapt</div></div>',
        unsafe_allow_html=True,
    )

    for index, entry in enumerate(history, start=1):
        tactic = tactics[entry["id"]]
        evidence_option = lens["evidence_options"][entry["prepared_evidence_id"]]
        effect = interview_effect([entry["id"]])
        message = (
            f'{interview_consequence(entry["id"])} This gives you context for: {evidence_option["label"]}. '
            f'Information yield: {effect["information_yield"]}.'
        )
        feedback_class = {"trace": "strong", "scope": "neutral", "challenge": "watch"}[entry["id"]]
        st.markdown(
            f'<div class="exchange-card">'
            f'<div class="card-label">Question {index} · Interview exchange</div>'
            f'<div class="exchange-section"><strong>You asked</strong><br>{tactic["prompt"]}</div>'
            f'<div class="exchange-section"><strong>Marcus answered</strong><br>{tactic["response"]}</div>'
            f'<div class="feedback-line {feedback_class}"><strong>Effect on the investigation</strong><br>{message}</div>'
            f'</div>',
            unsafe_allow_html=True,
        )

    asking = not history or st.session_state.asking_follow_up
    if asking:
        used = {entry["id"] for entry in history}
        available = [question_id for question_id in tactics if question_id not in used]
        prompt = "Which question will you ask Marcus?" if not history else "Which follow-up will you ask?"
        with st.form(f"interview_form_{len(history)}"):
            tactic_id = st.radio(
                prompt,
                available,
                format_func=lambda item: f'{tactics[item]["label"]} — “{tactics[item]["prompt"]}”',
                index=None,
            )
            submitted = st.form_submit_button(
                "Ask the selected question · 1 token", type="primary", use_container_width=True
            )

        if submitted:
            if tactic_id is None:
                st.error("Select one question before continuing.")
            elif not can_afford_action(
                st.session_state.investigation_budget, "interview_question", reserve=3
            ):
                st.error("This question would use a token reserved for the required evidence, response, or judgment.")
            else:
                evidence_id = prepared_evidence_ids(route, [tactic_id])[0]
                spend_token(
                    "interview_question",
                    "Follow-up interview question" if history else "Initial interview question",
                )
                st.session_state.question_history = history + [
                    {"id": tactic_id, "prepared_evidence_id": evidence_id}
                ]
                st.session_state.asking_follow_up = False
                st.rerun()

        if not history:
            st.caption("You may skip the interview, but evidence requested without process context will be less useful.")
            if st.button("Skip questions and move to evidence", use_container_width=True):
                advance_to(3)
    else:
        st.caption(
            f'You have built context for {len(history)} evidence source(s). Ask one follow-up to prepare another source, or continue.'
        )
        left, right = st.columns(2)
        with left:
            if len(history) == 1 and can_afford_action(
                st.session_state.investigation_budget, "interview_question", reserve=3
            ):
                if st.button("Choose one follow-up question · 1 token", use_container_width=True):
                    st.session_state.asking_follow_up = True
                    st.rerun()
            elif len(history) == 1:
                st.caption("No follow-up is available because three tokens must remain for evidence, response, and judgment.")
        with right:
            if st.button("Move to evidence", type="primary", use_container_width=True):
                advance_to(3)


def stage_evidence() -> None:
    route = st.session_state.route
    lens = route["lens_content"]
    guidance = EVIDENCE_GUIDANCE[route["lens"]]
    history = st.session_state.evidence_history
    question_ids = [entry["id"] for entry in st.session_state.question_history]
    prepared = set(prepared_evidence_ids(route, question_ids))

    st.markdown("## Decide what evidence is worth the token")
    st.write(
        "All three sources are available. You may obtain up to two, and each costs one token. Evidence connected to your interview questions will be more useful because you established how to interpret it."
    )
    metric_left, metric_right = st.columns(2)
    metric_left.metric("Sources available", len(lens["evidence_options"]))
    metric_right.metric("Sources prepared by your interview", len(prepared))

    for index, entry in enumerate(history, start=1):
        render_evidence_entry(entry, index)

    used = {entry["id"] for entry in history}
    available = [
        evidence_id
        for evidence_id in lens["evidence_options"]
        if evidence_id not in used
        and len(history) < 2
        and can_afford_action(st.session_state.investigation_budget, "evidence_source", reserve=2)
    ]

    if available:
        with st.form(f"evidence_form_{len(history)}"):
            evidence_id = st.radio(
                "Which source will you obtain?",
                available,
                format_func=lambda item: (
                    f'{evidence_profile(route, item)["source_type"]} · '
                    f'1 investigation token — '
                    f'{lens["evidence_options"][item]["label"]}. '
                    f'{"Interview context established" if item in prepared else "No matching interview context"}. '
                    f'Expected if Marcus is accurate: {guidance[item]["prediction"]}'
                ),
                index=None,
            )
            submitted = st.form_submit_button(
                "Obtain selected source · 1 token", type="primary", use_container_width=True
            )

        if submitted:
            if evidence_id is None:
                st.error("Select one evidence source before continuing.")
            elif not can_afford_action(
                st.session_state.investigation_budget, "evidence_source", reserve=2
            ):
                st.error("Two tokens must remain for the required pressure response and judgment.")
            else:
                option = lens["evidence_options"][evidence_id]
                route_result = get_evidence(route["code"], evidence_id)
                profile = evidence_profile(route, evidence_id)
                is_prepared = evidence_id in prepared
                if is_prepared:
                    result_text = route_result["result"]
                    result_impact = route_result["impact"]
                    preparation_note = ""
                    usefulness_label = f'{profile["strength_label"]} usefulness'
                else:
                    result_text = guidance[evidence_id]["without_context"]
                    result_impact = "limited"
                    profile["strength"] = 1
                    profile["strength_label"] = "Limited"
                    usefulness_label = "Limited usefulness without interview context"
                    preparation_note = (
                        "You requested this source before first asking: “"
                        f'{guidance[evidence_id]["preparation_prompt"]}” '
                        "That process understanding would have made the evidence more useful. "
                        "Treat this result as a lead rather than a basis for moving confidence."
                    )
                entry = {
                    "id": evidence_id,
                    "label": option["label"],
                    "request": option["request"],
                    "prediction": guidance[evidence_id]["prediction"],
                    "why": guidance[evidence_id]["why"],
                    "result": result_text,
                    "impact": result_impact,
                    "prepared": is_prepared,
                    "preparation_note": preparation_note,
                    "usefulness_label": usefulness_label,
                    **profile,
                }
                st.session_state.evidence_history = history + [entry]
                spend_token("evidence_source", f'Evidence source: {option["label"]}')
                st.rerun()
    elif len(history) >= 2:
        st.info("You have reached the two-source limit.")
    else:
        st.info("Your remaining tokens are reserved for the required pressure response and judgment.")

    if history:
        st.caption(
            "You may obtain one additional source or preserve the token for a later revision."
        )
        if st.button("Move to the pressure decision", type="primary", use_container_width=True):
            advance_to(4)


def stage_pressure() -> None:
    route = st.session_state.route
    lens = route["lens_content"]
    impact = aggregate_evidence_impact(st.session_state.evidence_history)
    history = st.session_state.pressure_history

    st.markdown("## Pressure enters the room")
    st.caption("Cost: 1 token for your first response. Replacing it after feedback costs 1 additional token.")
    response_html = ""
    if history:
        latest = history[-1]
        choice = PRESSURE_CHOICES[latest["choice_id"]]
        coach = latest["feedback"]
        feedback_class = "strong" if latest["choice_id"] == "narrow" else "watch"
        response_html = (
            f'<div class="judgment-section"><strong>Your response</strong><br>'
            f'{choice["label"]} — {choice["stance"]}</div>'
            f'<div class="feedback-line {feedback_class}"><strong>{coach["title"]}</strong><br>'
            f'{coach["message"]}</div>'
            f'<div class="judgment-section"><strong>Consequence</strong><br>{latest["consequence"]}</div>'
        )
    st.markdown(
        f'<div class="judgment-card"><div class="card-label">Management pressure</div>'
        f'<div class="judgment-section">{lens["pressure"]}</div>{response_html}</div>',
        unsafe_allow_html=True,
    )

    if not history or st.session_state.revising_pressure:
        options = list(PRESSURE_CHOICES)
        if st.session_state.revising_pressure and history:
            options = [choice_id for choice_id in options if choice_id != history[-1]["choice_id"]]
        with st.form(f"pressure_form_{len(history)}"):
            pressure_choice = st.radio(
                "How will your team respond?",
                options,
                format_func=lambda item: f'{PRESSURE_CHOICES[item]["label"]} — {PRESSURE_CHOICES[item]["stance"]}',
                index=None,
            )
            action_id = "pressure_revision" if history else "pressure_response"
            submit_label = "Commit revised response · 1 token" if history else "Commit response · 1 token"
            submitted = st.form_submit_button(submit_label, type="primary", use_container_width=True)

        if submitted:
            if pressure_choice is None:
                st.error("Choose a response before continuing.")
            elif not can_afford_action(
                st.session_state.investigation_budget, action_id, reserve=1
            ):
                st.error("One token must remain for the required judgment.")
            else:
                entry = {
                    "choice_id": pressure_choice,
                    "feedback": pressure_feedback(pressure_choice, impact),
                    "consequence": pressure_consequence(pressure_choice, impact),
                }
                st.session_state.pressure_history = history + [entry]
                spend_token(
                    action_id,
                    "Pressure-response revision" if history else "Initial pressure response",
                )
                st.session_state.revising_pressure = False
                st.rerun()
    else:
        left, right = st.columns(2)
        with left:
            if len(history) == 1 and can_afford_action(
                st.session_state.investigation_budget, "pressure_revision", reserve=1
            ):
                if st.button("Revise your response once · 1 token", use_container_width=True):
                    st.session_state.revising_pressure = True
                    st.rerun()
            elif len(history) == 1:
                st.caption("No response revision is available because your final token is reserved for judgment.")
        with right:
            if st.button("Keep response and shape the conclusion", type="primary", use_container_width=True):
                advance_to(5)


def stage_conclusion() -> None:
    route = st.session_state.route
    conclusion_choices = build_aggregate_conclusion_choices(route, st.session_state.evidence_history)
    follow_up_options = FOLLOW_UP_OPTIONS[route["lens"]]
    history = st.session_state.conclusion_history

    st.markdown("## Make the conclusion earn its confidence")
    st.write(
        "Choose an interim conclusion and the next source that would reduce its remaining uncertainty. You will see feedback before the decision becomes final."
    )
    st.caption("Cost: 1 token for the first judgment test. A second-and-final selection costs 1 additional token.")

    if history:
        latest = history[-1]
        conclusion = conclusion_choices[latest["conclusion_id"]]
        follow_up = follow_up_options[latest["follow_up_id"]]
        conclusion_class = "strong" if conclusion["status"] == "strong" else "watch"
        follow_up_class = "strong" if follow_up["status"] == "strong" else "watch"
        st.markdown(
            f'<div class="judgment-card"><div class="card-label">Judgment feedback</div>'
            f'<div class="judgment-section"><strong>Your interim conclusion</strong><br>{conclusion["label"]}'
            f'<div class="feedback-line {conclusion_class}">{conclusion["feedback"]}</div></div>'
            f'<div class="judgment-section"><strong>Your next request</strong><br>{follow_up["request"]}'
            f'<div class="feedback-line {follow_up_class}">{follow_up["feedback"]}</div></div>'
            f'</div>',
            unsafe_allow_html=True,
        )

    if not history or st.session_state.revising_conclusion:
        with st.form(f"conclusion_form_{len(history)}"):
            conclusion_id = st.radio(
                "Which interim conclusion stays within the evidence?",
                list(conclusion_choices),
                format_func=lambda item: conclusion_choices[item]["label"],
                index=None,
            )
            follow_up_id = st.radio(
                "Which next request best reduces the remaining uncertainty?",
                list(follow_up_options),
                format_func=lambda item: f'{follow_up_options[item]["label"]} — {follow_up_options[item]["request"]}',
                index=None,
            )
            action_id = "judgment_revision" if history else "judgment_test"
            submit_label = "Test revised judgment · 1 token" if history else "Test this judgment · 1 token"
            submitted = st.form_submit_button(submit_label, type="primary", use_container_width=True)

        if submitted:
            if conclusion_id is None or follow_up_id is None:
                st.error("Select both a conclusion and a next evidence request.")
            elif not can_afford_action(st.session_state.investigation_budget, action_id):
                st.error("No investigation token remains for this judgment.")
            else:
                st.session_state.conclusion_history = history + [
                    {"conclusion_id": conclusion_id, "follow_up_id": follow_up_id}
                ]
                spend_token(
                    action_id,
                    "Judgment revision" if history else "Initial judgment test",
                )
                st.session_state.revising_conclusion = False
                st.rerun()
    else:
        latest = history[-1]
        conclusion = conclusion_choices[latest["conclusion_id"]]
        follow_up = follow_up_options[latest["follow_up_id"]]
        needs_revision = conclusion["status"] != "strong" or follow_up["status"] != "strong"
        left, right = st.columns(2)
        with left:
            if len(history) == 1 and can_afford_action(
                st.session_state.investigation_budget, "judgment_revision"
            ):
                revise_label = "Revise your judgment once · 1 token"
                if st.button(revise_label, use_container_width=True):
                    st.session_state.revising_conclusion = True
                    st.rerun()
            elif len(history) == 1:
                st.caption("No token remains for a judgment revision.")
        with right:
            continue_label = "Keep this judgment" if needs_revision else "See what your investigation changed"
            if st.button(continue_label, type="primary", use_container_width=True):
                advance_to(6)


def stage_takeaway() -> None:
    impact = aggregate_evidence_impact(st.session_state.evidence_history)

    st.markdown("## What your investigation revealed")
    metric_1, metric_2, metric_3 = st.columns(3)
    metric_1.metric("Questions asked", len(st.session_state.question_history))
    metric_2.metric("Sources obtained", len(st.session_state.evidence_history))
    metric_3.metric(
        "Investigation tokens used",
        f'{TOTAL_INVESTIGATION_TOKENS - st.session_state.investigation_budget} of {TOTAL_INVESTIGATION_TOKENS}',
    )

    st.caption(
        "Budget path: " + " → ".join(entry["label"] for entry in st.session_state.budget_history)
    )

    st.markdown("### Your evidence trail")
    for index, entry in enumerate(st.session_state.evidence_history, start=1):
        render_evidence_entry(entry, index)

    st.markdown(
        f'<div class="takeaway-card"><strong>Your route-specific takeaway</strong><br>'
        f'{takeaway_for_impact(impact)}<br><br>'
        '<strong>The larger lesson</strong><br>Interview quality changes what you can learn. '
        'Evidence quality changes what you can conclude.</div>',
        unsafe_allow_html=True,
    )


initialize_state()
render_header()
render_progress()

stage_renderers = {
    0: stage_setup,
    1: stage_briefing,
    2: stage_interview,
    3: stage_evidence,
    4: stage_pressure,
    5: stage_conclusion,
    6: stage_takeaway,
}
stage_renderers[st.session_state.stage]()

st.divider()
left, right = st.columns([3, 1])
with left:
    st.markdown(
        "<div class='small-note'>Your choices remain only in this browser session. “Start over” resets the entire investigation.</div>",
        unsafe_allow_html=True,
    )
with right:
    if st.session_state.stage > 0:
        st.button("Start over", on_click=reset_activity, use_container_width=True)

if st.session_state.scroll_pending:
    st.session_state.scroll_pending = False
    scroll_to_top(st.session_state.scroll_request_id)
