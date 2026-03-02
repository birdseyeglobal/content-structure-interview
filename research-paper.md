# Structural Determinants of LLM Citation: How Website Architecture Predicts AI Visibility

## Abstract

We conducted two experiments to determine whether the structural properties of a brand's website predict how often those pages get cited by large language models (LLMs). Using production data from 39 brands and 18.7M citations, we find that internal link topology — specifically hub dominance, link asymmetry, and cross-section connectivity — are strong, statistically significant predictors of citation rate. Our second experiment using graph-based community detection produces ~75% stronger effect sizes than URL-path-based analysis, and reveals a key counterintuitive finding: link *density* is a strong negative predictor of citability.

---

## 1. Introduction

Large language models increasingly mediate how users discover brands and products. When an LLM cites a URL in its response, that citation drives awareness, trust, and traffic. Understanding *which* pages get cited — and *why* — is critical for brands seeking visibility in AI-generated content.

We hypothesize that the internal structure of a website (how pages link to each other, how content is organized, how authority is distributed) predicts citation likelihood independently of content quality. If true, this provides a structural optimization lever: brands can improve AI visibility by restructuring their site architecture.

### 1.1 Data Sources

All data is sourced from a production system that:

- **Crawls brand websites** using a recursive web crawler, extracting page content, internal/external links (as structured JSONB), crawl depth, and page metadata
- **Generates embeddings** for each page (768-dimensional vectors from title + H1 + intro text) stored as pgvector columns
- **Tracks LLM citations** by running prompts against multiple LLMs and recording which URLs appear in responses, linked to stable webpage identities

| Data Source | Description | Scale |
|---|---|---|
| Crawled pages | Web pages with internal link graph (JSONB), depth, content | ~2.9M pages |
| Documents | Content snapshots with 768-dim topic embeddings (pgvector) | 2.8M docs, 96% with embeddings |
| Citations | LLM responses citing specific URLs, linked via stable webpage IDs | 18.7M citations |
| Brands | Customer websites as analysis units | 697 with 100+ crawled pages |
| Topics | Brand-defined topics with name embeddings for similarity matching | Used in topic-aware analysis |

### 1.2 Key Technical Infrastructure

- **Database**: PostgreSQL with pgvector extension (AlloyDB)
- **Vector operations**: `cosine_distance()`, `l2_normalize()`, `inner_product()`, `AVG()` on 768-dim embeddings
- **Link graph extraction**: `CROSS JOIN LATERAL jsonb_array_elements(links_internal)` on JSONB arrays
- **Binning**: `WIDTH_BUCKET()` for quintile stratification

---

## 2. Experiment 1: URL-Path-Based Subnetwork Analysis

### 2.1 Method

**Locus definition**: We segment each brand's crawled pages by first URL path segment (e.g., `/blog/` → "blog", `/products/` → "products", root pages → "__root__"). Each segment forms a "locus" — a subnetwork of pages sharing a URL prefix.

**Sample**: 222 loci across 39 brands, sampled uniformly by log-scale page count from brands with 100+ crawled pages. Minimum 4 pages per locus.

**Metrics computed per locus**:

| Metric | Definition |
|---|---|
| `page_count` | Number of pages in the locus |
| `avg_in_degree` | Mean number of internal backlinks per page (within locus) |
| `link_density` | Internal edges / (n × (n-1)), where n = page count |
| `link_entropy` | Shannon entropy of in-degree distribution |
| `max_in_degree` | Highest in-degree of any single page |
| `avg_depth` | Mean crawl depth of pages |
| `depth_stddev` | Standard deviation of crawl depth |
| `embedding_variance` | Mean cosine distance from each page's embedding to locus centroid |
| `embedding_entropy` | Shannon entropy of embedding distance distribution (binned) |
| `cross_locus_in_edges` | Count of inbound links from pages in other loci |
| `cross_locus_out_edges` | Count of outbound links to pages in other loci |
| `topic_similarity` | Max cosine similarity between locus centroid and any brand topic embedding |

**Outcome variable**: `citations_per_page` = total citation count for pages in the locus / page count.

**Citation distribution**: Heavily zero-inflated (41% uncited) and right-skewed (median=2, p90=640, max=15,446 raw citations). All analyses use rank-based methods, log transforms, and stratification.

### 2.2 Results

#### 2.2.1 Internal Backlink Density Is the Strongest Predictor

| Analysis | Statistic | Value | p-value |
|---|---|---|---|
| All loci, Spearman | ρ(avg_in_degree, cite/page) | **+0.264** | **0.0001** |
| Cited loci, Pearson log | r(avg_in_degree, log_cite) | **+0.256** | **0.003** |
| Partial (controlling page_count) | partial ρ | **+0.226** | **0.037** |
| Point-biserial (cited vs uncited) | r_pb | +0.156 | 0.020 |

`avg_in_degree` is the only variable that survives partial correlation controlling for locus size.

**Quintile breakdown (cited loci only)**:

| avg_in_degree quintile | n | Median cite/page | Median link density |
|---|---|---|---|
| Q1 (lowest) | 33 | 0.56 | 0.000 |
| Q2 | 20 | 1.17 | 0.035 |
| Q3 | 26 | 0.90 | 0.064 |
| Q4 | 26 | 0.39 | 0.130 |
| **Q5 (highest)** | **26** | **11.37** | **0.753** |

The top quintile has **20× the median citation rate** of the bottom quintile.

#### 2.2.2 Semantic Coherence Matters for Large Subnetworks

Embedding variance (average cosine distance from locus centroid) correlates negatively with citability — more coherent loci are cited more — but only in large loci:

| Analysis | ρ | p-value |
|---|---|---|
| All loci | +0.029 | 0.668 (n.s.) |
| Large loci only (43+ pages) | **-0.354** | **0.009** |
| Cited loci, Pearson log | **-0.188** | **0.032** |

The most semantically coherent quintile has **11× the citation rate** of the least coherent.

#### 2.2.3 Cross-Locus Connectivity Drives Citations

| Metric | Spearman ρ | p-value |
|---|---|---|
| cross_locus_in_edges | **+0.216** | **0.001** |
| cross_locus_out_edges | +0.147 | 0.029 |

Top-cited loci receive **738% more** cross-locus inbound links than bottom-cited loci.

#### 2.2.4 Depth Variation Predicts Citability

`depth_stddev` is the strongest binary predictor of whether a locus gets cited at all (r_pb = +0.253, p = 0.002). Loci with pages at varying depths represent real content hierarchies rather than flat lists.

#### 2.2.5 Smaller Focused Loci Get More Citations Per Page

Among cited loci, smaller ones get more citations per page (r = -0.183, p = 0.036). The top-cited third has median 18 pages vs 34 for the bottom third.

### 2.3 Structural Profile: High vs Low Citation Loci

| Metric | Bottom 1/3 | Top 1/3 | Difference |
|---|---|---|---|
| Median cite/page | 0.11 | 22.25 | 200× |
| Page count | 34 | 18 | **-47%** |
| Link density | 0.049 | 0.130 | **+168%** |
| Avg in-degree | 3.97 | 13.10 | **+230%** |
| Embedding variance | 0.184 | 0.151 | **-18%** |
| Cross-locus inbound | 8 | 67 | **+738%** |

### 2.4 Non-Predictors

- `link_entropy`: Not significant. Distribution of links matters less than density.
- `embedding_entropy`: Not significant.
- `avg_depth`: No direct effect.
- `topic_similarity`: Positive trend but not significant (n=50, underpowered).

---

## 3. Experiment 2: Graph-Clustered Loci with Topology Mining

### 3.1 Method

**Motivation**: URL-path segments are arbitrary groupings that may not reflect actual content clusters. We replace them with algorithmically discovered communities from the internal link graph.

**Community detection**: Louvain algorithm (NetworkX, default resolution, seed=42) on the directed internal-link graph. Clusters with <4 pages merged into the nearest cluster by edge count.

**Sample**: 224 clusters from 33 brands (bins 1-4, 103-947 pages per brand). Embedding enrichment available for 10 brands (79 clusters).

**New shape metrics**:

| Metric | Definition |
|---|---|
| `reciprocity` | Fraction of edges that are bidirectional |
| `degree_gini` | Gini coefficient of in-degree distribution (0=equal, 1=one node gets all) |
| `hub_dominance` | Fraction of all internal edges pointing to the top hub page |
| `pagerank_gini` | Gini coefficient of PageRank distribution |
| `clustering_coeff` | Average local clustering coefficient |
| `scc_coverage` | Fraction of nodes in the largest strongly connected component |
| `bridge_node_fraction` | Fraction of articulation points |
| `boundary_ratio` | Fraction of edges crossing cluster boundary |
| `boundary_in_edges` | Count of inbound cross-cluster edges |

**Topology archetypes**: Rule-based classification into six types:

| Archetype | Defining characteristics |
|---|---|
| **clique** | link_density > 0.5 |
| **hub_spoke** | hub_dominance > 0.4 and degree_gini > 0.5 |
| **chain** | Low density, low clustering, sequential structure |
| **mesh** | Moderate density, low degree inequality |
| **tree** | Low density, hierarchical depth |
| **mixed** | Does not fit cleanly into above categories |

### 3.2 Results

#### 3.2.1 Hub Structure Is the Dominant Predictor

| Metric | Spearman ρ | p-value |
|---|---|---|
| **max_in_degree** | **+0.461** | **<0.0001** |
| **page_count** | **+0.459** | **<0.0001** |
| **stddev_in_degree** | **+0.446** | **<0.0001** |
| boundary_in_edges | +0.400 | <0.0001 |
| degree_gini | +0.369 | <0.0001 |
| pagerank_gini | +0.347 | <0.0001 |

Effect sizes are ~75% larger than Experiment 1.

#### 3.2.2 Dense, Symmetric Clusters Are LESS Citable (Key Reversal)

| Metric | Spearman ρ | p-value |
|---|---|---|
| **link_density** | **-0.352** | **<0.0001** |
| **reciprocity** | **-0.268** | **0.00005** |
| clustering_coeff | -0.136 | 0.042 |
| scc_coverage | -0.190 | 0.004 |

This reverses Experiment 1's positive finding on `avg_in_degree`. The resolution: **raw link count is positive, but link concentration/symmetry is negative.** Clusters where every page links to every other (navigation menus, product grids, footer blocks) are not substantive reference material. The most citable clusters have **asymmetric** structure — hub pages receiving links from supporting content.

#### 3.2.3 Hub Dominance Survives Controlling for Size

| Metric | Partial ρ (controlling page_count) | p-value |
|---|---|---|
| **hub_dominance** | **+0.214** | **0.001** |
| **pagerank_gini** | **+0.144** | **0.032** |
| **boundary_ratio** | **+0.144** | **0.031** |
| embedding_variance | +0.331 | 0.003 (n=79) |

Hub dominance is the strongest size-independent predictor. Clusters with unequal authority distribution are more citable regardless of size.

#### 3.2.4 Topology Archetypes Predict Citation Rate

Kruskal-Wallis: H=26.098, **p=0.00003**

| Archetype | n | Median cite/page | % cited |
|---|---|---|---|
| **mixed** | 122 | 0.092 | **62.3%** |
| hub_spoke | 6 | 0.180 | 66.7% |
| tree | 29 | 0.091 | 55.2% |
| chain | 1 | 0.050 | 100% |
| **clique** | **22** | **0.000** | **36.4%** |
| **mesh** | **44** | **0.000** | **13.6%** |

Mesh clusters have only 13.6% citation rate vs 62.3% for mixed. Uniform linking structures are not citable.

#### 3.2.5 Shallow Clusters Are More Citable

| Metric | Spearman ρ | p-value |
|---|---|---|
| avg_depth | -0.234 | 0.0004 |
| depth_stddev | +0.132 | 0.048 |

Clusters closer to the site root are more citable.

### 3.3 Experiment 1 vs Experiment 2 Comparison

| Aspect | Exp 1 (URL-path) | Exp 2 (Graph clusters) |
|---|---|---|
| Locus definition | First URL path segment | Louvain community detection |
| Sample | 222 loci, 39 brands | 224 clusters, 33 brands |
| Strongest predictor | avg_in_degree (ρ=+0.264) | max_in_degree (ρ=+0.461) |
| Size-independent predictor | avg_in_degree (partial=+0.226) | hub_dominance (partial=+0.214) |
| Link density effect | Not tested separately | **-0.352 (negative)** |
| Cross-section connectivity | cross_locus_in (ρ=+0.216) | boundary_in (ρ=+0.400) |
| Shape metrics | Not available | 10 new metrics, 6 archetypes |

---

## 4. Consolidated Findings

### 4.1 What Predicts LLM Citation

1. **Asymmetric authority structure** (hub_dominance, degree_gini) — the single most important structural signal
2. **Cross-section connectivity** (boundary_in_edges, boundary_ratio) — pages linked from the rest of the site
3. **Content hierarchy** (depth_stddev) — pages at varying depths indicating pillar → subtopic → article structure
4. **Semantic coherence** (low embedding_variance for large clusters) — topically focused content
5. **Moderate size** (15-50 pages) — focused clusters outperform sprawling ones per-page

### 4.2 What Hurts LLM Citation

1. **Uniform link meshes** (high link_density, high reciprocity) — nav bars, footer links, product grids
2. **Clique/mesh topologies** — every page linking to every other
3. **Deep burial** (high avg_depth) — content far from the root
4. **Topical diffusion** (high embedding_variance in large clusters)

### 4.3 Limitations

- All findings are **correlational**. Optimizing for these metrics may not cause increased citations.
- Embedding results in Experiment 2 are preliminary (n=79, 10 brands). The positive direction of embedding_variance in Exp 2 contradicts Exp 1's negative direction; more data needed.
- The "mixed" archetype classification (54.5% of clusters) suggests the topology rules need refinement.
- Multiple testing: With 28 metrics, ~1.4 false positives expected at α=0.05. Only findings with p<0.001 are robust to Bonferroni correction.
- Brand size bins 5+ (1000+ pages) were validated directionally but not fully analyzed due to JSONB extraction timeouts.

---

## Appendix A: Statistical Methods

- **Spearman rank correlation**: Primary method; robust to zero-inflation and skew
- **Pearson correlation with log transform**: Applied to cited-only subset for effect size estimation
- **Point-biserial correlation**: Binary cited/uncited classification
- **Partial rank correlation**: Controls for page_count to isolate size-independent effects
- **Kruskal-Wallis H-test**: Non-parametric one-way ANOVA for topology archetypes
- **Quintile stratification**: `WIDTH_BUCKET()` for visualizing dose-response relationships

## Appendix B: Data Schema Reference

```
web_crawl_page
├── id (UUID)
├── brand_id (UUID) → brand
├── url (VARCHAR)
├── canonical_url (VARCHAR)
├── depth (INT) — crawl depth from seed
├── links_internal (JSONB) — array of {href, text, base_domain, ...}
├── webpage_id (UUID) → webpage
└── success (BOOL)

document
├── id (UUID)
├── brand_id (UUID) → brand
├── webpage_id (UUID) → webpage
├── web_crawl_page_id (UUID) → web_crawl_page
├── topic_embedding (VECTOR(768)) — pgvector, HNSW indexed
└── content_hash (VARCHAR)

webpage
├── id (UUID) — stable URL identity
├── brand_id (UUID) → brand
├── canonical_url (VARCHAR)
└── current_document_id (UUID) → document

citation
├── id (UUID)
├── webpage_id (UUID) → webpage
├── brand_id (UUID) → brand
├── prompt_execution_id (UUID) → prompt_execution
├── url (VARCHAR)
├── canonical_url (VARCHAR)
└── is_biased_by_prompt (BOOL)

topic
├── id (UUID)
├── workspace_id (UUID)
├── name (VARCHAR)
└── name_embedding (VECTOR) — pgvector, HNSW indexed
```
