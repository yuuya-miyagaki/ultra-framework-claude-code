---
description: Run framework validators (contract + status checks)
allowed-tools: Bash, Read
---

# /validate

Run both framework validators and report results.

```bash
python3 scripts/check_framework_contract.py
python3 scripts/check_status.py --root .
```

If an `examples/minimal-project/` directory exists, also run:
```bash
python3 scripts/check_status.py --root examples/minimal-project
```

Report each validator result (PASS/FAIL) and list any failures.
