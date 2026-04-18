# QA Browser Workflow

4-step browser verification process for the `qa-browser` agent.

The qa-browser agent uses browser-assist skill for tool resolution.
When gstack `$B` is available, it is preferred for navigation and interaction.
When `$B` is not installed, Playwright MCP tools are used as fallback.
Console and network diagnostics always use Playwright MCP (no `$B` equivalent).

## Step 1: Snapshot

Verify that the page renders correctly.

- Navigate to the target URL (`$B goto` or `browser_navigate`)
- Capture an accessibility snapshot (`$B snapshot -i` or `browser_snapshot`)
- Take a screenshot (`$B screenshot` or `browser_take_screenshot`) and save to `docs/qa-reports/`
- Check that key elements are present in the snapshot

**Pass criteria:** page loads without blank screen, key elements visible.

## Step 2: Interact

Execute key user interactions on the page.

- Click primary actions (`$B click @eN` or `browser_click`)
- Fill forms if applicable (`$B fill @eN "text"` or `browser_fill_form`)
- Navigate between views if multi-page

**Pass criteria:** interactions complete without errors, expected state changes occur.

## Step 3: Verify

Check for runtime errors and network issues.
Always use Playwright MCP for this step (`$B` has no equivalent).

- Retrieve console messages (`browser_console_messages` with level `error`)
- Retrieve network requests (`browser_network_requests`)
- Flag any 4xx/5xx responses
- Flag any JavaScript errors

**Pass criteria:** no unhandled errors, no unexpected 4xx/5xx responses.

## Step 4: Evidence Capture

Package all evidence for the QA report.

- Save final screenshot to `docs/qa-reports/` (`$B screenshot` or `browser_take_screenshot`)
- Compile structured results: pass/fail per step with details
- List console errors (if any) with summary
- List network errors (if any) with status codes and endpoints
- Return all evidence to the calling QA agent

**Output format:**

```
## Browser QA Evidence
- Page render: PASS/FAIL (screenshot: <path>)
- Console errors: <count> (<summary or "none">)
- Network 4xx/5xx: <count> (<summary or "none">)
- Key interactions: PASS/FAIL (<details>)
```

The QA agent incorporates this evidence into the QA report using the
browser QA section of `QA-REPORT.template.md`.
