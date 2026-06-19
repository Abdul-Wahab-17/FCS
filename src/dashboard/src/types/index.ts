export type Severity = 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';

export interface Violation {
  event_id: string;
  timestamp: string;
  clip_id: string;
  zone: string;
  behavior_class: string;
  policy_rule_ref: string;
  event_description: string;
  description?: string;
  severity: Severity;
  escalation_action: string;
  confidence: number;
  frame_number: number;
  bounding_box?: [number, number, number, number] | null;
  rationale?: string;
  metadata?: Record<string, unknown>;
}

export interface DashboardStats {
  total: number;
  by_severity: Record<string, number>;
  by_behavior: Record<string, number>;
}

export interface ViolationFilters {
  severity?: string;
  behavior_class?: string;
  start_date?: string;
  end_date?: string;
}

export interface ApiProcessResponse {
  status: string;
  count: number;
  reports: Violation[];
}
