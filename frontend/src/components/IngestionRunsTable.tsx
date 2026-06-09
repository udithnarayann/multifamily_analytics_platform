import type { IngestionRunSummary } from '../api/types';
import { formatDateTime, formatInteger } from '../formatters';

interface IngestionRunsTableProps {
  runs: IngestionRunSummary[];
}

export function IngestionRunsTable({ runs }: IngestionRunsTableProps) {
  if (runs.length === 0) {
    return <div className="empty-chart">No ingestion runs recorded yet.</div>;
  }

  return (
    <div className="table-wrap">
      <table>
        <thead>
          <tr>
            <th>Source</th>
            <th>Status</th>
            <th>Started</th>
            <th>Completed</th>
            <th>Requested</th>
            <th>Upserted</th>
            <th>Failed</th>
          </tr>
        </thead>
        <tbody>
          {runs.map((run) => (
            <tr key={run.id}>
              <td>{run.source_name}</td>
              <td><span className={`status status-${run.status}`}>{run.status}</span></td>
              <td>{formatDateTime(run.started_at)}</td>
              <td>{formatDateTime(run.completed_at)}</td>
              <td>{formatInteger(run.records_requested)}</td>
              <td>{formatInteger(run.records_upserted)}</td>
              <td>{formatInteger(run.records_failed)}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
