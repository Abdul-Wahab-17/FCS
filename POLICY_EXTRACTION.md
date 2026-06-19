# Policy Extraction Process

The compliance policy content in the project plan defines four observable unsafe behavior domains. I translated those into structured rules in `src/severity/rules.json` so the detector, classifier, API, and documentation share the same source of truth.

## Mapping Method

1. Identify each unsafe behavior described by the policy.
2. Convert the written rule into an observable indicator.
3. Assign a default severity from the policy signal.
4. Add context-based escalation rules where the policy describes higher-risk conditions.
5. Store policy section references and rationales with each rule.

## Behavior Rules

### Safe_Walkway_Violation

- Policy reference: Section 3.3.2
- Observable indicator: person outside green-marked walkway boundary.
- Default severity: MEDIUM.
- Rationale: the policy marks it as a warning and high-frequency behavior.
- Escalates to HIGH when the person is within one meter of machinery or during forklift operation.

### Unauthorized_Intervention

- Policy reference: Section 4.3.2
- Observable indicator: person without authorization indicators interacting with equipment.
- Default severity: HIGH.
- Rationale: direct equipment manipulation without clearance has immediate injury risk.
- Escalates to CRITICAL when multiple unauthorized personnel are involved.

### Opened_Panel_Cover

- Policy reference: Section 5.2.2
- Observable indicator: electrical or machine panel cover visible in open state.
- Default severity: MEDIUM.
- Rationale: the hazard exists as a state but escalates with exposure time or personnel proximity.
- Escalates to HIGH after five minutes or when personnel are within one meter.

### Carrying_Overload_with_Forklift

- Policy reference: Section 6.3.2
- Observable indicator: forklift carrying three or more blocks.
- Default severity: CRITICAL.
- Rationale: the policy defines an explicit overload threshold and the vehicle instability hazard is immediate.

## Why JSON Rules

Rules are stored in JSON rather than hardcoded across modules so policy references, default severity, and escalation conditions can be reviewed and updated without changing the detector or API code.
