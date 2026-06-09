import type { ReactNode } from 'react';
import { useEffect, useMemo, useState } from 'react';
import {
  fetchFreddieMacObservationSamples,
  fetchFreddieMacRiskReport,
  generateFreddieMacRiskReport,
} from '../api/client';
import type { FreddieMacObservationSample, RiskReportResponse } from '../api/types';
import {
  formatCurrencyCompact,
  formatDateTime,
  formatInteger,
  formatPercent,
  formatRatio,
} from '../formatters';
import { DataSourceBadge } from './DataSourceBadge';

function Field({ label, value }: { label: string; value: string }) {
  return (
    <div className="ai-field">
      <span>{label}</span>
      <strong>{value}</strong>
    </div>
  );
}

function ReportSection({ title, children }: { title: string; children: ReactNode }) {
  return (
    <div className="ai-report-section">
      <h4>{title}</h4>
      {children}
    </div>
  );
}

function formatStatus(observation: FreddieMacObservationSample): string {
  const code = observation.mortgage_status_code ?? 'unknown';
  const label = observation.mortgage_status_label?.replace(/_/g, ' ') ?? 'unknown';
  return `${code} — ${label}`;
}

function RiskReportCard({ report }: { report: RiskReportResponse }) {
  return (
    <div className="ai-report-card">
      <div className="ai-report-header">
        <div>
          <span className={`risk-pill risk-${report.risk_rating}`}>{report.risk_rating}</span>
          <h3>Saved AI risk report</h3>
        </div>
        <div className="risk-score">
          <span>Risk score</span>
          <strong>{report.risk_score.toFixed(0)}</strong>
        </div>
      </div>

      <ReportSection title="Summary">
        <p>{report.summary}</p>
      </ReportSection>

      <ReportSection title="Key risk factors">
        <ul>
          {report.key_risk_factors.map((factor) => (
            <li key={factor}>{factor}</li>
          ))}
        </ul>
      </ReportSection>

      <div className="two-column compact">
        <ReportSection title="Loan performance analysis">
          <p>{report.loan_performance_analysis}</p>
        </ReportSection>
        <ReportSection title="Credit metric analysis">
          <p>{report.credit_metric_analysis}</p>
        </ReportSection>
      </div>

      <ReportSection title="Delinquency analysis">
        <p>{report.delinquency_analysis}</p>
      </ReportSection>

      <ReportSection title="Analyst follow-up questions">
        <ul>
          {report.analyst_follow_up_questions.map((question) => (
            <li key={question}>{question}</li>
          ))}
        </ul>
      </ReportSection>

      <div className="ai-meta-grid">
        <Field label="Model used" value={report.model_name} />
        <Field label="Created" value={formatDateTime(report.created_at)} />
        <Field label="Prompt version" value={report.prompt_version} />
        <Field label="Data source" value={report.data_source_labels.join(', ')} />
      </div>
    </div>
  );
}

export function AiRiskReportPanel() {
  const [observations, setObservations] = useState<FreddieMacObservationSample[]>([]);
  const [selectedId, setSelectedId] = useState<string>('');
  const [report, setReport] = useState<RiskReportResponse | null>(null);
  const [loadingSamples, setLoadingSamples] = useState(true);
  const [loadingReport, setLoadingReport] = useState(false);
  const [generating, setGenerating] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchFreddieMacObservationSamples()
      .then((payload) => {
        setObservations(payload.observations);
        setSelectedId(payload.observations[0]?.id ?? '');
      })
      .catch((err: unknown) => setError(err instanceof Error ? err.message : 'Unknown error'))
      .finally(() => setLoadingSamples(false));
  }, []);

  useEffect(() => {
    if (!selectedId) return;
    setLoadingReport(true);
    setError(null);
    fetchFreddieMacRiskReport(selectedId)
      .then(setReport)
      .catch((err: unknown) => setError(err instanceof Error ? err.message : 'Unknown error'))
      .finally(() => setLoadingReport(false));
  }, [selectedId]);

  const selectedObservation = useMemo(
    () => observations.find((observation) => observation.id === selectedId) ?? null,
    [observations, selectedId],
  );

  async function handleGenerate() {
    if (!selectedId) return;
    setGenerating(true);
    setError(null);
    try {
      setReport(await generateFreddieMacRiskReport(selectedId));
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Unknown error');
    } finally {
      setGenerating(false);
    }
  }

  return (
    <section className="section-card ai-panel">
      <div className="section-heading">
        <div>
          <DataSourceBadge tone="freddie">Gemini AI · Freddie Mac only</DataSourceBadge>
          <h2>AI risk report</h2>
          <p>
            AI commentary is generated from one real Freddie Mac MLPD loan-quarter observation.
            It is not a property appraisal, not a complete loan history, and does not join to HUD
            property data. It may miss context not present in the selected observation.
          </p>
        </div>
      </div>

      <div className="ai-warning">
        Uses Gemini API quota. Generate only when needed; regenerating creates a fresh saved
        report for the selected observation.
      </div>

      {loadingSamples ? <p>Loading real Freddie Mac observation samples…</p> : null}
      {error ? <div className="inline-error">{error}</div> : null}

      {observations.length > 0 ? (
        <div className="ai-layout">
          <div className="panel">
            <label className="select-label" htmlFor="ai-observation-select">
              Select real loan-quarter observation
            </label>
            <select
              id="ai-observation-select"
              value={selectedId}
              onChange={(event) => setSelectedId(event.target.value)}
            >
              {observations.map((observation) => (
                <option key={observation.id} value={observation.id}>
                  {observation.loan_id} · {observation.reporting_quarter} ·{' '}
                  {observation.property_metro ?? 'unknown metro'}
                </option>
              ))}
            </select>

            {selectedObservation ? (
              <div className="ai-field-grid">
                <Field label="Loan ID" value={selectedObservation.loan_id} />
                <Field label="Quarter" value={selectedObservation.reporting_quarter} />
                <Field label="Status" value={formatStatus(selectedObservation)} />
                <Field label="Ending balance" value={formatCurrencyCompact(selectedObservation.ending_balance)} />
                <Field label="Original LTV" value={formatPercent(selectedObservation.original_ltv)} />
                <Field label="Original DCR" value={formatRatio(selectedObservation.original_dcr)} />
                <Field label="Note rate" value={formatPercent(selectedObservation.note_rate)} />
                <Field label="State" value={selectedObservation.property_state ?? '—'} />
                <Field label="Metro" value={selectedObservation.property_metro ?? '—'} />
                <Field label="Units" value={formatInteger(selectedObservation.residential_units)} />
              </div>
            ) : null}

            <button
              className="primary-button"
              disabled={generating || !selectedId}
              onClick={handleGenerate}
            >
              {generating ? 'Generating…' : report ? 'Regenerate AI Risk Report' : 'Generate AI Risk Report'}
            </button>
          </div>

          <div className="panel">
            {loadingReport ? <p>Checking for an existing saved report…</p> : null}
            {!loadingReport && !report ? <p>No saved report yet for this observation.</p> : null}
            {report ? <RiskReportCard report={report} /> : null}
          </div>
        </div>
      ) : !loadingSamples ? (
        <p>No sample Freddie Mac observations are available yet.</p>
      ) : null}
    </section>
  );
}