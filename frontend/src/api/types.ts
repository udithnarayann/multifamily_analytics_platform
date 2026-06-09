export interface CountBucket {
  key: string;
  count: number;
}

export interface BalanceBucket {
  key: string;
  total_ending_balance: number | null;
  observation_count: number;
}

export interface IngestionRunSummary {
  id: string;
  source_name: string;
  status: string;
  started_at: string | null;
  completed_at: string | null;
  records_requested: number | null;
  records_fetched: number | null;
  records_upserted: number | null;
  records_failed: number | null;
  metadata: Record<string, unknown> | null;
}

export interface HudPropertySummary {
  source_label: string;
  total_hud_properties: number;
  total_units: number | null;
  total_assisted_units: number | null;
  property_count_by_state: CountBucket[];
  top_states_by_property_count: CountBucket[];
  count_by_geocode_quality: CountBucket[];
  latest_hud_ingestion_run: IngestionRunSummary | null;
}

export interface FreddieMacMlpdSummary {
  source_label: string;
  total_loan_quarter_observations: number;
  distinct_loan_count: number;
  min_reporting_quarter: string | null;
  max_reporting_quarter: string | null;
  total_ending_balance_for_latest_quarter: number | null;
  average_original_ltv: number | null;
  average_original_dcr: number | null;
  average_note_rate: number | null;
  count_by_mortgage_status_code: CountBucket[];
  count_by_property_state: CountBucket[];
  latest_freddie_mac_ingestion_run: IngestionRunSummary | null;
}

export interface FreddieMacStatusCode {
  code: number;
  label: string;
}

export interface FreddieMacLatestQuarterSummary {
  source_label: string;
  reporting_quarter: string | null;
  observation_count: number;
  distinct_loan_count: number;
  total_ending_balance: number | null;
  average_original_ltv: number | null;
  average_original_dcr: number | null;
  average_note_rate: number | null;
  count_by_mortgage_status_code: CountBucket[];
  count_by_property_state: CountBucket[];
  top_property_metros_by_balance: BalanceBucket[];
}

export interface RecentIngestionRunsResponse {
  source_label: string;
  runs: IngestionRunSummary[];
}

export interface DashboardData {
  hud: HudPropertySummary;
  freddieMac: FreddieMacMlpdSummary;
  latestQuarter: FreddieMacLatestQuarterSummary;
  statusCodes: FreddieMacStatusCode[];
  ingestionRuns: RecentIngestionRunsResponse;
}
