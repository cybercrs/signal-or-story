from playwright.sync_api import expect


def lesson(page, click, choose, select, idle, check, results, readonly):
    def pick(index=0):
        page.get_by_role("radio").nth(index)
        page.locator("label[data-baseweb=radio]").nth(index).click()
        page.wait_for_timeout(100)
        idle()

    click("Open your case")
    click("Begin the interview")
    pick()
    draft = idle()["browser_form_drafts"].copy()
    click("Back")
    readonly()
    click("Forward")
    assert idle()["browser_form_drafts"] == draft
    expect(page.get_by_role("radio").nth(0)).to_be_checked()
    click("Ask the selected question · 1 token")
    assert idle()["investigation_budget"] == 5
    click("Move to evidence")
    pick()
    click("Obtain selected source · 1 token")
    assert idle()["investigation_budget"] == 4
    click("Move to the pressure decision")
    pick()
    click("Commit response · 1 token")
    assert idle()["investigation_budget"] == 3
    click("Revise your response once · 1 token")
    pick()
    click("Commit revised response · 1 token")
    assert idle()["investigation_budget"] == 2
    click("Keep response and shape the conclusion")
    # Two radio groups; choose the first response in each to exercise revision feedback.
    groups = page.get_by_role("radiogroup")
    groups.nth(0).get_by_role("radio").first
    groups.nth(0).locator("label[data-baseweb=radio]").first.click()
    idle()
    page.get_by_role("radiogroup").nth(1).get_by_role("radio").first
    page.get_by_role("radiogroup").nth(1).locator(
        "label[data-baseweb=radio]"
    ).first.click()
    idle()
    click("Test this judgment · 1 token")
    assert idle()["investigation_budget"] == 1
    click("Revise your judgment once · 1 token")
    for i in range(2):
        page.get_by_role("radiogroup").nth(i).get_by_role("radio").last
        page.get_by_role("radiogroup").nth(i).locator(
            "label[data-baseweb=radio]"
        ).last.click()
        idle()
    click("Test revised judgment · 1 token")
    assert idle()["investigation_budget"] == 0
    candidates = ["Keep this judgment", "See what your investigation changed"]
    click(
        next(
            n
            for n in candidates
            if page.get_by_role("button", name=n, exact=True).count()
        )
    )
    state = idle()
    assert state["stage"] == 6
    assert len(state["question_history"]) == 1
    assert len(state["evidence_history"]) == 1
    assert len(state["pressure_history"]) == 2
    assert len(state["conclusion_history"]) == 2
    check(
        "Complete session-only investigation, preserved draft, consequences, both revisions and six-token budget"
    )
