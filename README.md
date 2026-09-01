# Signal or Story? Evidence Under Pressure

A branching Streamlit activity in which student teams test a process-owner explanation through repeated choice, consequence, feedback, and revision loops.

## Classroom design

All teams begin with the same Vela Mobility evidence snapshot. The instructor assigns each team a unique number from 1 through 12. That number opens one of twelve routes across four audit lenses:

- dashboard logic;
- approval independence;
- maintenance and release timing; and
- post-review edits.

Within the assigned route, interview choices affect the process-owner response and prepare teams to interpret related evidence. All three evidence sources remain available, regardless of the questions asked, and teams may obtain up to two. A source requested without matching interview context returns a less informative result plus feedback about the understanding the team should have established first. Teams share one six-token investigation budget across questions, sources, the pressure response, and the final judgment. Every investigative action costs one token. Spending two optional tokens on a second question and second source preserves breadth but removes the capacity to revise both later decisions. Different routes can support different interim conclusions; the debrief compares the quality of the evidence logic rather than searching for one universal answer.

The app is designed for a 15-minute team activity followed by a 6-minute instructor-led debrief. It does not include quiz content.

## Student flow

1. Enter the instructor-assigned team number.
2. Read the Vela Mobility briefing, shared signals, and process-owner explanation.
3. Ask zero, one, or two fully worded interview questions at one token each. See each question's information and relationship effects, and decide how much process context is worth buying.
4. Choose up to two of the three available evidence sources. Compare each predicted pattern with the result, notice when missing interview context limits usefulness, and decide whether another source is worth the revision capacity it consumes.
5. Spend one token to respond to stakeholder pressure, see the consequence, and decide whether replacing the response is worth another token.
6. Spend one token to test a route-specific interim conclusion and next evidence request, then decide whether a second—and final—selection is worth the last available token.
7. Review the evidence trail and route-specific takeaway.

The app contains no free-text fields and collects no student names. Choices remain in the team's browser memory and disappear when the session is reset or closes.

## Visual direction

The interface is an audit evidence room: warm paper, dark ink, amber signals, teal evidence cards, orange pressure moments, route markers, and a checkpoint-based rhythm that connects visually to the Vela Mobility presentation.

## Run locally

Python 3.11 or 3.12 is recommended.

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
streamlit run streamlit_app.py
```

## Check the project

```bash
python -m py_compile streamlit_app.py case_content.py case_logic.py
python -m unittest discover -s tests -v
```

The included GitHub Actions workflow runs both checks on pushes and pull requests.

## Publish through GitHub and Streamlit Community Cloud

1. Create an empty GitHub repository.
2. Push this folder's `main` branch to that repository.
3. In Streamlit Community Cloud, create an app from the repository.
4. Select `main` and set the entrypoint to `streamlit_app.py`.
5. After deployment, test one complete route before sharing the URL or QR code with students.

No secrets, database, or external service configuration is required.

## File guide

- `streamlit_app.py` — student interface and stage flow.
- `case_content.py` — shared facts, team routes, evidence, and pressure prompts.
- `case_logic.py` — route resolution, question-to-evidence preparation, evidence aggregation, feedback, and takeaway logic.
- `tests/test_case_logic.py` — structural and coaching checks.
- `.streamlit/config.toml` — app palette and browser settings.
- `.github/workflows/ci.yml` — GitHub validation workflow.

## Source basis

The fictional Vela Mobility case adapts the existing “Signal or Story? Evidence Under Pressure” activity and Chapter 01 principles concerning inquiry, corroboration, professional judgment, objectivity, the five Cs, curiosity, communication, and professional courage.
