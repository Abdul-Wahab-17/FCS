# Database Schema

SQLite database: `outputs/violations.db`

Table: `violations`

| Column | Type | Notes |
| --- | --- | --- |
| event_id | TEXT | Primary key |
| timestamp | TEXT | Event timestamp |
| clip_id | TEXT | Source clip id |
| zone | TEXT | Facility zone |
| behavior_class | TEXT | Unsafe behavior |
| policy_rule_ref | TEXT | Policy section |
| event_description | TEXT | Human-readable description |
| severity | TEXT | LOW, MEDIUM, HIGH, CRITICAL |
| escalation_action | TEXT | Routing action |
| confidence | REAL | Detector confidence |
| frame_number | INTEGER | Frame index |
| bounding_box | TEXT | JSON encoded box |
| metadata | TEXT | JSON encoded context |
| rationale | TEXT | Severity rationale |
| created_at | TEXT | Persistence timestamp |

Indexes:

- `idx_violations_timestamp`
- `idx_violations_severity`
- `idx_violations_behavior`
