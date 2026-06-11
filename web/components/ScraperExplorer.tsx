'use client';

import { useMemo, useState } from 'react';
import type { ScraperInvestor, ScraperStartup } from '@/lib/api';

type Row = ScraperInvestor | ScraperStartup;

export function ScraperExplorer({
  title,
  rows,
  kind,
}: {
  title: string;
  rows: Row[];
  kind: 'investors' | 'startups';
}) {
  const [q, setQ] = useState('');

  const filtered = useMemo(() => {
    const needle = q.trim().toLowerCase();
    if (!needle) return rows;
    return rows.filter((r) => r.name.toLowerCase().includes(needle));
  }, [q, rows]);

  return (
    <div className="explorer">
      <header className="head">
        <h1>{title}</h1>
        <input
          type="search"
          placeholder={`Search ${kind}…`}
          value={q}
          onChange={(e) => setQ(e.target.value)}
        />
      </header>
      <div className="table-wrap">
        <table>
          <thead>
            <tr>
              <th>Name</th>
              {kind === 'investors' ? (
                <>
                  <th>Type</th>
                  <th>Stages</th>
                  <th>Industries</th>
                </>
              ) : (
                <th>Description</th>
              )}
              <th>Website</th>
            </tr>
          </thead>
          <tbody>
            {filtered.map((row) =>
              kind === 'investors' ? (
                <tr key={(row as ScraperInvestor).id}>
                  <td>{row.name}</td>
                  <td>{(row as ScraperInvestor).investor_type || '—'}</td>
                  <td>{(row as ScraperInvestor).stages.slice(0, 2).join(', ') || '—'}</td>
                  <td>{(row as ScraperInvestor).industries.slice(0, 2).join(', ') || '—'}</td>
                  <td>
                    {(row as ScraperInvestor).website ? (
                      <a href={(row as ScraperInvestor).website} target="_blank" rel="noreferrer">
                        Link
                      </a>
                    ) : (
                      '—'
                    )}
                  </td>
                </tr>
              ) : (
                <tr key={(row as ScraperStartup).id}>
                  <td>{row.name}</td>
                  <td className="desc">{(row as ScraperStartup).description?.slice(0, 80) || '—'}</td>
                  <td>
                    {(row as ScraperStartup).website ? (
                      <a href={(row as ScraperStartup).website} target="_blank" rel="noreferrer">
                        Link
                      </a>
                    ) : (
                      '—'
                    )}
                  </td>
                </tr>
              ),
            )}
          </tbody>
        </table>
        {rows.length === 0 ? (
          <p className="empty">
            No {kind} in the database yet. Use <strong>Rescrape OpenVC</strong> or{' '}
            <strong>Rescrape gallery</strong> above, then open this tab again.
          </p>
        ) : filtered.length === 0 ? (
          <p className="empty">No matches for &ldquo;{q}&rdquo;.</p>
        ) : null}
      </div>
      <style jsx>{`
        .explorer {
          display: flex;
          flex-direction: column;
          gap: 14px;
        }
        .head h1 {
          font-family: var(--font-display);
          font-size: 1.25rem;
          margin: 0 0 10px;
          color: var(--brown);
        }
        .head input {
          width: 100%;
          max-width: 320px;
          padding: 8px 10px;
          border: 2px solid var(--border);
          background: var(--bg-panel);
          font-size: 13px;
        }
        .table-wrap {
          border: 2px solid var(--border);
          background: var(--cream);
          overflow: auto;
          box-shadow: 2px 2px 0 var(--border-soft);
        }
        table {
          width: 100%;
          border-collapse: collapse;
          font-size: 12px;
        }
        th,
        td {
          padding: 8px 10px;
          text-align: left;
          border-bottom: 1px solid var(--border-soft);
        }
        th {
          background: var(--bg-sidebar);
          font-family: var(--font-mono);
          font-size: 10px;
          text-transform: uppercase;
          letter-spacing: 0.06em;
        }
        .desc {
          color: var(--text-muted);
          max-width: 280px;
        }
        .empty {
          padding: 2rem;
          text-align: center;
          color: var(--text-muted);
          font-family: var(--font-mono);
        }
      `}</style>
    </div>
  );
}
