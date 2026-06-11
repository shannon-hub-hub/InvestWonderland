import { CommandCenter } from '@/components/CommandCenter';
import { fetchCooccurrence, fetchFundingFlow, fetchInvestors, fetchStartups } from '@/lib/api';

export const dynamic = 'force-dynamic';

export default async function HomePage() {
  const [flow, cooc, investors, startups] = await Promise.all([
    fetchFundingFlow().catch(() => null),
    fetchCooccurrence(15).catch(() => null),
    fetchInvestors(undefined, 500).catch(() => []),
    fetchStartups(undefined, 500).catch(() => []),
  ]);

  return (
    <CommandCenter
      initialFlow={flow}
      initialCooc={cooc}
      initialInvestors={investors}
      initialStartups={startups}
    />
  );
}
