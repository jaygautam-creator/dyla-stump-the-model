"use client";

import { useCallback, useRef, useState } from "react";
import { Gem, UploadCloud, Loader2, AlertCircle, ImageOff } from "lucide-react";
import { matchPhoto, catalogueImageUrl, MatchError, type MatchResult } from "@/lib/api";

type Status = "idle" | "loading" | "done" | "error";

export default function Home() {
  const [status, setStatus] = useState<Status>("idle");
  const [preview, setPreview] = useState<string | null>(null);
  const [results, setResults] = useState<MatchResult[]>([]);
  const [error, setError] = useState<string>("");
  const [dragActive, setDragActive] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);

  const runMatch = useCallback(async (file: File) => {
    setPreview((old) => {
      if (old) URL.revokeObjectURL(old);
      return URL.createObjectURL(file);
    });
    setStatus("loading");
    setError("");
    setResults([]);
    try {
      const res = await matchPhoto(file);
      setResults(res.results);
      setStatus("done");
    } catch (e) {
      setError(e instanceof MatchError ? e.message : "Something went wrong reading that photo.");
      setStatus("error");
    }
  }, []);

  const onFile = useCallback(
    (files: FileList | null) => {
      const file = files?.[0];
      if (!file) return;
      // iOS Safari often reports an empty file.type for photos picked from the camera roll -- fall
      // back to checking the extension rather than rejecting a genuine photo outright.
      const looksLikeImage =
        file.type.startsWith("image/") || /\.(jpe?g|png|webp|heic|heif)$/i.test(file.name);
      if (!looksLikeImage) {
        setError("Please choose an image file.");
        setStatus("error");
        return;
      }
      runMatch(file);
    },
    [runMatch]
  );

  return (
    <div className="min-h-screen">
      <header className="border-b border-line/70 bg-ivory/80 backdrop-blur-sm sticky top-0 z-10">
        <div className="mx-auto max-w-5xl px-6 py-5 flex items-center gap-2.5">
          <Gem className="w-5 h-5 text-champagne-dark" strokeWidth={1.5} />
          <span className="font-serif text-lg tracking-wide text-charcoal">Dyla</span>
          <span className="text-stone text-sm ml-1">Stump the Model</span>
        </div>
      </header>

      <main className="mx-auto max-w-5xl px-6 py-14">
        <div className="text-center max-w-2xl mx-auto mb-12">
          <h1 className="font-serif text-4xl sm:text-5xl text-charcoal mb-4 leading-tight">
            Find the piece,<br />from the photo.
          </h1>
          <p className="text-stone text-base sm:text-lg leading-relaxed">
            Upload a phone photo of a piece of jewellery and see its closest matches in the catalogue,
            ranked by visual similarity.
          </p>
        </div>

        <div
          onDragOver={(e) => {
            e.preventDefault();
            setDragActive(true);
          }}
          onDragLeave={() => setDragActive(false)}
          onDrop={(e) => {
            e.preventDefault();
            setDragActive(false);
            onFile(e.dataTransfer.files);
          }}
          onClick={() => inputRef.current?.click()}
          role="button"
          tabIndex={0}
          aria-label="Upload a photo of a piece of jewellery"
          onKeyDown={(e) => {
            if (e.key === "Enter" || e.key === " ") {
              e.preventDefault();
              inputRef.current?.click();
            }
          }}
          className={`group cursor-pointer rounded-2xl border-2 border-dashed transition-colors
            focus-visible:outline focus-visible:outline-2 focus-visible:outline-champagne-dark focus-visible:outline-offset-2
            ${dragActive ? "border-champagne bg-blush/40" : "border-line bg-white/60 hover:border-champagne/70"}
            p-10 sm:p-14 flex flex-col items-center text-center gap-4`}
        >
          <input
            ref={inputRef}
            type="file"
            accept="image/*"
            aria-hidden="true"
            tabIndex={-1}
            className="sr-only"
            onChange={(e) => onFile(e.target.files)}
          />
          {preview ? (
            // eslint-disable-next-line @next/next/no-img-element
            <img
              src={preview}
              alt="Your uploaded jewellery photo"
              className="w-40 h-40 object-cover rounded-xl border border-line shadow-sm"
            />
          ) : (
            <div className="w-14 h-14 rounded-full bg-cream flex items-center justify-center group-hover:bg-blush transition-colors">
              <UploadCloud className="w-6 h-6 text-champagne-dark" strokeWidth={1.5} />
            </div>
          )}
          <div>
            <p className="font-medium text-charcoal">
              {preview ? "Drop a different photo, or click to browse" : "Drag a photo here, or click to browse"}
            </p>
            <p className="text-sm text-stone mt-1">JPEG, PNG, or WebP — up to 15MB</p>
          </div>
        </div>

        {status === "loading" && (
          <div className="mt-10 flex flex-col items-center gap-3 text-stone">
            <Loader2 className="w-6 h-6 animate-spin text-champagne-dark" />
            <p>Comparing against the catalogue…</p>
          </div>
        )}

        {status === "error" && (
          <div className="mt-10 flex items-center gap-3 rounded-xl border border-red-200 bg-red-50 px-5 py-4 text-red-800">
            <AlertCircle className="w-5 h-5 shrink-0" />
            <p className="text-sm">{error}</p>
          </div>
        )}

        {status === "done" && (
          <section className="mt-14">
            <h2 className="font-serif text-2xl text-charcoal mb-1">Closest matches</h2>
            <p className="text-stone text-sm mb-8">Ranked by visual similarity — not a guarantee of an exact match.</p>

            {results.length === 0 ? (
              <p className="text-stone">No candidates found.</p>
            ) : (
              <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-5">
                {results.map((r, i) => (
                  <ResultCard key={`${r.vendor}-${r.product_id}`} result={r} rank={i + 1} />
                ))}
              </div>
            )}
          </section>
        )}
      </main>

      <footer className="mx-auto max-w-5xl px-6 py-10 text-center text-xs text-stone/80">
        Built for the Thuli Studios (Dyla) take-home. Whole-image CLIP retrieval over a scraped catalogue —
        see the project README for accuracy numbers and known limitations.
      </footer>
    </div>
  );
}

function ResultCard({ result, rank }: { result: MatchResult; rank: number }) {
  const [imgError, setImgError] = useState(false);
  const pct = Math.round(result.score * 100);

  return (
    <div className="rounded-xl border border-line bg-white overflow-hidden shadow-sm hover:shadow-md transition-shadow">
      <div className="relative aspect-square bg-cream">
        {rank === 1 && (
          <span className="absolute top-2 left-2 z-10 rounded-full bg-champagne-dark text-white text-[10px] font-semibold px-2 py-0.5 tracking-wide">
            BEST MATCH
          </span>
        )}
        {imgError ? (
          <div className="w-full h-full flex items-center justify-center text-stone">
            <ImageOff className="w-6 h-6" strokeWidth={1.5} />
          </div>
        ) : (
          // eslint-disable-next-line @next/next/no-img-element
          <img
            src={catalogueImageUrl(result.image_url)}
            alt={result.title}
            className="w-full h-full object-cover"
            onError={() => setImgError(true)}
          />
        )}
      </div>
      <div className="p-3">
        <p className="text-sm font-medium text-charcoal leading-snug line-clamp-2 min-h-[2.5em]">{result.title}</p>
        <p className="text-xs text-stone capitalize mt-0.5">{result.vendor}</p>
        <div className="mt-2">
          <div className="h-1.5 w-full rounded-full bg-cream overflow-hidden">
            <div className="h-full rounded-full bg-champagne" style={{ width: `${pct}%` }} />
          </div>
          <p className="text-[11px] text-stone mt-1">{pct}% similarity</p>
        </div>
      </div>
    </div>
  );
}
