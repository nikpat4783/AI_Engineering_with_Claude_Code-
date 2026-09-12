import statistics
from .schema import Citation, ConfidenceBreakdown


def compute_confidence(citations: list[Citation]) -> ConfidenceBreakdown:
    n = len(citations)

    if n == 0:
        return ConfidenceBreakdown(
            score=0.0,
            level="none",
            num_supporting_sources=0,
            mean_relevance_score=0.0,
            agreement=0.0,
            stale_penalty_applied=False,
            rationale="No citations provided."
        )

    scores = [c.relevance_score for c in citations]
    mean_score = statistics.mean(scores)

    if n == 1:
        agreement = 0.0
    else:
        score_stdev = statistics.pstdev(scores)
        agreement = max(0.0, 1.0 - (score_stdev / mean_score)) if mean_score > 0 else 0.0

    corroboration_factor = min(1.0, n / 2.0)
    stale_fraction = sum(1 for c in citations if c.status == "stale") / n
    base_score = mean_score * (0.6 + 0.4 * agreement) * corroboration_factor
    final_score = max(0.0, base_score * (1.0 - 0.5 * stale_fraction))
    final_score = round(final_score, 3)

    if final_score >= 0.7:
        level = "high"
    elif final_score >= 0.4:
        level = "medium"
    else:
        level = "low"

    rationale = f"Score based on {n} source(s), mean relevance {round(mean_score, 2)}, " \
                f"agreement {round(agreement, 2)}, corroboration {round(corroboration_factor, 2)}"
    if stale_fraction > 0:
        rationale += f", stale penalty {round(0.5 * stale_fraction, 2)}"

    return ConfidenceBreakdown(
        score=final_score,
        level=level,
        num_supporting_sources=n,
        mean_relevance_score=round(mean_score, 3),
        agreement=round(agreement, 3),
        stale_penalty_applied=stale_fraction > 0,
        rationale=rationale
    )
