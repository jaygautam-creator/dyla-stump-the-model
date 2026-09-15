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

// The backend runs on a free-tier host that sleeps when idle (docs/PLAN.md, "Phase 6") -- a cold start
// reloads CLIP+torch+FAISS from scratch, which can take well over the ~1s a warm request needs. 90s
// gives real cold starts room to finish while still eventually surfacing an error instead of freezing
// the UI forever on a genuinely dead backend or dropped connection.
const REQUEST_TIMEOUT_MS = 90_000;

export async function matchPhoto(file: File): Promise<MatchResponse> {
  const form = new FormData();
  form.append("photo", file);

  let res: Response;
  try {
    res = await fetch(`${API_BASE}/match`, {
      method: "POST",
      body: form,
      signal: AbortSignal.timeout(REQUEST_TIMEOUT_MS),
    });
  } catch (e) {
    if (e instanceof Error && e.name === "TimeoutError") {
      throw new MatchError("The matcher is taking too long to respond — it may be waking up from being idle. Please try again in a moment.");
    }
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
