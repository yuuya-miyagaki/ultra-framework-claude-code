# QA Browser Workflow

4-step browser verification process for the `qa-browser` agent.

The qa-browser agent uses browser-assist skill for tool resolution.
When gstack `$B` is available, it is preferred for navigation and interaction.
When `$B` is not installed, Playwright MCP tools are used as fallback.
Console and network diagnostics use `$B console` / `$B network` when available.
Playwright MCP is used when `$B` is not installed or when deep inspection is needed.

## Step 1: Snapshot

Verify that the page renders correctly.

- Navigate to the target URL (`$B goto` or `browser_navigate`)
- Capture an accessibility snapshot (`$B snapshot -i` or `browser_snapshot`)
- Take an initial screenshot (`$B screenshot` or `browser_take_screenshot`) and save to `docs/qa-reports/`
  This serves as the baseline visual evidence.
- Check that key elements are present in the snapshot
- Check initial render errors (`$B console --errors` or `browser_console_messages` with level `error`)
- Check initial network errors (`$B network` or `browser_network_requests`)
- Flag any console errors or 4xx/5xx from the initial page load

**Pass criteria:** page loads without blank screen, key elements visible, no critical first-render errors.

## Step 1.5: Buffer Clear

After recording Step 1 results, clear buffers so that Step 3 captures
only errors generated during Step 2 interactions.

- `$B` available: `$B console --clear` and `$B network --clear`
- `$B` unavailable (Playwright MCP fallback): no clear equivalent exists.
  Playwright MCP accumulates all messages since session start.
  In Step 3, subtract the errors already recorded in Step 1 to isolate
  interaction-caused issues.

## Step 2: Interact

Execute key user interactions on the page.

- Click primary actions (`$B click @eN` or `browser_click`)
- Fill forms if applicable (`$B fill @eN "text"` or `browser_fill_form`)
- Navigate between views if multi-page

**Pass criteria:** interactions complete without errors, expected state changes occur.

## Step 3: Verify

Check for runtime errors and network issues.
Use `$B console --errors` and `$B network` when `$B` is available.
Fall back to Playwright MCP when `$B` is not installed.

- Retrieve console messages (`$B console --errors` or `browser_console_messages` with level `error`)
- Retrieve network requests (`$B network` or `browser_network_requests`)
- Flag any 4xx/5xx responses
- Flag any JavaScript errors

**Pass criteria:** no unhandled errors, no unexpected 4xx/5xx responses.

## Step 4: Evidence Capture

Package all evidence for the QA report.

- Save final screenshot only if page state changed since Step 1 (after interaction or navigation).
  If unchanged, reference the Step 1 screenshot path.
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
