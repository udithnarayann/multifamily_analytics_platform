import type {
  DashboardData,
  FreddieMacObservationSampleResponse,
  FreddieMacLatestQuarterSummary,
  FreddieMacMlpdSummary,
  FreddieMacStatusCode,
  HudPropertySummary,
  RecentIngestionRunsResponse,
  RiskReportResponse,
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

async function postJson<T>(path: string): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, { method: 'POST' });
  if (!response.ok) {
    const text = await response.text();
    throw new Error(`API request failed (${response.status}) for ${path}: ${text || response.statusText}`);
  }
  return response.json() as Promise<T>;
}

async function getJsonOrNullOn404<T>(path: string): Promise<T | null> {
  const response = await fetch(`${API_BASE_URL}${path}`);
  if (response.status === 404) return null;
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

export async function fetchFreddieMacObservationSamples(
  limit = 5,
): Promise<FreddieMacObservationSampleResponse> {
  return getJson<FreddieMacObservationSampleResponse>(`/freddie-mac/observations/sample?limit=${limit}`);
}

export async function fetchFreddieMacRiskReport(
  observationId: string,
): Promise<RiskReportResponse | null> {
  return getJsonOrNullOn404<RiskReportResponse>(`/risk-reports/freddie-mac/${observationId}`);
}

export async function generateFreddieMacRiskReport(
  observationId: string,
): Promise<RiskReportResponse> {
  return postJson<RiskReportResponse>(`/risk-reports/freddie-mac/${observationId}`);
}
