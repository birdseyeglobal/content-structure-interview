# PRD: Content Structure Intelligence

## Overview

Build a system that analyzes a brand's website structure, scores it against empirically validated predictors of LLM citation, generates actionable recommendations, and can directly optimize content structure.

This is a **progressive design and implementation exercise** with three phases of increasing complexity.

---

## Background

Our research (see attached paper) analyzed 18.7M LLM citations across ~2.9M crawled pages and found that internal link topology is a strong, statistically significant predictor of whether LLMs cite a brand's pages. The key findings:

- **Hub dominance** (asymmetric authority structure) is the strongest size-independent predictor of citation rate
- **Link density/reciprocity** are *negative* predictors — uniform link meshes (nav bars, product grids) are the least citable content structures
- **Cross-section connectivity** (links from other parts of the site) increases citability by up to 738%
- **Content hierarchy** (depth variation) is the strongest predictor of whether content gets cited at all
- **Topology archetypes** (hub_spoke, tree, mesh, clique, mixed) significantly predict citation rate (p=0.00003)

We want to turn these findings into a product feature.

---

## Data Available

You have access to the following production data:

| Table | Key Fields | Notes |
|---|---|---|
| `web_crawl_page` | `brand_id`, `url`, `canonical_url`, `depth`, `links_internal` (JSONB array of link objects with `href`, `text`), `webpage_id` | The raw link graph |
| `document` | `brand_id`, `webpage_id`, `web_crawl_page_id`, `topic_embedding` (768-dim pgvector) | Semantic embeddings |
| `webpage` | `id`, `brand_id`, `canonical_url`, `current_document_id` | Stable URL identity |
| `citation` | `webpage_id`, `brand_id`, `url`, `canonical_url` | LLM citation records |
| `topic` | `name`, `name_embedding` (pgvector), `workspace_id` | Brand-defined topics |

**Join path**: `web_crawl_page` → `webpage` (via `webpage_id`) ← `citation` (via `webpage_id`)

**Embedding access**: `document.topic_embedding` is a 768-dim vector with HNSW cosine index. Use `cosine_distance()`, `l2_normalize()`, and vector `AVG()` for centroid computation.

**Link graph extraction**: Each `web_crawl_page.links_internal` is a JSONB array. Use `jsonb_array_elements()` to extract individual links. Each link has at minimum an `href` field.

---

## Phase 1: Content Structure Score

### Objective

Given a brand, analyze its crawled pages and produce a **per-cluster content structure score** that predicts LLM citability based on the structural metrics from the research.

### Requirements

#### P1-R1: Graph Construction
- **Given**: A brand's crawled pages with their internal links
- **Produce**: A directed graph where nodes are pages and edges are internal links
- **Constraints**: Handle self-links, links to uncrawled pages, duplicate links, and pages with no links

#### P1-R2: Cluster Identification
- Partition the graph into content clusters (loci)
- You may use URL-path segmentation, graph-based community detection (e.g., Louvain), or a hybrid approach
- Minimum cluster size: 4 pages
- Document your choice and its tradeoffs

#### P1-R3: Structural Metric Computation
For each cluster, compute at minimum:

| Metric | Definition | Research finding |
|---|---|---|
| `page_count` | Number of pages | Larger clusters more citable (ρ=+0.459) |
| `avg_in_degree` | Mean internal backlinks per page | Positive predictor (ρ=+0.264) |
| `link_density` | Edges / max possible edges | **Negative** predictor (ρ=-0.352) |
| `hub_dominance` | Fraction of edges pointing to top page | Strongest size-independent predictor (partial ρ=+0.214) |
| `boundary_in_edges` | Inbound links from other clusters | Strong positive (ρ=+0.400) |
| `depth_stddev` | Std dev of page depths | Predicts citation existence (r_pb=+0.253) |

Optional but valuable:
- `reciprocity`, `degree_gini`, `pagerank_gini`, `clustering_coeff`
- `embedding_variance` (requires vector operations)
- Topology archetype classification

#### P1-R4: Composite Score
- Combine metrics into a single 0-100 score per cluster
- Account for the zero-inflation problem (41-50% of clusters are uncited)
- Normalize across different cluster sizes
- Justify your weighting/combination method

#### P1-R5: Brand-Level Summary
- Aggregate cluster scores into a brand-level content structure health score
- Identify the brand's strongest and weakest clusters

### User Stories

- **US-1.1**: As a brand manager, I can see a content structure score for my entire site so I know my overall structural health.
- **US-1.2**: As a brand manager, I can see scores broken down by content cluster so I know which sections of my site are structurally strong or weak.
- **US-1.3**: As a brand manager, I can see which specific structural metrics are driving my score up or down, so I understand *why* my score is what it is.

### Acceptance Criteria

- [ ] Given a brand with 100-500 crawled pages, the system produces cluster scores within 30 seconds
- [ ] Scores are reproducible (same input → same output)
- [ ] The scoring method is documented with justification tied to the research findings
- [ ] Edge cases handled: brands with <4 pages per cluster, pages with no internal links, disconnected subgraphs

---

## Phase 2: Content Structure Recommendations

### Objective

Given a brand's cluster scores and the underlying link graph, generate **specific, prioritized, actionable recommendations** for improving content structure.

### Requirements

#### P2-R1: Recommendation Taxonomy
Define and implement at least 4 recommendation types:

| Type | When to trigger | Example output |
|---|---|---|
| `add_internal_links` | Low hub_dominance or avg_in_degree | "Add links from pages [A, B, C] to hub page [X]" |
| `create_hub_page` | Cluster has no clear authority page | "Create a hub page for the '/pricing' cluster linking to [list of pages]" |
| `reduce_link_symmetry` | High reciprocity or link_density, mesh/clique topology | "The '/products' cluster has mesh topology (13.6% citation rate). Restructure as hub-spoke." |
| `improve_cross_section_links` | Low boundary_in_edges or boundary_ratio | "Connect cluster '/blog' to cluster '/case-studies' — they share semantic theme X" |
| `consolidate_cluster` | High embedding_variance in large cluster | "Split '/resources' into 2 focused sub-clusters based on topic similarity" |
| `promote_depth` | Low depth_stddev | "Add intermediate category pages to create a content hierarchy" |

#### P2-R2: Specificity
Each recommendation must reference:
- The target cluster and its current score
- Specific pages involved (URLs)
- The structural metric being addressed
- The expected score improvement (quantified)

#### P2-R3: Prioritization
Rank recommendations by **impact × feasibility**:
- **Impact**: How much would the score improve? Use the research quintile data to estimate (e.g., moving from Q1 to Q3 of hub_dominance)
- **Feasibility**: How many pages need to change? How complex is the change?
- Recommendations should not conflict with each other

#### P2-R4: Dependency Awareness
- Changing one cluster's structure affects neighboring clusters (boundary metrics)
- The system should flag when recommendations interact

### User Stories

- **US-2.1**: As a brand manager, I see a prioritized list of recommendations for improving my content structure, with the highest-impact items first.
- **US-2.2**: As a content strategist, I see specific pages I should link together, so I can take action immediately without further analysis.
- **US-2.3**: As a brand manager, I can see the expected score improvement for each recommendation so I can decide which ones are worth the effort.
- **US-2.4**: As a content strategist, I am warned when two recommendations interact with each other so I don't make conflicting changes.

### Acceptance Criteria

- [ ] At least 4 distinct recommendation types implemented
- [ ] Each recommendation includes specific page URLs and expected metric impact
- [ ] Recommendations are sorted by priority
- [ ] No two recommendations in the list directly contradict each other
- [ ] Recommendations reference the research findings that motivate them

---

## Phase 3: Direct Content Structure Optimization

### Objective

The system can **directly modify** a brand's content structure — inserting internal links, proposing page reorganizations, generating hub page outlines — with safety constraints and impact simulation.

### Requirements

#### P3-R1: Change Simulation
Before applying any change:
- Build the proposed link graph (current graph + proposed modifications)
- Recompute all structural metrics on the proposed graph
- Compare before/after scores
- Reject changes that decrease the overall score or violate constraints

#### P3-R2: Semantic Validation
Link insertions must be semantically valid:
- Use page embeddings (`document.topic_embedding`) to verify that source and target pages are topically related
- Define a minimum similarity threshold
- Generate contextually appropriate anchor text based on the target page's content

#### P3-R3: Optimization Strategy
For a given cluster, identify the optimal set of link modifications:
- Select the best hub candidate (highest existing in-degree, or best embedding centrality within the cluster)
- Identify supporting pages that should link to the hub but don't
- Rank candidate links by expected impact (metric improvement per link added)
- Apply diminishing returns — the marginal value of each additional link decreases

#### P3-R4: Safety Constraints
- Maximum number of links added per page per optimization pass
- No links that would create the negative patterns identified in the research (increasing link_density beyond a threshold, creating reciprocal mesh structures)
- Human-reviewable change sets: output must be auditable before application
- Rollback capability: all changes can be undone

#### P3-R5: Second-Order Effects
- Adding links to one cluster changes boundary metrics for adjacent clusters
- The optimizer should consider the global impact, not just per-cluster optimization
- Flag cases where optimizing cluster A would degrade cluster B

#### P3-R6: Feedback Loop Design
- After changes are applied and new citation data is collected, compare actual citation changes to predicted impact
- Track whether the correlational findings from the research translate to causal improvements
- Design the measurement framework (what to measure, how long to wait, what constitutes success)

### User Stories

- **US-3.1**: As a brand manager, I can preview proposed structural changes and see the simulated impact on my scores before anything is applied.
- **US-3.2**: As a content strategist, I receive specific link insertion suggestions with auto-generated anchor text that I can approve or reject one by one.
- **US-3.3**: As a brand manager, I can see when optimizing one section of my site would negatively impact another section.
- **US-3.4**: As a product owner, I can measure whether structural optimizations actually improved LLM citation rates over time, so I know the recommendations are working.

### Acceptance Criteria

- [ ] Changes are simulated before application with before/after metric comparison
- [ ] Link suggestions are validated for semantic relevance using embeddings
- [ ] The system identifies diminishing returns and stops adding links when marginal impact drops below a threshold
- [ ] No optimization pass can increase link_density or reciprocity above research-identified negative thresholds
- [ ] Change sets are human-reviewable (not auto-applied)
- [ ] The system flags second-order effects on neighboring clusters

---

## Evaluation Notes for Interviewer

### Phase 1 focuses on:
- Data modeling and graph construction
- Translating research findings into computable metrics
- Handling messy real-world data (zero-inflation, skew, missing data)
- Justifying design decisions with evidence

### Phase 2 focuses on:
- Going from data to actionable output
- Prioritization and ranking logic
- Specificity — vague recommendations are not useful
- Awareness of interactions between recommendations

### Phase 3 focuses on:
- Systems thinking — second-order effects, global vs local optimization
- Safety and reversibility
- Distinguishing correlation from causation
- Feedback loop design and measurement

### What strong candidates demonstrate:
- They question the research (sample bias, correlational limitations, contradictions between experiments)
- They make explicit tradeoffs (URL-path vs graph clustering, speed vs accuracy)
- Their recommendations are specific enough to act on (page URLs, not abstract advice)
- They simulate before they commit
- They acknowledge what they don't know (will optimizing for these metrics *cause* more citations?)
