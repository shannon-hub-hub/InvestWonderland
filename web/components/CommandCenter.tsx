'use client';

import { useCallback, useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { AnalyticsPanel } from '@/components/AnalyticsPanel';
import { ScraperExplorer } from '@/components/ScraperExplorer';
import type { Cooccurrence, FundingFlow, IngestionRun, ScraperInvestor, ScraperStartup } from '@/lib/api';
import {
  fetchCooccurrence,
  fetchFundingFlow,
  fetchIngestionRuns,
  fetchInvestors,
  fetchStartups,
  triggerIngestion,
} from '@/lib/api';

type Tab = 'analytics' | 'data';

type LogLine = { time: string; text: string; tone?: 'ok' | 'err' | 'info' };

function now() {
  return new Date().toLocaleTimeString();
}

export function CommandCenter({
  initialFlow,
  initialCooc,
  initialInvestors,
  initialStartups,
}: {
  initialFlow: FundingFlow | null;
  initialCooc: Cooccurrence | null;
  initialInvestors: ScraperInvestor[];
  initialStartups: ScraperStartup[];
}) {
  const router = useRouter();
  const [tab, setTab] = useState<Tab>('analytics');
  const [flow, setFlow] = useState<FundingFlow | null>(initialFlow);
  const [cooc, setCooc] = useState<Cooccurrence | null>(initialCooc);
  const [investors, setInvestors] = useState<ScraperInvestor[]>(initialInvestors);
  const [startups, setStartups] = useState<ScraperStartup[]>(initialStartups);
  const [runs, setRuns] = useState<IngestionRun[]>([]);
  const [log, setLog] = useState<LogLine[]>([]);
  const [busy, setBusy] = useState<string | null>(null);
  const [polling, setPolling] = useState(false);

  const pushLog = useCallback((text: string, tone: LogLine['tone'] = 'info') => {
    setLog((prev) => [{ time: now(), text, tone }, ...prev].slice(0, 12));
  }, []);

  const loadTables = useCallback(async () => {
    try {
      const [inv, st] = await Promise.all([
        fetchInvestors(undefined, 500),
        fetchStartups(undefined, 500),
      ]);
      setInvestors(inv);
      setStartups(st);
      return true;
    } catch (e) {
      pushLog(
        `Data tables failed: ${e instanceof Error ? e.message : 'error'}`,
        'err',
      );
      return false;
    }
  }, [pushLog]);

  const refreshAnalytics = useCallback(async () => {
    try {
      const [f, c] = await Promise.all([fetchFundingFlow(), fetchCooccurrence(15)]);
      setFlow(f);
      setCooc(c);
      await loadTables();
      router.refresh();
    } catch (e) {
      pushLog(`Analytics refresh failed: ${e instanceof Error ? e.message : 'error'}`, 'err');
    }
  }, [pushLog, router, loadTables]);

  const pollRuns = useCallback(async () => {
    try {
      const latest = await fetchIngestionRuns(undefined, 8);
      setRuns(latest);
      const active = latest.some((r) => r.status === 'running');
      if (!active) {
        setPolling(false);
        setBusy(null);
        await refreshAnalytics();
        pushLog('Scrape finished — analytics and tables updated.', 'ok');
        router.refresh();
      }
    } catch {
      /* ignore poll errors */
    }
  }, [pushLog, refreshAnalytics, router]);

  useEffect(() => {
    if (!polling) return;
    pollRuns();
    const id = setInterval(pollRuns, 2500);
    return () => clearInterval(id);
  }, [polling, pollRuns]);

  async function scrape(source: 'investors' | 'startups', label: string) {
    setBusy(source);
    pushLog(`Scraping all available records from ${label}…`);
    try {
      const res = await triggerIngestion(source);
      pushLog(res.message, 'ok');
      setPolling(true);
      setTab('analytics');
    } catch (e) {
      pushLog(e instanceof Error ? e.message : 'Scrape failed', 'err');
      setBusy(null);
    }
  }

  return (
    <div className="hub">
      <header className="hub-head hatch-teal">
        <div>
          <p className="eyebrow">Invest Wonderland</p>
          <h1>Command Center</h1>
          <p className="lead">Scrape · funding-flow analytics · data tables.</p>
        </div>
      </header>

      <section className="actions">
        <article className="action-card openvc">
          <span className="icon">🏦</span>
          <h2>OpenVC</h2>
          <p>Re-scrape all investors from openvc.app.</p>
          <button
            type="button"
            className="act-btn primary"
            disabled={!!busy}
            onClick={() => scrape('investors', 'OpenVC')}
          >
            {busy === 'investors' ? 'Scraping…' : '↻ Rescrape OpenVC'}
          </button>
        </article>

        <article className="action-card gallery">
          <span className="icon">🚀</span>
          <h2>startups.gallery</h2>
          <p>Re-scrape all Series C+ companies.</p>
          <button
            type="button"
            className="act-btn primary"
            disabled={!!busy}
            onClick={() => scrape('startups', 'gallery')}
          >
            {busy === 'startups' ? 'Scraping…' : '↻ Rescrape gallery'}
          </button>
        </article>

        <article className="action-card analytics">
          <span className="icon">📊</span>
          <h2>Analytics</h2>
          <p>Refresh charts from the database.</p>
          <button type="button" className="act-btn" disabled={!!busy} onClick={() => refreshAnalytics()}>
            ↻ Refresh analytics
          </button>
        </article>
      </section>

      <div className="split">
        <aside className="status-panel">
          <h3>Activity</h3>
          {polling && <p className="polling">● Scrape in progress…</p>}
          <ul className="log">
            {log.length === 0 && <li className="muted">Actions will appear here.</li>}
            {log.map((line, i) => (
              <li key={i} className={line.tone ?? 'info'}>
                <time>{line.time}</time> {line.text}
              </li>
            ))}
          </ul>
          <h3>Recent jobs</h3>
          <ul className="runs">
            {runs.length === 0 && <li className="muted">No ingestion runs yet.</li>}
            {runs.map((r) => (
              <li key={r.id}>
                <strong>{r.source}</strong> · {r.status} · {r.records_upserted} saved
              </li>
            ))}
          </ul>
        </aside>

        <div className="workspace">
          <div className="tabs">
            {(
              [
                ['analytics', 'Funding flow'],
                ['data', 'Data tables'],
              ] as const
            ).map(([id, label]) => (
              <button
                key={id}
                type="button"
                className={tab === id ? 'tab on' : 'tab'}
                onClick={() => setTab(id)}
              >
                {label}
              </button>
            ))}
          </div>

          {tab === 'analytics' && (
            <div className="panel">
              <AnalyticsPanel flow={flow} cooc={cooc} />
            </div>
          )}

          {tab === 'data' && (
            <div className="panel data-panel">
              <div className="data-toolbar">
                <span>
                  {investors.length} investors · {startups.length} startups in DB
                </span>
                <button type="button" className="act-btn" onClick={() => loadTables()}>
                  ↻ Reload tables
                </button>
              </div>
              <ScraperExplorer title="OpenVC investors" rows={investors} kind="investors" />
              <ScraperExplorer title="startups.gallery" rows={startups} kind="startups" />
            </div>
          )}
        </div>
      </div>

      <style jsx>{`
        .hub {
          display: flex;
          flex-direction: column;
          gap: 16px;
        }
        .hub-head {
          padding: 16px 18px;
          border: 3px solid var(--brown);
          color: var(--cream);
        }
        .eyebrow {
          margin: 0;
          font-family: var(--font-mono);
          font-size: 10px;
          letter-spacing: 0.14em;
          text-transform: uppercase;
          opacity: 0.9;
        }
        h1 {
          margin: 6px 0;
          font-family: var(--font-display);
          font-size: 1.75rem;
          letter-spacing: 0.06em;
          text-shadow: 2px 2px 0 var(--brown);
        }
        .lead {
          margin: 0;
          font-size: 13px;
          opacity: 0.95;
        }
        .actions {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
          gap: 10px;
        }
        .action-card {
          border: 3px solid var(--brown);
          padding: 14px;
          background: var(--cream);
          box-shadow: 4px 4px 0 var(--brown);
          display: flex;
          flex-direction: column;
          gap: 8px;
        }
        .action-card.openvc {
          border-top: 6px solid var(--teal);
        }
        .action-card.gallery {
          border-top: 6px solid var(--orange);
        }
        .action-card.analytics {
          border-top: 6px solid var(--brown);
        }
        .icon {
          font-size: 1.5rem;
        }
        .action-card h2 {
          margin: 0;
          font-size: 14px;
          color: var(--brown);
        }
        .action-card p {
          margin: 0;
          font-size: 11px;
          color: var(--text-muted);
          flex: 1;
        }
        .act-btn {
          border: 2px solid var(--brown);
          background: var(--bg-panel);
          padding: 8px 10px;
          font-weight: 700;
          font-size: 11px;
          cursor: pointer;
        }
        .act-btn.primary {
          background: var(--orange);
          color: var(--cream);
        }
        .act-btn:disabled {
          opacity: 0.55;
          cursor: wait;
        }
        .split {
          display: grid;
          grid-template-columns: 220px 1fr;
          gap: 14px;
          align-items: start;
        }
        .status-panel {
          border: 2px solid var(--brown);
          background: var(--bg-panel);
          padding: 12px;
          font-size: 11px;
          position: sticky;
          top: 8px;
        }
        .status-panel h3 {
          margin: 0 0 8px;
          font-family: var(--font-mono);
          font-size: 10px;
          text-transform: uppercase;
          letter-spacing: 0.08em;
          color: var(--teal);
        }
        .polling {
          color: var(--orange);
          font-weight: 700;
          animation: pulse 1.2s ease infinite;
        }
        @keyframes pulse {
          50% {
            opacity: 0.5;
          }
        }
        .log,
        .runs {
          list-style: none;
          margin: 0 0 14px;
          padding: 0;
        }
        .log li,
        .runs li {
          padding: 4px 0;
          border-bottom: 1px dashed rgba(80, 61, 45, 0.2);
        }
        .log li.ok {
          color: var(--teal);
        }
        .log li.err {
          color: var(--orange);
        }
        .log time {
          font-family: var(--font-mono);
          opacity: 0.7;
        }
        .muted {
          color: var(--text-muted);
        }
        .workspace {
          min-width: 0;
        }
        .tabs {
          display: flex;
          gap: 6px;
          margin-bottom: 10px;
          flex-wrap: wrap;
        }
        .tab {
          border: 2px solid var(--brown);
          background: var(--cream);
          padding: 8px 14px;
          font-weight: 700;
          font-size: 12px;
          cursor: pointer;
        }
        .tab.on {
          background: var(--teal);
          color: var(--cream);
        }
        .panel {
          border: 3px solid var(--brown);
          background: var(--cream);
          padding: 12px;
          min-height: 320px;
        }
        .data-panel {
          display: flex;
          flex-direction: column;
          gap: 20px;
        }
        .data-toolbar {
          display: flex;
          flex-wrap: wrap;
          justify-content: space-between;
          align-items: center;
          gap: 8px;
          font-family: var(--font-mono);
          font-size: 11px;
          color: var(--brown);
        }
        @media (max-width: 900px) {
          .split {
            grid-template-columns: 1fr;
          }
          .status-panel {
            position: static;
          }
        }
      `}</style>
    </div>
  );
}
