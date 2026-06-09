import type {
  DashboardData,
  FreddieMacLatestQuarterSummary,
  FreddieMacMlpdSummary,
  FreddieMacStatusCode,
  HudPropertySummary,
  RecentIngestionRunsResponse,
} from './types';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? 'http://127.0.0.1:8000';

async function getJson<T>(path: string): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`);
  if (!response.ok) {
    const text = await response.text();
    throw new Error(`API request failed (${response.status}) for ${path}: ${text || response.statusText}`);
  }
  return response.json() as Promise<T>;
}

export async function fetchDashboardData(): Promise<DashboardData> {
  const [hud, freddieMac, latestQuarter, statusCodes, ingestionRuns] = await Promise.all([
    getJson<HudPropertySummary>('/analytics/hud/summary'),
    getJson<FreddieMacMlpdSummary>('/analytics/freddie-mac/summary'),
    getJson<FreddieMacLatestQuarterSummary>('/analytics/freddie-mac/latest-quarter'),
    getJson<FreddieMacStatusCode[]>('/analytics/freddie-mac/status-codes'),
    getJson<RecentIngestionRunsResponse>('/analytics/ingestion-runs/recent'),
  ]);

  return { hud, freddieMac, latestQuarter, statusCodes, ingestionRuns };
}
