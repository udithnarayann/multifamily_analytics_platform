import { useEffect, useState } from 'react';
import type { DashboardData } from '../api/types';
import { fetchDashboardData } from '../api/client';
import { DataSourceBadge } from '../components/DataSourceBadge';
import { ErrorState } from '../components/ErrorState';
import { IngestionRunsTable } from '../components/IngestionRunsTable';
import { LoadingState } from '../components/LoadingState';
import { MetricCard } from '../components/MetricCard';
import { DistributionBarChart } from '../components/charts/DistributionBarChart';
import { MetroBalanceChart } from '../components/charts/MetroBalanceChart';
import { formatInteger, formatPercent, formatRatio } from '../formatters';

export function DashboardPage() {
  const [data, setData] = useState<DashboardData | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchDashboardData()
      .then(setData)
      .catch((err: unknown) => setError(err instanceof Error ? err.message : 'Unknown error'));
  }, []);

  if (error) return <ErrorState message={error} />;
  if (!data) return <LoadingState />;

  const { hud, freddieMac, latestQuarter, statusCodes, ingestionRuns } = data;

  return (
    <main className="dashboard">
      <section className="hero">
        <div>
          <p className="eyebrow">Real-Time Multifamily Property Analytics Platform</p>
          <h1>Housing-finance analytics dashboard powered by real public datasets.</h1>
          <p>
            This MVP highlights real HUD public property data and real Freddie Mac MLPD
            loan-quarter observations. It uses no synthetic loan data and makes no assumed join
            between HUD properties and Freddie Mac records.
          </p>
        </div>
        <div className="badge-stack">
          <DataSourceBadge tone="hud">Real HUD public property data</DataSourceBadge>
          <DataSourceBadge tone="freddie">Real Freddie Mac MLPD observations</DataSourceBadge>
          <DataSourceBadge>No synthetic loan data</DataSourceBadge>
          <DataSourceBadge>No assumed HUD/Freddie join</DataSourceBadge>
        </div>
      </section>

      <section className="metric-grid">
        <MetricCard label="HUD properties" value={formatInteger(hud.total_hud_properties)} helper="Real HUD assisted multifamily records" />
        <MetricCard label="HUD total units" value={formatInteger(hud.total_units)} />
        <MetricCard label="HUD assisted units" value={formatInteger(hud.total_assisted_units)} />
        <MetricCard label="Freddie Mac observations" value={formatInteger(freddieMac.total_loan_quarter_observations)} helper="Loan-quarter panel rows" />
        <MetricCard label="Distinct Freddie Mac loans" value={formatInteger(freddieMac.distinct_loan_count)} />
        <MetricCard label="Avg original LTV" value={formatPercent(freddieMac.average_original_ltv)} />
        <MetricCard label="Avg original DCR" value={formatRatio(freddieMac.average_original_dcr)} />
        <MetricCard label="Avg note rate" value={formatPercent(freddieMac.average_note_rate)} />
        <MetricCard label="Latest reporting quarter" value={latestQuarter.reporting_quarter ?? '—'} helper="Chronological SQL quarter sort" />
      </section>

      <section className="section-card">
        <div className="section-heading">
          <div>
            <DataSourceBadge tone="freddie">Real Freddie Mac MLPD loan-quarter observations</DataSourceBadge>
            <h2>Freddie Mac analytics</h2>
            <p>No synthetic loan data. These observations are not joined to HUD properties.</p>
          </div>
        </div>
        <div className="two-column">
          <div className="panel">
            <h3>Status-code distribution</h3>
            <DistributionBarChart data={freddieMac.count_by_mortgage_status_code} color="#1d4ed8" />
          </div>
          <div className="panel">
            <h3>Property-state distribution</h3>
            <DistributionBarChart data={freddieMac.count_by_property_state} color="#7c3aed" />
          </div>
        </div>
        <div className="two-column">
          <div className="panel">
            <h3>Latest-quarter summary: {latestQuarter.reporting_quarter ?? '—'}</h3>
            <div className="mini-grid">
              <MetricCard label="Observations" value={formatInteger(latestQuarter.observation_count)} />
              <MetricCard label="Distinct loans" value={formatInteger(latestQuarter.distinct_loan_count)} />
              <MetricCard label="Avg LTV" value={formatPercent(latestQuarter.average_original_ltv)} />
              <MetricCard label="Avg DCR" value={formatRatio(latestQuarter.average_original_dcr)} />
            </div>
          </div>
          <div className="panel">
            <h3>Top metros by ending balance</h3>
            <MetroBalanceChart data={latestQuarter.top_property_metros_by_balance} />
          </div>
        </div>
        <div className="panel">
          <h3>Status-code definitions</h3>
          <div className="definition-grid">
            {statusCodes.map((status) => (
              <div key={status.code} className="definition-item">
                <strong>{status.code}</strong>
                <span>{status.label.replace(/_/g, ' ')}</span>
              </div>
            ))}
          </div>
        </div>
      </section>

      <section className="section-card">
        <DataSourceBadge tone="hud">Real HUD Multifamily Properties Assisted data</DataSourceBadge>
        <h2>HUD property analytics</h2>
        <div className="two-column">
          <div className="panel">
            <h3>Property count by state</h3>
            <DistributionBarChart data={hud.top_states_by_property_count} color="#0f766e" />
          </div>
          <div className="panel">
            <h3>Geocode quality distribution</h3>
            <DistributionBarChart data={hud.count_by_geocode_quality} color="#ea580c" />
          </div>
        </div>
      </section>

      <section className="section-card">
        <h2>Recent ingestion runs</h2>
        <p>Operational traceability for HUD and Freddie Mac real-data ingestion jobs.</p>
        <IngestionRunsTable runs={ingestionRuns.runs} />
      </section>
    </main>
  );
}
