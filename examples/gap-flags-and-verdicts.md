# Sample: What the engine flagged

> **Illustrative output.** The claim-level verdicts below are the machine-readable layer that ships
> alongside every draft. This is what "anti-hallucination" means in practice: the engine extracts
> each claim, matches it against your source documents, and tells you which parts you can trust and
> which parts need a human decision. Numbers are invented for this example.

## Claim verdicts from the sample draft

| Claim in draft | Verdict | Why |
|----------------|---------|-----|
| Scope 1+2 (market-based) fell 18% to 33,800 tCO₂e in FY2025 | `highly_reliable` | Exact match in Acme-CDP-Climate-2024.pdf p. 7 (figure + % both present) |
| Renewable electricity reached 74% of office/ops consumption | `mostly_reliable` | Figure found in ESG policy doc p. 6; scope of "consumption" ambiguous (op vs. total) |
| Net zero by 2045 is a public target | `highly_reliable` | Stated in annual report p. 12 |
| No lost-time incident for 14 months | `mostly_reliable` | Found in HS section p. 4; 14-month window not independently dated in source |
| Water withdrawal (FY2025) = 412,000 m³ | `unreliable` → **dropped** | No FY2025 water number exists in sources; draft wrote a gap note instead |
| Board ESG committee established FY2023 | `highly_reliable` | Annual report p. 41 governance section |

**Grounding score: 78/100** (weighted share of draft claims rated `highly_reliable`/`mostly_reliable`).

## What an "insufficient data" flag looks like inside the draft

> ⚠️ **Flagged gap:** Acme's FY2025 Scope 3 emissions were not reported in the provided sources.
> The draft below therefore excludes Scope 3 from the environmental summary rather than estimating it.

### Why this is a feature, not a defect

A generalist chatbot, asked to write the Scope 3 section, will usually invent a plausible-looking
number or a generic paragraph. ai4sustainablex is built to do the opposite:

1. It **searches your folder** for the number. If the source exists, the claim is written and cited.
2. If the number isn't there, it **writes the gap in place** and moves on — so the ESG team sees
   exactly what to chase down (the missing CDP response, the missing audit note).
3. It records a **verdict and confidence** for every claim, so a reviewer can spot-check the weak
   spots in minutes instead of re-reading everything.

### What reviewers should treat as the "manual" part

| Layer | Machine | Human |
|-------|---------|-------|
| Finding the source of a number | ✅ done (citation + page) | — |
| Judging whether the source is *authoritative* (audited vs. self-declared) | ⚠️ flagged | ✅ decide |
| Filling gaps from unindexed records | ❌ refused (gap note) | ✅ do it |
| Framework alignment (latest ESRS/IFRS amendments) | ⚠️ scaffold | ✅ verify |
| Sign-off | ❌ | ✅ |
