# PRD: Content Structure Intelligence

## Overview

We want to help brands understand and improve how their website structure affects their visibility in AI-generated responses. Our research (see attached paper) has established that the way pages link to each other within a site is a strong predictor of whether LLMs cite those pages. We want to turn these findings into a product.

This is a **progressive design and implementation exercise** with three phases of increasing complexity.

---

## Context

### The Problem

Brands have no visibility into whether their website's internal structure helps or hurts their chances of being cited by LLMs. They invest heavily in content quality but have no tools to evaluate or improve their site's structural health from an AI discoverability perspective.

### What We Know

Our research analyzed millions of LLM citations and crawled pages. The key findings are in the attached research paper. In summary:

- How pages link to each other within a site strongly predicts citation rates
- Not all linking is good — some link patterns actively hurt citability
- Pages that are structurally well-positioned (clear authority hierarchy, cross-section visibility, topical coherence) get cited significantly more
- These structural signals are independent of content quality

### What We Have

We operate an existing platform that:

- **Crawls customer websites** — we have each page's content, its links to other pages on the same site, and how deep it sits in the site hierarchy
- **Tracks LLM citations** — we monitor which customer pages get cited in AI responses and how often
- **Generates content embeddings** — we compute semantic vectors for each page's content, enabling similarity and coherence analysis

The candidate should assume this data exists and design systems that consume it. How they choose to model, transform, and structure this data for their system is part of the design exercise.

---

## Phase 1: Content Structure Score

### Goal

Give brands a clear, interpretable score that reflects how well their site's internal structure supports LLM citability.

### Requirements

**R1.1** — The system must analyze a brand's website and produce a **site-level content structure score** that communicates overall structural health.

**R1.2** — The system must break the site into meaningful **content sections** and score each one independently, so brands can see which parts of their site are structurally strong or weak.

**R1.3** — For each section, the system must surface the **specific structural factors** contributing to its score — both positive and negative — so the brand understands *why* the score is what it is.

**R1.4** — Scores must be grounded in the research findings. The candidate should justify which structural signals they incorporate and how they weight them.

**R1.5** — The scoring system must handle the reality that most content sections on most sites will have zero or very few citations. The score should still be meaningful for uncited sections.

### User Stories

- As a brand manager, I can see a single score that tells me how structurally healthy my site is for AI visibility, so I know whether I need to take action.
- As a brand manager, I can see which sections of my site are structurally strong and which are weak, so I know where to focus.
- As a brand manager, I can see what's driving each section's score up or down, so I understand the problem before trying to fix it.

### Acceptance Criteria

- Given a brand with several hundred pages, the system produces scores in a reasonable timeframe
- Scores are deterministic — same input produces the same output
- The scoring rationale is explainable and tied to research findings
- The system degrades gracefully when data is sparse (few pages, few links, missing embeddings)

---

## Phase 2: Content Structure Recommendations

### Goal

Go beyond scoring to tell brands *what to do* — generate specific, prioritized, actionable recommendations for improving their content structure.

### Requirements

**R2.1** — The system must generate **specific recommendations** — not generic advice like "add more links," but concrete actions referencing actual pages or sections on the brand's site.

**R2.2** — Recommendations must be **categorized by type** so brands understand the nature of each suggested change (e.g., linking changes vs. content organization vs. new content creation).

**R2.3** — Recommendations must be **prioritized** by expected impact. Brands have limited resources — they need to know what to fix first.

**R2.4** — Each recommendation must include an **estimated impact** — how much would implementing this recommendation improve the score?

**R2.5** — The system must account for **interactions between recommendations**. Structural changes in one part of the site can affect other parts. The system should warn when recommendations conflict or when implementing one changes the priority of another.

### User Stories

- As a brand manager, I see a prioritized list of recommendations with the highest-impact items first, so I can plan my team's work.
- As a content strategist, I see exactly which pages to modify and how, so I can take action without further analysis.
- As a brand manager, I can see the expected score improvement for each recommendation, so I can decide which are worth the effort.
- As a content strategist, I am warned when recommendations interact with each other, so I don't make conflicting changes.

### Acceptance Criteria

- Recommendations reference specific pages or sections by URL
- Each recommendation has a type, a priority rank, and an estimated score impact
- No two recommendations in the output directly contradict each other
- Recommendations are grounded in the research — each one should trace back to a finding

---

## Phase 3: Direct Content Structure Optimization

### Goal

Move from advice to action — the system can propose and simulate concrete structural changes to a brand's site, with appropriate safety guardrails.

### Requirements

**R3.1** — The system must be able to **propose specific structural edits** to the site (e.g., specific links to add between specific pages, pages to reorganize, new hub content to create).

**R3.2** — Before any change is applied, the system must **simulate its impact** — show the brand what their scores would look like after the change, before they commit.

**R3.3** — Proposed changes must be **semantically valid** — you can't just link any page to any other page. The system must ensure that suggested connections make sense given the content of the pages involved.

**R3.4** — The system must enforce **safety constraints** — it should not propose changes that would create the structural anti-patterns identified in the research. It should recognize diminishing returns.

**R3.5** — The system must account for **second-order effects** — optimizing one section of the site can degrade another. The system should surface these tradeoffs.

**R3.6** — Change proposals must be **human-reviewable** — the system presents a changeset that a human approves, not a black box that auto-applies changes.

**R3.7** — The system must include a **feedback loop design** — after changes are applied, how do we measure whether they actually improved citations? The research is correlational; the system should help us learn whether these optimizations are causal.

### User Stories

- As a brand manager, I can preview exactly what the system wants to change and see the projected score impact before anything is applied.
- As a content strategist, I receive specific edit suggestions (e.g., "add a link from page X to page Y with this anchor text") that I can approve or reject individually.
- As a brand manager, I can see when optimizing one section would negatively impact another section.
- As a product owner, I can measure whether optimizations actually improved citation rates over time, so I know the system is working.

### Acceptance Criteria

- Every proposed change includes a before/after score comparison
- Link suggestions are validated for topical relevance
- The system identifies and communicates diminishing returns
- The system prevents changes that would introduce known negative structural patterns
- All changesets are human-reviewable
- The design includes a measurement framework for validating causal impact

---

## What This Document Does NOT Specify

The following are intentionally left to the candidate to design:

- **Data modeling** — How you structure, transform, and store the data is your decision. The platform provides crawled pages, links, embeddings, and citations. How you model these for your system is part of the exercise.
- **Algorithm choices** — How you identify content sections, what graph algorithms you use, how you compute similarity — these are design decisions you should make and justify.
- **Metric definitions** — The research identifies many structural signals. Which ones you use, how you compute them, and how you combine them into scores is up to you.
- **Architecture** — Whether this is a batch pipeline, a real-time service, or something else is your call.
- **Technology choices** — Use whatever language, framework, or libraries you prefer.
