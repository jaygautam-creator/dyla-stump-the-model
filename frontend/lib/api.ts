const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export type MatchResult = {
  vendor: string;
  product_id: string;
  title: string;
  design_group: string;
  score: number;
  image_url: string;
};

export type MatchResponse = {
  results: MatchResult[];
  timings: Record<string, number>;
};

export class MatchError extends Error {}

export async function matchPhoto(file: File): Promise<MatchResponse> {
  const form = new FormData();
  form.append("photo", file);

  let res: Response;
  try {
    res = await fetch(`${API_BASE}/match`, { method: "POST", body: form });
  } catch {
    throw new MatchError("Could not reach the matcher. It may still be starting up — try again in a moment.");
  }

  if (!res.ok) {
    const body = await res.json().catch(() => null);
    throw new MatchError(body?.detail || `Match failed (${res.status})`);
  }
  return res.json();
}

export function catalogueImageUrl(path: string): string {
  return `${API_BASE}${path}`;
}
