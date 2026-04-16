---
description: Run tiered framework evaluation
allowed-tools: Bash, Read
---

# /validate

Run the tier 1 evaluation suite (all 4 validators) and report results.

```bash
python3 scripts/run_eval.py --tier 1
```

Report the summary table and highlight any FAIL or WARNING results.

## Profile-based validation (optional)

To validate a project against a specific profile:
```bash
python3 scripts/check_framework_contract.py --profile=standard --root <project-path>
```

Available profiles: `minimal`, `standard`. (`full` is framework repo root only — do not use with `--root`.)
