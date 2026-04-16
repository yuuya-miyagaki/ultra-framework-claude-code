# QA Browser Extension

Optional browser-based QA workflow for projects with `ui_surface: true`.

## Prerequisites

- Playwright MCP server configured in your Claude Code environment
- `qa-browser` agent available (included in core `.claude/agents/`)

## Setup

Copy this extension into your project manually:

```bash
cp -r extensions/qa-browser <your-project>/extensions/qa-browser
```

This extension is not included in `setup.sh` profiles. It is manual opt-in.

## Usage

1. Set `ui_surface: true` in `docs/STATUS.md` frontmatter
2. During the QA phase, the QA agent delegates browser checks to `qa-browser`
3. The `qa-browser` agent follows the workflow in [WORKFLOW.md](WORKFLOW.md)
4. Results are incorporated into the QA report by the QA agent

## Files

- `WORKFLOW.md` — 4-step browser verification workflow
- `README.md` — this file

## Related

- `.claude/agents/qa-browser.md` — agent definition (in core)
- `templates/QA-REPORT.template.md` — QA report template with browser section
