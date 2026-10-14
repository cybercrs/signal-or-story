# Signal or Story?

The final student-facing native app is published under `/js/`. The original Streamlit implementation and existing published root remain intact. Source branch: `rollout/native-browser`; static branch: `stlite-browser`. Native publication changes only `/js/`, without changing Pages settings or adding any storage service.

All twelve original team routes, interview responses, evidence, confidence boundaries and token costs are retained. Native calculations match 1,080 independent Python route/choice outcomes. The browser completed every route with deliberately weak pressure/judgment choices and both revisions, plus a two-question/two-source route with reserved mandatory actions. The original step display uses a native progress element. Zero-question evidence downgrading and token reserves are covered by engine tests.

Signal remains session-only. Refreshing, opening an old or native bookmark, or closing the tab starts fresh. No local storage, URL state saving or central service is added. Back/Forward within the open session preserve drafts, histories and earned progress. Earlier pages expose no mutation actions or new evidence.

Build with `python native/build.py`. Export original content with the repository's prepared interpreter using `python native/export.py`; Python is build/testing tooling only and is never loaded in the delivered app. Validate with the original repository suite, `node --test native/tests/*.test.mjs`, ESLint, and `python native/tests/browser.py` after building. See [VALIDATION.md](VALIDATION.md), [browser results](review/browser-results.json) and screenshots in `review/`.

The accepted Receivables reference is `a9dd736614db779b75389222ed8c251dc4d8db8f`. App-specific teaching changes were not copied.
