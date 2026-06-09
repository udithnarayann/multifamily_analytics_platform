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

export interface FreddieMacObservationSample {
  id: string;
  loan_id: string;
  reporting_quarter: string;
  mortgage_status_code: number | null;
  mortgage_status_label: string | null;
  ending_balance: number | null;
  original_ltv: number | null;
  original_dcr: number | null;
  note_rate: number | null;
  property_state: string | null;
  property_metro: string | null;
  residential_units: number | null;
}

export interface FreddieMacObservationSampleResponse {
  source_label: string;
  observations: FreddieMacObservationSample[];
}

export interface RiskReportResponse {
  id: string;
  freddie_mac_observation_id: string | null;
  hud_property_id: string | null;
  risk_rating: 'low' | 'moderate' | 'elevated' | 'high' | 'critical';
  risk_score: number;
  summary: string;
  key_risk_factors: string[];
  loan_performance_analysis: string;
  credit_metric_analysis: string;
  property_analysis: string | null;
  delinquency_analysis: string;
  analyst_follow_up_questions: string[];
  model_name: string;
  model_version: string | null;
  prompt_version: string;
  input_snapshot: Record<string, unknown>;
  output_snapshot: Record<string, unknown>;
  data_source_labels: string[];
  created_by: string | null;
  created_at: string | null;
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
