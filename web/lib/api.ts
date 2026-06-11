import { APP_NAME } from './theme';

export type ScraperInvestor = {
  id: number;
  name: string;
  investor_type: string | null;
  check_size_min: number | null;
  check_size_max: number | null;
  requirements: string | null;
  website: string;
  logo_url: string | null;
  locations: string[];
  industries: string[];
  stages: string[];
  last_seen_at?: string | null;
  last_ingestion_run_id?: number | null;
  stale?: boolean;
};

export type ScraperStartup = {
  id: number;
  name: string;
  description: string | null;
  website: string;
  logo_url: string | null;
  last_seen_at?: string | null;
  last_ingestion_run_id?: number | null;
  stale?: boolean;
};

export type SectorStageFlow = { sector: string; stage: string; count: number };
export type NameCount = { name: string; count: number };
export type TagPair = { tag_a: string; tag_b: string; investor_count: number };
export type InvestorPair = {
  investor_a: string;
  investor_b: string;
  shared_industries: number;
};

export type FundingFlow = {
  investor_count: number;
  startup_count: number;
  by_sector: { sector: string; count: number }[];
  by_stage: { stage: string; count: number }[];
  by_location: NameCount[];
  by_type: NameCount[];
  sector_stage_flow: SectorStageFlow[];
  startup_stage_flow: { stage: string; count: number }[];
};

export type Cooccurrence = {
  industry_pairs: TagPair[];
  stage_pairs: TagPair[];
  investor_pairs: InvestorPair[];
};

export type ScrapeStats = {
  investors_scraped: number;
  startups_scraped: number;
};

export type IngestionRun = {
  id: number;
  source: string;
  status: string;
  started_at: string;
  finished_at: string | null;
  records_scraped: number;
  records_upserted: number;
  error_message: string | null;
};

function apiBase() {
  if (typeof window !== 'undefined') return '';
  return process.env.API_URL || 'http://127.0.0.1:8000';
}

async function get<T>(path: string): Promise<T> {
  const res = await fetch(`${apiBase()}${path}`, { cache: 'no-store' });
  if (!res.ok) {
    throw new Error(`API ${path} failed: ${res.status}`);
  }
  return res.json();
}

async function post<T>(path: string): Promise<T> {
  const res = await fetch(`${apiBase()}${path}`, { method: 'POST', cache: 'no-store' });
  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    const detail = (body as { detail?: string }).detail ?? res.statusText;
    throw new Error(detail);
  }
  return res.json();
}

export function fetchInvestors(q?: string, limit = 50) {
  const params = new URLSearchParams({ limit: String(limit) });
  if (q) params.set('q', q);
  return get<ScraperInvestor[]>(`/api/v1/investors?${params}`);
}

export function fetchStartups(q?: string, limit = 50) {
  const params = new URLSearchParams({ limit: String(limit) });
  if (q) params.set('q', q);
  return get<ScraperStartup[]>(`/api/v1/startups?${params}`);
}

export function fetchFundingFlow() {
  return get<FundingFlow>('/api/v1/analytics/funding-flow');
}

export function fetchCooccurrence(limit = 25, minShared = 1) {
  return get<Cooccurrence>(
    `/api/v1/analytics/cooccurrence?limit=${limit}&min_shared=${minShared}`,
  );
}

export function triggerIngestion(source: 'investors' | 'startups') {
  return post<{ message: string; source: string }>(
    `/api/v1/ingestion/runs?source=${source}`,
  );
}

export function fetchScrapeStats() {
  return get<ScrapeStats>('/api/v1/ingestion/stats');
}

export function fetchIngestionRuns(source?: 'investors' | 'startups', limit = 12) {
  const params = new URLSearchParams({ limit: String(limit) });
  if (source) params.set('source', source);
  return get<IngestionRun[]>(`/api/v1/ingestion/runs?${params}`);
}

export { APP_NAME };
