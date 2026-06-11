'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { PaletteStrip } from '@/components/PaletteStrip';
import { APP_NAME, APP_TAGLINE } from '@/lib/theme';

const NAV = [
  { href: '/', label: 'Command Center' },
  { href: '/api/docs', label: 'API Docs', external: true },
] as const;

export function DesktopShell({
  children,
  scrapeStats,
}: {
  children: React.ReactNode;
  scrapeStats: { investors_scraped: number; startups_scraped: number };
}) {
  const pathname = usePathname();

  return (
    <div className="desktop-root">
      <div className="window">
        <header className="titlebar hatch-teal">
          <div className="traffic">
            <span className="sq orange" title="Close" />
            <span className="sq mustard" title="Minimize" />
            <span className="sq cream" title="Zoom" />
          </div>
          <div className="title">
            <span className="title-app">🐇 {APP_NAME}</span>
            <span className="title-sub">— Investor digest OS</span>
          </div>
          <div className="titlebar-meta">v1.0 · RETRO</div>
        </header>

        <div className="window-body">
          <aside className="sidebar">
            <div className="brand-box hatch-mustard">
              <div className="brand-diamond">
                <span>◆</span>
              </div>
              <div>
                <div className="sidebar-brand">{APP_NAME}</div>
                <p className="sidebar-sub">{APP_TAGLINE}</p>
              </div>
            </div>

            <nav>
              {NAV.map((item) => {
                const active =
                  item.href === '/'
                    ? pathname === '/'
                    : item.href.startsWith('/')
                      ? pathname === item.href || pathname.startsWith(`${item.href}/`)
                      : false;
                const className = active ? 'nav-item active' : 'nav-item';
                if ('external' in item && item.external) {
                  return (
                    <a key={item.href} href={item.href} className={className} target="_blank" rel="noreferrer">
                      {item.label} ↗
                    </a>
                  );
                }
                return (
                  <Link key={item.href} href={item.href} className={className}>
                    {item.label}
                  </Link>
                );
              })}
            </nav>

            <div className="sidebar-stats">
              <div className="stat-block stat-teal">
                <div className="stat-label">Investors scraped</div>
                <div className="stat-value">{scrapeStats.investors_scraped}</div>
                <div className="stat-hint">OpenVC rescrape runs</div>
              </div>
              <div className="stat-block stat-orange">
                <div className="stat-label">Startups scraped</div>
                <div className="stat-value">{scrapeStats.startups_scraped}</div>
                <div className="stat-hint">Gallery rescrape runs</div>
              </div>
            </div>

            <PaletteStrip compact />
          </aside>

          <main className="content">{children}</main>
        </div>

        <footer className="statusbar hatch-orange">
          <span>Invest Wonderland ready</span>
          <span>#503D2D · #1F9295 · #F0ECC9 · #E3AD43 · #D44C1A</span>
        </footer>
      </div>

      <style jsx>{`
        .desktop-root {
          min-height: 100vh;
          display: grid;
          place-items: center;
          padding: 32px 16px;
        }
        .window {
          width: min(1320px, 100%);
          background: var(--bg-window);
          border: 4px solid var(--border);
          border-radius: var(--radius-window);
          box-shadow: var(--shadow-outset), 10px 10px 0 rgba(0, 0, 0, 0.2);
          overflow: hidden;
        }
        .titlebar {
          display: grid;
          grid-template-columns: 100px 1fr auto;
          align-items: center;
          gap: 10px;
          padding: 10px 14px;
          border-bottom: 4px solid var(--brown);
          color: var(--text-on-teal);
        }
        .traffic {
          display: flex;
          gap: 6px;
        }
        .sq {
          width: 16px;
          height: 16px;
          border: 2px solid var(--brown);
          display: inline-block;
          box-shadow: 1px 1px 0 rgba(0, 0, 0, 0.2);
        }
        .sq.orange {
          background: var(--orange);
        }
        .sq.mustard {
          background: var(--mustard);
        }
        .sq.cream {
          background: var(--cream);
        }
        .title {
          font-family: var(--font-display);
          font-size: 14px;
          font-weight: 700;
        }
        .title-app {
          text-shadow: 2px 2px 0 var(--cream);
          color: var(--teal);
          letter-spacing: 0.04em;
        }
        .title-sub {
          font-weight: 400;
          color: var(--cream);
          opacity: 0.95;
        }
        .titlebar-meta {
          font-family: var(--font-mono);
          font-size: 10px;
          color: var(--cream);
          opacity: 0.9;
        }
        .window-body {
          display: grid;
          grid-template-columns: 248px 1fr;
          min-height: 520px;
        }
        .sidebar {
          background: var(--bg-sidebar);
          border-right: 4px solid var(--border);
          padding: 14px 12px;
          display: flex;
          flex-direction: column;
          gap: 14px;
        }
        .brand-box {
          display: flex;
          gap: 10px;
          align-items: flex-start;
          padding: 10px;
          border: 3px solid var(--border);
          box-shadow: 3px 3px 0 var(--border-soft);
        }
        .brand-diamond {
          width: 36px;
          height: 36px;
          background: var(--cream);
          border: 2px solid var(--border);
          display: grid;
          place-items: center;
          font-size: 16px;
          color: var(--teal);
          transform: rotate(45deg);
          flex-shrink: 0;
        }
        .brand-diamond span {
          transform: rotate(-45deg);
        }
        .sidebar-brand {
          font-family: var(--font-display);
          font-weight: 700;
          font-size: 13px;
          color: var(--brown);
          text-transform: uppercase;
          letter-spacing: 0.06em;
        }
        .sidebar-sub {
          margin: 4px 0 0;
          font-size: 10px;
          line-height: 1.4;
          color: var(--brown);
          opacity: 0.85;
        }
        nav {
          display: flex;
          flex-direction: column;
          gap: 4px;
        }
        nav :global(.nav-item) {
          display: block;
          padding: 9px 10px;
          font-size: 12px;
          font-weight: 700;
          color: var(--brown);
          text-decoration: none;
          border: 2px solid var(--border-soft);
          background: var(--bg-panel);
        }
        nav :global(.nav-item:hover) {
          background: var(--cream);
          border-color: var(--border);
        }
        nav :global(.nav-item.active) {
          background: var(--teal);
          color: var(--cream);
          border-color: var(--brown);
          box-shadow: var(--shadow-inset);
        }
        .sidebar-stats {
          margin-top: auto;
          display: flex;
          flex-direction: column;
          gap: 8px;
        }
        .stat-block {
          background: var(--bg-panel);
          border: 2px solid var(--border);
          padding: 8px 10px;
          box-shadow: 2px 2px 0 var(--border-soft);
        }
        .stat-teal {
          border-left: 5px solid var(--teal);
        }
        .stat-mustard {
          border-left: 5px solid var(--mustard);
        }
        .stat-orange {
          border-left: 5px solid var(--orange);
        }
        .stat-label {
          font-family: var(--font-mono);
          font-size: 9px;
          text-transform: uppercase;
          letter-spacing: 0.08em;
          color: var(--text-muted);
        }
        .stat-value {
          font-family: var(--font-display);
          font-size: 1.25rem;
          font-weight: 700;
          color: var(--orange);
        }
        .stat-hint {
          font-family: var(--font-mono);
          font-size: 8px;
          color: var(--text-muted);
          margin-top: 4px;
          opacity: 0.85;
        }
        .content {
          padding: 22px 24px;
          background: var(--bg-window);
          overflow: auto;
          background-image: repeating-linear-gradient(
            0deg,
            transparent,
            transparent 24px,
            rgba(80, 61, 45, 0.04) 24px,
            rgba(80, 61, 45, 0.04) 25px
          );
        }
        .statusbar {
          display: flex;
          justify-content: space-between;
          flex-wrap: wrap;
          gap: 6px;
          padding: 8px 14px;
          border-top: 4px solid var(--border);
          font-family: var(--font-mono);
          font-size: 9px;
          color: var(--cream);
          letter-spacing: 0.04em;
        }
        @media (max-width: 800px) {
          .window-body {
            grid-template-columns: 1fr;
          }
          .sidebar {
            border-right: none;
            border-bottom: 4px solid var(--border);
          }
          .sidebar-stats {
            flex-direction: row;
            flex-wrap: wrap;
          }
          .stat-block {
            flex: 1;
            min-width: 120px;
          }
        }
      `}</style>
    </div>
  );
}
