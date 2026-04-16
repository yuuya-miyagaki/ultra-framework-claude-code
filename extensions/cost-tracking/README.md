# Cost Tracking Extension

Optional addon (manual opt-in) for recording per-session token usage.
Not included in `setup.sh` profiles.

## Prerequisites

None. This extension requires no MCP servers or external tools.

## Setup

```bash
cp -r extensions/cost-tracking <your-project>/extensions/cost-tracking
```

## Usage

1. Copy `COST-LOG.template.md` to `docs/cost-log.md` (or a location of your choice)
2. At the end of each session, record the token usage in the table
3. Token counts can be obtained from Claude Code's session summary or billing dashboard

## Limitations

- Claude Code does not expose a programmatic token usage API
- Recording is manual; no automated collection is provided
- This extension provides only the recording format, not analysis tooling

## Related

- `extensions/CONVENTIONS.md` — extension conventions
