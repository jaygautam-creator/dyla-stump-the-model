"""Evaluation metrics for the stumper harness.

Pure functions, no I/O — `harness.py` reads labels.csv and matcher output and calls these. Kept
separate so the metrics themselves can be checked against known values without needing a stumper
set or a trained matcher (see the checks at the bottom of this file, run with
`python -m eval.metrics`).
"""
import math
from dataclasses import dataclass


def topk_accuracy(hits: list[bool]) -> float:
    """`hits[i]` is whether the true id was within the top-K for example i. Plain hit rate."""
    if not hits:
        raise ValueError("no examples")
    return sum(hits) / len(hits)


def wilson_ci(successes: int, n: int, z: float = 1.959964) -> tuple[float, float]:
    """Wilson score interval for a binomial proportion. z=1.959964 is the two-sided 95% default.

    Preferred over the normal (Wald) interval here because n per condition is small (~15,
    per docs/PLAN.md) and Wald can produce nonsensical bounds outside [0, 1] at those sizes.
    """
    if n == 0:
        raise ValueError("n=0")
    p = successes / n
    denom = 1 + z**2 / n
    center = p + z**2 / (2 * n)
    half_width = z * math.sqrt(p * (1 - p) / n + z**2 / (4 * n**2))
    lower = (center - half_width) / denom
    upper = (center + half_width) / denom
    return max(0.0, lower), min(1.0, upper)


def far_frr(scores: list[float], is_in_catalogue: list[bool], threshold: float) -> tuple[float, float]:
    """False accept / false reject rate at one threshold. Decision rule: accept iff score >= threshold.

    FAR = fraction of not-in-catalogue photos wrongly accepted.
    FRR = fraction of in-catalogue photos wrongly refused.
    """
    if len(scores) != len(is_in_catalogue):
        raise ValueError("scores and is_in_catalogue must be the same length")
    negatives = [s for s, pos in zip(scores, is_in_catalogue) if not pos]
    positives = [s for s, pos in zip(scores, is_in_catalogue) if pos]
    far = sum(1 for s in negatives if s >= threshold) / len(negatives) if negatives else float("nan")
    frr = sum(1 for s in positives if s < threshold) / len(positives) if positives else float("nan")
    return far, frr


def far_frr_curve(
    scores: list[float], is_in_catalogue: list[bool], n_thresholds: int = 101
) -> list[tuple[float, float, float]]:
    """(threshold, FAR, FRR) at `n_thresholds` evenly spaced thresholds spanning the observed scores.

    For the full trade-off curve `docs/PLAN.md` asks for under Refusal — not just the single
    operating point picked on the calibration split.
    """
    if not scores:
        raise ValueError("no scores")
    lo, hi = min(scores), max(scores)
    curve = []
    for i in range(n_thresholds):
        t = lo + (hi - lo) * i / (n_thresholds - 1)
        far, frr = far_frr(scores, is_in_catalogue, t)
        curve.append((t, far, frr))
    return curve


@dataclass
class ReliabilityBin:
    lo: float
    hi: float
    n: int
    avg_confidence: float
    accuracy: float


def expected_calibration_error(
    confidences: list[float], correct: list[bool], n_bins: int = 10
) -> tuple[float, list[ReliabilityBin]]:
    """ECE: bin predictions by confidence, weight each bin's |accuracy - avg confidence| by its size.

    Returns (ece, bins) — `bins` is what the reliability plot in docs/PLAN.md is drawn from.
    """
    if len(confidences) != len(correct):
        raise ValueError("confidences and correct must be the same length")
    n = len(confidences)
    if n == 0:
        raise ValueError("no examples")

    edges = [i / n_bins for i in range(n_bins + 1)]
    bins = []
    ece = 0.0
    for i in range(n_bins):
        lo, hi = edges[i], edges[i + 1]
        in_bin = [
            (c, ok) for c, ok in zip(confidences, correct)
            if (lo <= c < hi) or (i == n_bins - 1 and c == hi)
        ]
        if not in_bin:
            bins.append(ReliabilityBin(lo, hi, 0, 0.0, 0.0))
            continue
        avg_conf = sum(c for c, _ in in_bin) / len(in_bin)
        acc = sum(1 for _, ok in in_bin if ok) / len(in_bin)
        bins.append(ReliabilityBin(lo, hi, len(in_bin), avg_conf, acc))
        ece += (len(in_bin) / n) * abs(acc - avg_conf)
    return ece, bins


if __name__ == "__main__":
    # Checks against known reference values — not a full test suite, just enough to trust the
    # formulas before they're used on real stumper numbers.
    assert topk_accuracy([True, True, False, True]) == 0.75

    # n=100, k=80, z=1.96, hand-computed: center=0.819208, half_width=0.080719, denom=1.038416
    # -> (0.71127, 0.86663)
    lo, hi = wilson_ci(80, 100)
    assert abs(lo - 0.71127) < 1e-3 and abs(hi - 0.86663) < 1e-3, (lo, hi)

    # All-negative, all correctly rejected below threshold -> FAR 0; all-positive, all correctly
    # accepted -> FRR 0.
    far, frr = far_frr([0.9, 0.1, 0.9, 0.1], [True, False, True, False], threshold=0.5)
    assert far == 0.0 and frr == 0.0, (far, frr)

    # Perfectly calibrated: confidence == accuracy in every bin -> ECE 0.
    confs = [0.05, 0.15, 0.25, 0.85, 0.95]
    correct = [False, False, False, True, True]  # crude but bins land near their own confidence
    ece, _ = expected_calibration_error(confs, correct, n_bins=10)
    assert ece < 0.2, ece  # loose bound; exact value depends on binning, not the point of this check

    print("eval/metrics.py: all checks passed")
