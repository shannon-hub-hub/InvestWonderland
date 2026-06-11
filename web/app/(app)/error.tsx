'use client';

export default function AppError({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  return (
    <div className="err">
      <h2>Briefing window hit a snag</h2>
      <p className="msg">{error.message}</p>
      <button type="button" onClick={() => reset()}>
        Try again
      </button>
      <p className="hint">
        If you see <code>Cannot find module &apos;./682.js&apos;</code> (or similar), stop all
        servers on port 3000, then in <code>web/</code> run <code>npm run dev</code> (it clears{' '}
        <code>.next</code> automatically). Do not run <code>npm run build</code> and{' '}
        <code>npm run dev</code> in the same folder without cleaning between them.
      </p>
      <style jsx>{`
        .err {
          padding: 24px;
          background: var(--bg-panel);
          border: 2px solid var(--border);
          box-shadow: 2px 2px 0 var(--border-soft);
        }
        h2 {
          margin: 0 0 10px;
          font-family: var(--font-display);
          color: var(--brown);
        }
        .msg {
          font-size: 13px;
          color: var(--text-muted);
          margin-bottom: 14px;
        }
        button {
          background: var(--orange);
          color: var(--cream);
          border: 2px solid var(--brown);
          padding: 8px 16px;
          font-weight: 700;
          margin-bottom: 14px;
        }
        .hint {
          font-size: 11px;
          color: var(--text-muted);
          line-height: 1.5;
        }
        code {
          font-family: var(--font-mono);
          font-size: 10px;
        }
      `}</style>
    </div>
  );
}
