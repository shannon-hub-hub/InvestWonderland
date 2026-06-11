import { PALETTE } from '@/lib/theme';

const SWATCHES = [
  { name: 'Brown', hex: PALETTE.brown },
  { name: 'Teal', hex: PALETTE.teal },
  { name: 'Cream', hex: PALETTE.cream },
  { name: 'Mustard', hex: PALETTE.mustard },
  { name: 'Orange', hex: PALETTE.orange },
] as const;

export function PaletteStrip({ compact = false }: { compact?: boolean }) {
  return (
    <div className={`strip ${compact ? 'compact' : ''}`} aria-label="Brand color palette">
      {SWATCHES.map((s) => (
        <div key={s.hex} className="swatch" title={`${s.name} ${s.hex}`}>
          <span className="chip" style={{ background: s.hex }} />
          {!compact && <span className="hex">{s.hex}</span>}
        </div>
      ))}
      <style jsx>{`
        .strip {
          display: grid;
          grid-template-columns: repeat(5, 1fr);
          gap: 4px;
          padding: 8px;
          background: var(--brown);
          border: 2px solid var(--brown);
          box-shadow: 2px 2px 0 rgba(0, 0, 0, 0.2);
        }
        .strip.compact .hex {
          display: none;
        }
        .swatch {
          display: flex;
          flex-direction: column;
          align-items: center;
          gap: 3px;
        }
        .chip {
          width: 100%;
          height: 18px;
          border: 2px solid var(--cream);
        }
        .strip.compact .chip {
          height: 12px;
        }
        .hex {
          font-family: var(--font-mono);
          font-size: 7px;
          color: var(--cream);
          letter-spacing: 0.02em;
        }
      `}</style>
    </div>
  );
}
