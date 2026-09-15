# Codebase Audit Report: Dyla "Stump the Model" Visual Matcher

**Audit Date:** 2026-09-15  
**Audited Target:** `/Users/jaygautam/desktop/dyla` (entire repository across `src/`, `eval/`, `scripts/`, `configs/`, `docs/`, `backend/`, and `frontend/`)

---

## Executive Summary & Category Status

Every file in the repository was inspected in its entirety. Below is the explicit verification status across all seven requested audit categories:

1. **Matcher Pipeline Correctness (`embed.py`, `index.py`, `matcher.py`, `preprocess.py`, `rerank.py`):**
   - **Issues Identified:** Major algorithmic failure in `preprocess.py` `object_crop()` on annular geometries (rings/kadas); severe latent double-cropping bug in `rerank.py`; `transformers` version incompatibility in `embed.py`; sequential unbatched forward passes in `rerank.py`.
   - **Rerank Disconnection Verified:** Confirmed genuinely disconnected from the production path (`configs/default.yaml`, `cli.py`, `matcher.py`, `backend/main.py`).

2. **Known Unresolved Issue Verification (SKU `7557947424992` Kada Failure):**
   - **Verdict:** Existing diagnosis is incomplete and misattributed. The 0% retrieval is primarily driven by **exact background/lighting color confounding** (the home table surface on which stumper photos and self-sourced catalogue reference photos were shot has identical mean RGB `[167, 163, 157]`, giving `kadda_05` a massive 0.876 cosine match to `own-gold-ring`, whereas Swashaa's true catalogue packshot has a studio white background `[246, 246, 246]`). Furthermore, the conclusion that "crop preprocessing hurt" was distorted because `object_crop` bisected annular jewellery into narrow slivers (e.g., 47×358 px), and `verify_rerank` double-cropped candidate images down to 24–41 px slivers.

3. **Concurrency / I/O Bugs (`scripts/hydrate_catalogue_images.py`, `scrape.py`):**
   - **Issues Identified:** High-concurrency race condition and file corruption caused by 1,528 duplicate `local_path` rows in `products.csv` submitted simultaneously to 16 threads; non-atomic file writes leaving corrupt images cached; `requests.Session` thread safety and connection pool exhaustion (default pool size 10 vs 16 workers).

4. **Security Issues (`backend/main.py`, `render.yaml`):**
   - **Issues Identified:** Unbounded in-memory file buffering causing Denial of Service / OOM (`photo.read()`); client-controlled Content-Type spoofing; insecure prefix matching for path traversal in `/catalogue-image`; hardcoded personal email in `USER_AGENT`.

5. **Frontend Correctness (`frontend/`):**
   - **Issues Identified:** Severe accessibility (a11y) failure (hidden input with `display: none`, upload container lacking keyboard focus/roles/handlers); missing request timeout on `fetch` leading to an infinite loading freeze on cold starts; iOS Safari HEIC rejection due to empty MIME type; unhandled `NaN` scores in UI cards.

6. **Configuration & Deployment Issues (`configs/`, `pyproject.toml`, `Dockerfile`, `render.yaml`):**
   - **Issues Identified:** **Clean-machine and Docker build breaker:** self-sourced items (`own_*.jpg`) are `.gitignored` and have null `image_source_url`, causing `build-index` to crash with `FileNotFoundError`; relative working directory dependencies in `backend/main.py`; `pyyaml` missing from core dependencies; missing `pillow-heif`; hardcoded CUDA-blind device selection.

7. **Dead Code & Inconsistencies:**
   - **Issues Identified:** `DECISIONS.md` line 74 contains a stale claim ("Headline (real 58 photos, CLIP + crop): 75.9%"); `docs/PLAN.md` line 14 incorrectly lists `verify_rerank` in the FastAPI backend description; missing baseline `configs/dinov2.yaml`.

---

## Detailed Findings (Ordered by Severity)

### [SEVERITY: critical] Clean-machine & Docker build crash: self-sourced catalogue images are gitignored and unhydratable
- **File:** `.gitignore`, line 8; `data/catalogue/products.csv`, lines 7271–7272; `scripts/hydrate_catalogue_images.py`, lines 41–44; `backend/Dockerfile`, lines 22–23; `README.md`, lines 28–33
- **What's wrong:** The catalogue images directory `data/catalogue/images/` is `.gitignored`. For scraped products, `hydrate_catalogue_images.py` redownloads them using `image_source_url`. However, the two self-sourced items (`own-gold-chain` and `own-gold-ring`) have `image_source_url` set to empty/NaN. `hydrate_catalogue_images.py` cannot download them and skips them. Consequently, on any fresh clone or inside the Docker container build (`backend/Dockerfile`), `data/catalogue/images/own_gold-chain.jpg` and `own_gold-ring.jpg` do not exist. When `dyla-match build-index` subsequently runs, it attempts to load all paths listed in `products.csv` and crashes with `FileNotFoundError`.
- **Concrete failure scenario:** A reviewer follows the `README.md` quickstart on a fresh machine or runs `docker build -t dyla-backend -f backend/Dockerfile .`. When `dyla-match build-index` runs, Python raises `FileNotFoundError: [Errno 2] No such file or directory: 'data/catalogue/images/own_gold-chain.jpg'`. Neither the CLI quickstart nor the backend container can build.
- **Suggested fix:** Whitelist self-sourced images in `.gitignore` via `!data/catalogue/images/own_*.jpg` and track them in git, or update `hydrate_catalogue_images.py` to copy/restore them from `data/stumper/photos/`.

---

### [SEVERITY: critical] Race condition and file corruption in catalogue hydration due to duplicate local paths
- **File:** `scripts/hydrate_catalogue_images.py`, lines 41–48; `src/dyla_match/catalogue/scrape.py`, lines 82–90; `data/catalogue/products.csv`
- **What's wrong:** `data/catalogue/products.csv` contains 7,272 product rows, but only 5,744 unique `local_path` destinations (1,528 duplicate paths due to multi-variant listings sharing imagery). `hydrate_catalogue_images.py` builds `pending` directly from `rows` without deduplicating by destination file. When executed with `ThreadPoolExecutor(max_workers=16)`, multiple worker threads concurrently process the exact same destination file, writing simultaneously to `dest.with_suffix(".tmp")`. One thread unlinks or overwrites `.tmp` while another thread is reading it via `Image.open(tmp)`, or two threads execute `img.save(dest)` concurrently.
- **Concrete failure scenario:** Running `python -m scripts.hydrate_catalogue_images` on a clean machine without existing images causes multiple worker threads to race on identical filenames (e.g. `giva_4529134272602_47056439804066.jpg`). Workers crash with `FileNotFoundError`, `OSError: image file is truncated`, or write partially corrupted JPEG files.
- **Suggested fix:** Deduplicate `pending` by destination path (`seen = set()`) before submitting tasks to the executor, and write to unique thread-safe temporary filenames (e.g., `tempfile.NamedTemporaryFile` in `dest.parent`).

---

### [SEVERITY: critical] Runtime crash on standard transformers installations (`AttributeError: 'Tensor' object has no attribute 'pooler_output'`)
- **File:** `src/dyla_match/embed.py`, lines 54–57; `pyproject.toml`, line 19
- **What's wrong:** `pyproject.toml` specifies `"transformers>=4.40"`. However, in `transformers` versions 4.40 through 4.49, `CLIPModel.get_image_features()` returns a bare `torch.Tensor`. Line 57 explicitly accesses `.pooler_output` (`feats = self.model.get_image_features(**inputs).pooler_output`), assuming `transformers>=5.0.0` (which is unreleased or prerelease). On any clean environment where pip resolves `transformers` to a 4.x release, this line immediately crashes with `AttributeError`.
- **Concrete failure scenario:** A user installs the repo dependencies with `pip install -e ".[ml]"`. Pip installs `transformers==4.46.x`. Running `dyla-match match --photo ...` crashes with `AttributeError: 'Tensor' object has no attribute 'pooler_output'`.
- **Suggested fix:** Handle both return types defensively: `feats = out.pooler_output if hasattr(out, "pooler_output") else out`, or pin `transformers>=5.0` in `pyproject.toml`.

---

### [SEVERITY: critical] Denial of Service (OOM) via unmetered file buffering in FastAPI `/match`
- **File:** `backend/main.py`, lines 64–66
- **What's wrong:** Line 64 performs `body = await photo.read()` before checking file length against `MAX_UPLOAD_BYTES` (15MB). In Starlette/FastAPI, `photo.read()` reads the entire incoming request stream into server RAM. An attacker can send a multi-gigabyte payload, causing the process to exhaust memory and be killed by the OS kernel OOM killer before line 65's size check can execute.
- **Concrete failure scenario:** A client sends a `POST /match` request with a 1GB body to the deployed FastAPI service on Render (Starter plan: 512MB–1GB RAM). The server attempts to buffer the 1GB payload into memory, runs out of memory, and terminates the container.
- **Suggested fix:** Stream the upload in chunks (e.g. 64KB) while keeping a running byte count, and immediately abort with HTTP 413 if the count exceeds `MAX_UPLOAD_BYTES`.

---

### [SEVERITY: high] Annular geometry bisection flaw in `object_crop()` breaks rings, bangles, and necklaces
- **File:** `src/dyla_match/preprocess.py`, lines 16–37, 56–57
- **What's wrong:** `_largest_dense_run()` operates on 1D projections (`mask.mean(axis=1)` and `mask.mean(axis=0)`). Any jewellery item with a central opening (rings, bangles/kadas, hoop earrings, looped chains) has high foreground density at its outer rim tangents and a density valley in the center hole. Whenever the center column/row density dips below `0.3 * peak_density`, `_largest_dense_run` splits the object into disconnected runs and discards everything except one rim. It literally bisects the ring or kada, producing extreme degenerate crops (e.g., 47×358 px or 56×269 px) that distort the aspect ratio and discard 50–70% of the jewellery item.
- **Concrete failure scenario:** An uncropped image of Swashaa kada (`swashaa_7557947424992_46784612106464.jpg`, 384×512) is passed to `object_crop()`. The center of the kada dips below threshold on the x-axis projection; `_largest_dense_run` selects only the left rim, cropping the image to 56×269. Resized to 224×224 for CLIP, the bangle becomes an unrecognizable horizontal smear, dropping top-1 SKU accuracy from 75.9% to 51.7%.
- **Suggested fix:** Use 2D connected-component bounding boxes (e.g., via `scipy.ndimage.label` or flood fill) or use the outer convex hull / extent of all density regions above threshold rather than the single largest 1D run.

---

### [SEVERITY: high] Latent double-crop bug in `verify_rerank()` destroys candidate embeddings
- **File:** `src/dyla_match/rerank.py`, lines 67–74; `eval/run_rerank.py`, lines 22–24; `src/dyla_match/embed.py`, lines 51–52
- **What's wrong:** In `src/dyla_match/rerank.py`, `verify_rerank` explicitly crops the candidate images: `cand_tight = object_crop(cand_img, pad_frac=TIGHT_CROP_PAD_FRAC)`. It then passes `cand_tight` to `embedder.embed([cand_tight])`. In `eval/run_rerank.py`, `embedder` is loaded with `configs/clip_crop.yaml`, which sets `preprocess.object_crop: true`. Because `embedder.use_object_crop` is `True`, `embedder.embed()` calls `object_crop()` a **second time** on `cand_tight` with `pad_frac=0.12`. On this second pass, the tightly cropped item touches all four corners; `object_crop` samples the golden metal as background (`bg`), inverts the foreground mask, and truncates the candidate to a 24–41 pixel sliver.
- **Concrete failure scenario:** In `eval/run_rerank.py`, every candidate image is cropped twice sequentially. On `swashaa_7557947424992_46784612270304.jpg`, Crop 1 yields (48, 229); Crop 2 reduces it to (24, 229). The resulting tight scores compare noise, causing real-photo accuracy to collapse from 75.9% to 31.0%.
- **Suggested fix:** Set `embedder.use_object_crop = False` when instantiating the verification embedder, or prevent `embedder.embed()` from re-cropping images that are already cropped.

---

### [SEVERITY: high] Keyboard navigation and screen reader accessibility failure on upload dropzone
- **File:** `frontend/app/page.tsx`, lines 70–92
- **What's wrong:** The file dropzone is a `<div>` element with an `onClick` handler that triggers `inputRef.current?.click()`. It lacks `tabIndex={0}`, `role="button"`, `aria-label`, and `onKeyDown` listeners (Enter / Space). Furthermore, the actual `<input type="file" />` has Tailwind class `className="hidden"`, which applies `display: none;`. Because `display: none` removes elements from the accessibility tree and keyboard focus order, a keyboard-only user or screen-reader user cannot tab to or trigger the file upload control.
- **Concrete failure scenario:** A user navigates the web demo using only the keyboard (`Tab` key). The focus jumps straight from the header to the page footer, completely bypassing the upload zone. Pressing `Enter` or `Space` has no effect, making the application unusable for keyboard-only users.
- **Suggested fix:** Replace `className="hidden"` on the input with standard accessible hidden styling (e.g. `className="sr-only"`), wrap the dropzone in a semantic `<label htmlFor="photo-upload">`, or add `tabIndex={0}`, `role="button"`, and `onKeyDown` to the container.

---

### [SEVERITY: high] Missing fetch timeout in frontend causes permanent freeze on slow or cold-starting backends
- **File:** `frontend/lib/api.ts`, lines 19–28; `frontend/app/page.tsx`, lines 22–32
- **What's wrong:** `matchPhoto()` invokes `fetch(`${API_BASE}/match`, { method: "POST", body: form })` without passing an `AbortSignal` or timeout. When deployed to platforms like Render (whose instances spin down when idle, taking 60–90 seconds to wake up and load PyTorch/CLIP into memory), or during network drops, `fetch` will wait indefinitely. The UI stays locked in `status === "loading"` ("Comparing against the catalogue…") without giving the user feedback or an option to retry.
- **Concrete failure scenario:** The FastAPI backend is deployed on Render and has spun down. A user uploads a photo. The browser waits for over 2 minutes while the spinner spins continuously. If the connection drops silently, the UI never transitions to an error state.
- **Suggested fix:** Add `signal: AbortSignal.timeout(45000)` to the `fetch` options, catch `AbortError` / `TimeoutError`, and display an explicit "Backend took too long to respond — it may be cold-starting, please retry" message.

---

### [SEVERITY: high] Missing `pyyaml` in core dependencies breaks CLI on base install
- **File:** `pyproject.toml`, lines 6–21; `src/dyla_match/cli.py`, line 16
- **What's wrong:** `src/dyla_match/cli.py` unconditionally imports `yaml` at top level (`import yaml`). However, `pyyaml` is listed under `[project.optional-dependencies].ml`, not under core `dependencies`. If a user or downstream tool installs the package using `pip install -e .` without extras, the entry point script `dyla-match` is installed in PATH, but executing it fails immediately.
- **Concrete failure scenario:** A user installs the base package via `pip install -e .` and runs `dyla-match --help`. Python crashes immediately with `ModuleNotFoundError: No module named 'yaml'`.
- **Suggested fix:** Move `"pyyaml>=6.0"` from `[project.optional-dependencies].ml` into base `project.dependencies`.

---

### [SEVERITY: high] Missing `pillow-heif` dependency for advertised HEIC/HEIF phone uploads
- **File:** `backend/main.py`, line 26; `pyproject.toml`, lines 6–26
- **What's wrong:** `backend/main.py` explicitly lists `"image/heic"` and `"image/heif"` in `ALLOWED_CONTENT_TYPES`. However, standard Pillow cannot decode HEIF/HEIC files out of the box without the `pillow-heif` library. Neither `pyproject.toml` nor `backend/Dockerfile` includes `pillow-heif`. When an iPhone user uploads a native HEIC photo, `_state["matcher"].match` crashes inside PIL, and the backend returns HTTP 422.
- **Concrete failure scenario:** An iPhone user uploads an unaltered `.heic` photo. The upload passes content-type validation (`image/heic`), but `Image.open()` raises `UnidentifiedImageError: cannot identify image file`. The API responds with HTTP 422 ("could not read this file as an image").
- **Suggested fix:** Add `"pillow-heif>=0.18"` to `pyproject.toml` under `api` and call `pillow_heif.register_heif_opener()` in `backend/main.py`.

---

### [SEVERITY: medium] Macro-precision divisor bug when classes have zero predictions
- **File:** `eval/metrics.py`, lines 92–95; `eval/report_clip.md`, lines 44–47
- **What's wrong:** In `multiclass_precision_recall_f1()`, line 92 computes:
  `macro_p = sum(v["precision"] for v in per_class.values() if v["precision"] == v["precision"]) / len(classes)`
  When a class has zero positive predictions (`tp + fp == 0`), its precision is `float("nan")`. The comprehension `if v["precision"] == v["precision"]` filters out `NaN` from the numerator sum, but the divisor remains `len(classes)`! This divides the sum of valid precisions by the total number of classes, silently treating the missing class as having precision 0.0 in the macro average while displaying `nan` in the table.
- **Concrete failure scenario:** In `eval/report_clip.md`, `7557947424992` has precision `nan`, `own-gold-chain` has `1.000`, and `own-gold-ring` has `0.711`. The valid precisions sum to 1.711. The report outputs `macro avg = 0.570` (which is `1.711 / 3`), rather than `1.711 / 2 = 0.856` (macro average over classes with predictions) or explicitly defining unpredicted classes as `0.0`.
- **Suggested fix:** Either divide the sum by the number of non-NaN classes (`sum(1 for v in per_class.values() if not math.isnan(v["precision"]))`), or explicitly set `precision = 0.0` when `tp + fp == 0`.

---

### [SEVERITY: medium] Non-atomic file writes in image scraper cause corrupt image cache
- **File:** `src/dyla_match/catalogue/scrape.py`, lines 84–90; `scripts/hydrate_catalogue_images.py`, line 48
- **What's wrong:** In `download_and_resize()`, the PIL thumbnail is saved directly to the final destination path `dest` (`img.save(dest, "JPEG", quality=90)`). If the process is terminated (SIGINT / timeout / out of disk) while `img.save` is writing, a zero-byte or truncated `.jpg` file is left at `dest`. Because line 69 checks `if dest.exists(): return True`, all subsequent runs of `hydrate_catalogue_images.py` skip this file, permanently leaving a corrupt image on disk.
- **Concrete failure scenario:** A user cancels `hydrate_catalogue_images.py` with Ctrl+C midway through downloading. On the next invocation, the truncated images are assumed complete. Later, `cli.py build-index` crashes with `PIL.UnidentifiedImageError` or `OSError: image file is truncated`.
- **Suggested fix:** Save the thumbnail to a temporary file in the same directory (e.g. `dest.with_suffix(".tmp.jpg")`) and atomically rename it via `os.replace(tmp_file, dest)`.

---

### [SEVERITY: medium] Insecure prefix matching in `/catalogue-image` endpoint
- **File:** `backend/main.py`, lines 103–105
- **What's wrong:** Line 104 checks path traversal using string prefix:
  `if not str(resolved).startswith(str(catalogue_dir)): raise HTTPException(400, "invalid path")`
  Because `str(catalogue_dir)` lacks a trailing directory separator, if `catalogue_dir` is `/app/data/catalogue`, any resolved path beginning with `/app/data/catalogue_backup/` or `/app/data/catalogue.env` would satisfy `startswith`.
- **Concrete failure scenario:** If an attacker crafts metadata pointing to a directory sharing the same prefix as `catalogue_dir` (e.g. `/app/data/catalogue_private/secret.jpg`), the prefix check passes.
- **Suggested fix:** Use Python 3.9+'s native `resolved.is_relative_to(catalogue_dir)` or ensure a trailing path separator: `str(catalogue_dir).rstrip('/') + '/'`.

---

### [SEVERITY: medium] Hardcoded relative paths in backend break when executed from non-root CWD
- **File:** `backend/main.py`, lines 23, 41, 50; `configs/default.yaml`, lines 25–26, 38
- **What's wrong:** `CONFIG_PATH` defaults to `"configs/default.yaml"`, and `configs/default.yaml` uses relative paths (`data/catalogue`, `data/index`). All path lookups are resolved against the current working directory (`os.getcwd()`). If the FastAPI server is launched from inside the `backend/` directory (e.g. `cd backend && uvicorn main:app`) or by a systemd supervisor running from `/`, path resolution fails.
- **Concrete failure scenario:** A developer runs `cd backend && uvicorn main:app --reload`. On startup, `load_matcher()` crashes with `FileNotFoundError: [Errno 2] No such file or directory: 'configs/default.yaml'`.
- **Suggested fix:** Resolve paths relative to the project root: `PROJECT_ROOT = Path(__file__).resolve().parent.parent`, and anchor `CONFIG_PATH` and config entries to `PROJECT_ROOT`.

---

### [SEVERITY: medium] Background and surface confounding drives the 0% Kada retrieval failure
- **File:** `DECISIONS.md`, lines 83–93; `data/catalogue/images/own_*.jpg`; `data/stumper/photos/`
- **What's wrong:** The existing analysis in `DECISIONS.md` attributes the 0% recall of SKU `7557947424992` (Swashaa kada) to "plain, featureless gold jewellery looking identical to every backbone." While low surface detail is a factor, empirical analysis of image statistics reveals a more fundamental confounding variable: **background color temperature and lighting domain**.
  - All stumper photos of the kada were shot on a home wooden/beige table (mean RGB: `[167.3, 163.3, 156.7]`).
  - The reference images for `own-gold-ring` and `own-gold-chain` were shot on the **exact same table** (mean RGB: `[169.0, 165.0, 157.4]` and `[163.7, 158.0, 151.4]`).
  - Swashaa's catalogue images are studio packshots on pure white backgrounds (mean RGB: `[245.8, 245.8, 245.8]`).
  Because the jewellery item occupies only 10–15% of the frame, the whole-image CLIP embedding is dominated by background pixels. Consequently, `kadda_05` achieves an **0.876 cosine similarity** to `own-gold-ring` (identical background), out-competing its true Swashaa packshot (**0.779 cosine similarity**). The 96.4% and 100% scores on the two self-sourced items are inflated by background leakage, while the kada fails because it is the only item forced to cross the phone-to-studio domain gap.
- **Concrete failure scenario:** A clean phone photo of the kada (`kadda_00` or `kadda_05`) is submitted to `dyla-match`. CLIP ranks `own-gold-ring` at #1 (score 0.876) and places the true kada at rank 15–43, because the background table matches `own-gold-ring`'s reference image almost perfectly.
- **Suggested fix:** Document in `DECISIONS.md` that background domain leakage (home table vs white studio packshot) is the primary driver of the kada failure and self-sourced success, and that a proper segmentation mask (removing background before embedding) is required.

---

### [SEVERITY: medium] Hardcoded device selection ignores CUDA GPUs on Linux
- **File:** `src/dyla_match/embed.py`, lines 18–23
- **What's wrong:** `pick_device(requested: str = "auto")` only checks `torch.backends.mps.is_available()`. It never inspects `torch.cuda.is_available()`. When deployed on a Linux server or cloud VM equipped with an Nvidia GPU, it defaults to `"cpu"`, completely ignoring available CUDA acceleration.
- **Concrete failure scenario:** A user deploys the application on an AWS EC2 `g4dn` instance or Render GPU plan with CUDA available. `pick_device("auto")` returns `"cpu"`, performing all inferences on CPU with 10x higher latency.
- **Suggested fix:** Update `pick_device` to check CUDA first:
  ```python
  if torch.cuda.is_available():
      return "cuda"
  if torch.backends.mps.is_available():
      return "mps"
  return "cpu"
  ```

---

### [SEVERITY: medium] Sequential unbatched neural network inference in `verify_rerank()`
- **File:** `src/dyla_match/rerank.py`, lines 70–75
- **What's wrong:** In `verify_rerank()`, candidate products are iterated one by one:
  ```python
  tight_vecs = []
  for _, row in candidates.iterrows():
      cand_img = Image.open(catalogue_dir / row["local_path"]).convert("RGB")
      cand_tight = object_crop(cand_img, pad_frac=TIGHT_CROP_PAD_FRAC)
      tight_vecs.append(embedder.embed([cand_tight])[0])
  ```
  This performs 75 individual single-image forward passes through CLIP. On an Apple M2 or CPU, this adds 3–6 seconds of latency per query, rather than batching the 75 images in chunks of 16.
- **Concrete failure scenario:** When running `eval/run_rerank.py`, matching 103 photos takes over 10 minutes because every photo runs 75 individual PyTorch forward passes.
- **Suggested fix:** Collect all `cand_tight` images into a list and call `embedder.embed(batch)` in batches of 16.

---

### [SEVERITY: medium] iOS Safari HEIC uploads rejected client-side due to empty MIME type
- **File:** `frontend/app/page.tsx`, lines 39–43
- **What's wrong:** Line 39 checks:
  `if (!file.type.startsWith("image/")) { setError("Please choose an image file."); return; }`
  On iOS Safari, photos selected directly from the camera roll or file picker often have an empty string `""` for `file.type`. The check fails, and the user is blocked before the photo is uploaded.
- **Concrete failure scenario:** A user opens the web demo on an iPhone, takes a photo, and selects it. The frontend immediately displays "Please choose an image file." without sending the request.
- **Suggested fix:** Check the file extension as a fallback:
  `const isImage = file.type.startsWith("image/") || /\.(jpe?g|png|webp|heic|heif)$/i.test(file.name);`

---

### [SEVERITY: low] Contradictory claim in `DECISIONS.md` ("CLIP + crop: 75.9%")
- **File:** `DECISIONS.md`, line 74
- **What's wrong:** Line 74 states: `Headline (real 58 photos, CLIP + crop): 75.9% top-1 SKU accuracy [63.5%, 85.0%].` This directly contradicts line 31 ("CLIP+crop real top-1 SKU 75.9% -> 51.7%... Rejected both times; configs/default.yaml uses the plain, uncropped whole-image embedding"), line 100, and `README.md` line 11 ("CLIP... plain whole-image cosine retrieval, no crop/re-rank/ensemble... 75.9%"). The 75.9% number is from plain uncropped CLIP; with crop, accuracy was 51.7%.
- **Concrete failure scenario:** A reviewer reading Section 6 sees "CLIP + crop: 75.9%", conflicting with Section 3 which reports that crop degraded accuracy to 51.7%.
- **Suggested fix:** Change "Headline (real 58 photos, CLIP + crop)" to "Headline (real 58 photos, plain whole-image CLIP)".

---

### [SEVERITY: low] Stale pipeline description in `docs/PLAN.md`
- **File:** `docs/PLAN.md`, line 14
- **What's wrong:** Line 14 specifies: `Backend: FastAPI wrapping the existing Matcher/verify_rerank pipeline`. `verify_rerank` was subsequently measured to degrade accuracy and was rejected; `backend/main.py` only wraps `Matcher`.
- **Concrete failure scenario:** A reviewer checking the implementation against `docs/PLAN.md` would look for `verify_rerank` in the backend code and suspect missing functionality.
- **Suggested fix:** Update line 14 to clarify that the backend wraps `Matcher` only, since `verify_rerank` was rejected.

---

### [SEVERITY: low] Missing `re.escape()` in condition tag matching
- **File:** `eval/harness.py`, line 84
- **What's wrong:** Line 84 constructs a regex using raw condition string: `rf"(?:^|;){cond}(?:;|$)"`. If any condition tag in `labels.csv` ever contains regex metacharacters (e.g. `+`, `(`, `)`), the regex will fail to compile or match unintended characters.
- **Concrete failure scenario:** A condition tag like `whatsapp(hd)` is added to `labels.csv`. `str.contains(rf"(?:^|;){cond}(?:;|$)")` raises `re.error: missing ), unterminated subpattern`.
- **Suggested fix:** Wrap `cond` in `re.escape`: `rf"(?:^|;){re.escape(cond)}(?:;|$)"`.

---

### [SEVERITY: low] Division by zero in `far_frr_curve()` when `n_thresholds=1`
- **File:** `eval/metrics.py`, lines 63–64
- **What's wrong:** Line 64 computes `t = lo + (hi - lo) * i / (n_thresholds - 1)`. If called with `n_thresholds = 1`, it raises `ZeroDivisionError`.
- **Concrete failure scenario:** A caller requests a single threshold point via `far_frr_curve(scores, labels, n_thresholds=1)`. The function crashes with `ZeroDivisionError: division by zero`.
- **Suggested fix:** Guard against `n_thresholds < 2` or return `[(lo, far, frr)]` if `n_thresholds == 1`.

---

### [SEVERITY: low] Non-idempotent augmentation in `scripts/augment_stumper.py`
- **File:** `scripts/augment_stumper.py`, lines 58, 86–87
- **What's wrong:** `augment_stumper.py` filters source rows with `df["photo_id"].str.startswith(prefix)`. If executed more than once, it includes previously generated synthetic rows (`prefix_aug00`, etc.) in `source_rows`, and appends another 45 rows to `labels.csv`.
- **Concrete failure scenario:** Running `python scripts/augment_stumper.py` a second time doubles the synthetic photo count to 90 and appends duplicate entries to `labels.csv`.
- **Suggested fix:** Filter out synthetic rows before augmenting: `df[df["photo_id"].str.startswith(prefix) & ~df["conditions"].str.contains("synthetic")]`.

---

### [SEVERITY: low] Personal email exposed in `scrape.py` User-Agent
- **File:** `src/dyla_match/catalogue/scrape.py`, line 27
- **What's wrong:** Line 27 hardcodes `USER_AGENT = "dyla-takehome-catalogue-builder/0.1 (personal project, jaygautam561@gmail.com)"`.
- **Concrete failure scenario:** Pushing the repo publicly or sharing with reviewers exposes the author's private email address.
- **Suggested fix:** Parameterize the contact email via an environment variable or generic placeholder.

---

### [SEVERITY: low] Missing baseline configuration file `configs/dinov2.yaml`
- **File:** `configs/`
- **What's wrong:** `configs/` contains `clip.yaml`, `clip_crop.yaml`, `default.yaml`, and `dinov2_crop.yaml`, but lacks `dinov2.yaml` (plain DINOv2 without crop). `eval/report.md` documents the baseline DINOv2 run, but there is no dedicated config file to reproduce it without editing `default.yaml`.
- **Concrete failure scenario:** A user tries to run `python -m eval.harness --config configs/dinov2.yaml` to reproduce `eval/report.md`, and gets `FileNotFoundError`.
- **Suggested fix:** Create `configs/dinov2.yaml` with `backbone: dinov2`, `preprocess.object_crop: false`, and `index.dir: data/index`.
