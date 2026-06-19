# Severity Logic

Severity rules are defined in `src/severity/rules.json`.

Routing behavior:

- LOW: database log only.
- MEDIUM: database log only.
- HIGH: database log and dashboard alert.
- CRITICAL: database log and dashboard alert.

The classifier applies the default tier first, then evaluates escalation rules against detection metadata.
