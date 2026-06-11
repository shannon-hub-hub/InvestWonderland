import { DesktopShell } from '@/components/DesktopShell';
import { fetchScrapeStats } from '@/lib/api';

export const dynamic = 'force-dynamic';

export default async function AppLayout({ children }: { children: React.ReactNode }) {
  const scrapeStats = await fetchScrapeStats().catch(() => ({
    investors_scraped: 0,
    startups_scraped: 0,
  }));

  return <DesktopShell scrapeStats={scrapeStats}>{children}</DesktopShell>;
}
