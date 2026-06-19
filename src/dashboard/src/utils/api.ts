import { API_BASE } from './constants';
import type {
  ApiProcessResponse,
  DashboardStats,
  Violation,
  ViolationFilters
} from '../types';

function queryString(filters: ViolationFilters = {}): string {
  const params = new URLSearchParams();
  Object.entries(filters).forEach(([key, value]) => {
    if (value) params.set(key, value);
  });
  return params.toString();
}

export async function fetchViolations(
  filters: ViolationFilters = {}
): Promise<Violation[]> {
  const qs = queryString(filters);
  const response = await fetch(`${API_BASE}/api/violations${qs ? `?${qs}` : ''}`);
  if (!response.ok) throw new Error('Failed to fetch violations');
  return response.json();
}

export async function fetchStats(): Promise<DashboardStats> {
  const response = await fetch(`${API_BASE}/api/stats`);
  if (!response.ok) throw new Error('Failed to fetch stats');
  return response.json();
}

export async function processVideoPath(videoPath: string): Promise<ApiProcessResponse> {
  const response = await fetch(`${API_BASE}/api/process_video`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ video_path: videoPath })
  });
  if (!response.ok) throw new Error(await response.text());
  return response.json();
}

export async function uploadVideo(file: File): Promise<ApiProcessResponse> {
  const formData = new FormData();
  formData.append('file', file);
  const response = await fetch(`${API_BASE}/api/upload_video`, {
    method: 'POST',
    body: formData
  });
  if (!response.ok) throw new Error(await response.text());
  return response.json();
}

export async function seedDemo(): Promise<ApiProcessResponse> {
  const response = await fetch(`${API_BASE}/api/demo/seed`, { method: 'POST' });
  if (!response.ok) throw new Error(await response.text());
  return response.json();
}

export function exportUrl(format: 'csv' | 'json', filters: ViolationFilters): string {
  const qs = queryString({ ...filters });
  return `${API_BASE}/api/export/violations?format=${format}${qs ? `&${qs}` : ''}`;
}
