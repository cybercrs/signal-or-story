# Browser validation — 2026-10-10

Repository: `cybercrs/signal-or-story`. Source branch: `rollout/stlite-browser-navigation`. Static branch: `stlite-browser`. Baseline main: `023ba3fc460d7ade602fdf81f189d879b7a68fe5`.

| Check | Final result |
| --- | --- |
| Repository unit/AppTest suite including three navigation regressions | Passed: 26 |
| Browser entrypoint AppTest regressions | Passed: 3 |
| Actual Chromium/stlite/Wasm walkthrough | Passed: 11 checks |
| Pinned build and local asset integrity | Passed |
| Ruff 0.14.0 on new browser source/tests | Passed |
| Python compilation, loader JavaScript syntax and Git whitespace | Passed |
| Hosted HTTPS UI, physical device/browser matrix, classroom capacity | Not run |

Actual browser runtime: {"pyodide": "0.29.3", "python": "3.13.2", "streamlit": "1.57.0"}.

The complete browser walkthrough ran with external traffic blocked by a closed test proxy and local static files served under `/lesson/`. Final errors: zero console errors, zero page errors, zero external requests, zero HTTP asset errors. Review, future-view rejection, drafts, complete lessons, deliberate wrong selections/revisions, keyboard focus/Enter, 390-pixel rendering, reset, independent sessions, and intended refresh/bookmark behavior were exercised. Detailed checks and screenshots are committed under `review/`. The test harness adds diagnostic console state only to its HTTP test response; diagnostics are absent from the published app.

The investigation remains session-only. Refreshing, opening a bookmark, or closing the tab begins a new investigation. Browser navigation within the open session preserves the token budget, histories, route, and unfinished choices. The browser adapter renders the original forms as ordinary controls so unsubmitted selections can survive review navigation. Only the original submit actions spend tokens. It does not add central saving.

Source protection: `streamlit_app.py`, original case/engine/progress modules, `requirements.txt`, `.streamlit/`, and the original workflows remain byte-identical to baseline main. The only workflow added is isolated browser validation. Browser files and navigation tests are additive.

No final functional failure remains. Development test harness locator/timing corrections and any runtime compatibility adaptations are captured in the code; incomplete early runs are not represented as successful. Pages activation and hosted classroom-device checks remain outstanding. No classroom capacity claim is made.
