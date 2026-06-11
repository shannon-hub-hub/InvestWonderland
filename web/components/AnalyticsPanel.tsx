'use client';

import {
  Bar,
  BarChart,
  Cell,
  Pie,
  PieChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts';
import type { Cooccurrence, FundingFlow } from '@/lib/api';
import { CHART_COLORS, PALETTE } from '@/lib/theme';

function CountBars({
  title,
  rows,
  labelKey,
}: {
  title: string;
  rows: { count: number }[];
  labelKey: 'sector' | 'stage' | 'name';
}) {
  const data = rows.map((r) => ({
    name: (r as Record<string, string | number>)[labelKey] as string,
    count: r.count,
  }));
  if (!data.length) return <p className="muted">No data yet.</p>;
  return (
    <div className="mini-chart">
      <h3>{title}</h3>
      <ResponsiveContainer width="100%" height={200}>
        <BarChart data={data.slice(0, 10)} layout="vertical" margin={{ left: 4, right: 12 }}>
          <XAxis type="number" allowDecimals={false} tick={{ fontSize: 10, fill: PALETTE.brown }} />
          <YAxis type="category" dataKey="name" width={88} tick={{ fontSize: 9, fill: PALETTE.brown }} />
          <Tooltip />
          <Bar dataKey="count" fill={PALETTE.teal} stroke={PALETTE.brown} />
        </BarChart>
      </ResponsiveContainer>
      <style jsx>{`
        .mini-chart {
          border: 2px solid var(--border-soft);
          padding: 8px;
          background: #faf6e4;
        }
        h3 {
          margin: 0 0 6px;
          font-size: 11px;
          text-transform: uppercase;
          font-family: var(--font-mono);
        }
        .muted {
          color: var(--text-muted);
          font-size: 12px;
        }
      `}</style>
    </div>
  );
}

function PairTable({
  title,
  rows,
  cols,
}: {
  title: string;
  rows: Record<string, string | number>[];
  cols: [string, string][];
}) {
  if (!rows.length) return null;
  return (
    <div className="pair-block">
      <h3>{title}</h3>
      <table>
        <thead>
          <tr>
            {cols.map(([label]) => (
              <th key={label}>{label}</th>
            ))}
          </tr>
        </thead>
        <tbody>
          {rows.slice(0, 12).map((row, i) => (
            <tr key={i}>
              {cols.map(([label, key]) => (
                <td key={key}>{row[key]}</td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
      <style jsx>{`
        .pair-block {
          border: 2px solid var(--border-soft);
          padding: 8px;
          background: #faf6e4;
        }
        h3 {
          margin: 0 0 8px;
          font-size: 11px;
          text-transform: uppercase;
          font-family: var(--font-mono);
        }
        table {
          width: 100%;
          border-collapse: collapse;
          font-size: 11px;
        }
        th,
        td {
          text-align: left;
          padding: 4px 6px;
          border-bottom: 1px dashed rgba(80, 61, 45, 0.2);
        }
        th {
          font-family: var(--font-mono);
          font-size: 9px;
          text-transform: uppercase;
          color: var(--text-muted);
        }
      `}</style>
    </div>
  );
}

export function AnalyticsPanel({
  flow,
  cooc,
}: {
  flow: FundingFlow | null;
  cooc: Cooccurrence | null;
}) {
  if (!flow || (flow.investor_count === 0 && flow.startup_count === 0)) {
    return <p className="empty">No scraped data yet. Run a rescrape to populate analytics.</p>;
  }

  const sourcePie = [
    { name: 'openvc.app', count: flow.investor_count },
    { name: 'startups.gallery', count: flow.startup_count },
  ].filter((s) => s.count > 0);

  return (
    <div className="analytics">
      <div className="metrics">
        <span>{flow.investor_count} investors</span>
        <span>{flow.startup_count} startups</span>
        <span>{flow.sector_stage_flow.length} sector×stage cells</span>
      </div>

      <div className="chart-grid">
        <div className="chart-box">
          {sourcePie.length > 0 && (
            <>
              <h3>Sources</h3>
              <ResponsiveContainer width="100%" height={180}>
                <PieChart>
                  <Pie data={sourcePie} dataKey="count" nameKey="name" innerRadius={36} outerRadius={64}>
                    {sourcePie.map((_, i) => (
                      <Cell key={i} fill={CHART_COLORS[i % CHART_COLORS.length]} />
                    ))}
                  </Pie>
                  <Tooltip />
                </PieChart>
              </ResponsiveContainer>
            </>
          )}
        </div>
        <CountBars title="Sectors" rows={flow.by_sector} labelKey="sector" />
        <CountBars title="Stages" rows={flow.by_stage} labelKey="stage" />
        <CountBars title="Locations" rows={flow.by_location} labelKey="name" />
        <CountBars title="Investor types" rows={flow.by_type} labelKey="name" />
      </div>

      {flow.sector_stage_flow.length > 0 && (
        <section>
          <h2>Sector × stage flow</h2>
          <table className="matrix">
            <thead>
              <tr>
                <th>Sector</th>
                <th>Stage</th>
                <th>Investors</th>
              </tr>
            </thead>
            <tbody>
              {flow.sector_stage_flow.slice(0, 20).map((row, i) => (
                <tr key={i}>
                  <td>{row.sector}</td>
                  <td>{row.stage}</td>
                  <td>{row.count}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </section>
      )}

      {cooc && (
        <section className="cooc-grid">
          <PairTable
            title="Industry co-occurrence"
            rows={cooc.industry_pairs}
            cols={[
              ['Tag A', 'tag_a'],
              ['Tag B', 'tag_b'],
              ['Investors', 'investor_count'],
            ]}
          />
          <PairTable
            title="Stage co-occurrence"
            rows={cooc.stage_pairs}
            cols={[
              ['Tag A', 'tag_a'],
              ['Tag B', 'tag_b'],
              ['Investors', 'investor_count'],
            ]}
          />
          <PairTable
            title="Investor pairs (shared industries)"
            rows={cooc.investor_pairs}
            cols={[
              ['Investor A', 'investor_a'],
              ['Investor B', 'investor_b'],
              ['Shared', 'shared_industries'],
            ]}
          />
        </section>
      )}

      <style jsx>{`
        .analytics {
          display: flex;
          flex-direction: column;
          gap: 16px;
        }
        .empty {
          color: var(--text-muted);
          font-size: 13px;
        }
        .metrics {
          display: flex;
          flex-wrap: wrap;
          gap: 12px;
          font-family: var(--font-mono);
          font-size: 11px;
          color: var(--brown);
        }
        .chart-grid {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
          gap: 12px;
        }
        .chart-box {
          border: 2px solid var(--border-soft);
          padding: 8px;
          background: #faf6e4;
        }
        .chart-box h3 {
          margin: 0 0 6px;
          font-size: 11px;
          text-transform: uppercase;
          font-family: var(--font-mono);
        }
        h2 {
          margin: 0 0 8px;
          font-size: 12px;
          font-family: var(--font-mono);
          text-transform: uppercase;
          color: var(--text-muted);
        }
        .matrix {
          width: 100%;
          border-collapse: collapse;
          font-size: 11px;
        }
        .matrix th,
        .matrix td {
          text-align: left;
          padding: 6px 8px;
          border-bottom: 1px solid rgba(80, 61, 45, 0.15);
        }
        .matrix th {
          font-family: var(--font-mono);
          font-size: 9px;
          text-transform: uppercase;
          color: var(--text-muted);
        }
        .cooc-grid {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
          gap: 12px;
        }
      `}</style>
    </div>
  );
}
