import type { Severity } from '../types';

export const API_BASE =
  import.meta.env.VITE_API_URL?.replace(/\/$/, '') || 'http://localhost:8000';

export const SEVERITY_ORDER: Severity[] = ['LOW', 'MEDIUM', 'HIGH', 'CRITICAL'];

export const SEVERITY_LABELS: Record<Severity, string> = {
  LOW: 'Low',
  MEDIUM: 'Medium',
  HIGH: 'High',
  CRITICAL: 'Critical'
};

export const BEHAVIOR_CLASSES = [
  'Safe_Walkway_Violation',
  'Unauthorized_Intervention',
  'Opened_Panel_Cover',
  'Carrying_Overload_with_Forklift'
];
