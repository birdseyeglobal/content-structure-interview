"""
Simulate LLM citations based on structural signals from the research.

Each page receives 100 "views" (simulated LLM queries where the page was a
retrieval candidate). Each view has a citation probability derived from the
page's structural context — its cluster's topology, the page's role within
that cluster, and cross-section connectivity.

The simulator produces a realistic citation distribution:
- Zero-inflated (many pages get 0 citations, matching 41-50% from research)
- Right-skewed (a few hub pages get many citations)
- Correlated with the structural metrics identified in the research

Input:  data/pages.json
Output: data/citations.json

Each citation: {query, cited_url, context}
"""

import json
import math
import random
from collections import defaultdict
from pathlib import Path

random.seed(42)

VIEWS_PER_PAGE = 100

# ── Load pages ───────────────────────────────────────────────────────────────

with open(Path("data/pages.json")) as f:
    raw_pages = json.load(f)

url_set = {p["url"] for p in raw_pages}
pages_by_url = {p["url"]: p for p in raw_pages}


# ── Build directed graph ─────────────────────────────────────────────────────

in_degree: dict[str, int] = defaultdict(int)
out_degree: dict[str, int] = defaultdict(int)
inbound: dict[str, set[str]] = defaultdict(set)    # url -> set of pages linking TO it
outbound: dict[str, set[str]] = defaultdict(set)    # url -> set of pages it links TO

for p in raw_pages:
    src = p["url"]
    for dst in p["links"]:
        if dst in url_set:
            in_degree[dst] += 1
            out_degree[src] += 1
            inbound[dst].add(src)
            outbound[src].add(dst)


# ── Cluster by first URL path segment ────────────────────────────────────────

def get_cluster(url: str) -> str:
    path = url.replace("https://acme.com/", "")
    segment = path.split("/")[0] if path else "root"
    return segment if segment else "root"


clusters: dict[str, list[str]] = defaultdict(list)
for url in url_set:
    clusters[get_cluster(url)].append(url)


# ── Compute per-cluster structural metrics ────────────────────────────────────

class ClusterMetrics:
    def __init__(self, name: str, urls: list[str]):
        self.name = name
        self.urls = set(urls)
        self.n = len(urls)

        # Intra-cluster edges
        self.intra_edges = 0
        self.reciprocal_edges = 0
        for u in urls:
            for v in outbound.get(u, set()):
                if v in self.urls:
                    self.intra_edges += 1
                    if u in outbound.get(v, set()):
                        self.reciprocal_edges += 1

        max_edges = self.n * (self.n - 1) if self.n > 1 else 1

        # Core metrics from research
        intra_in = {u: sum(1 for src in inbound.get(u, set()) if src in self.urls) for u in urls}
        self.avg_in_degree = sum(intra_in.values()) / self.n if self.n else 0
        self.max_in_degree = max(intra_in.values()) if intra_in else 0
        self.link_density = self.intra_edges / max_edges
        self.hub_dominance = self.max_in_degree / self.intra_edges if self.intra_edges > 0 else 0
        self.reciprocity = self.reciprocal_edges / self.intra_edges if self.intra_edges > 0 else 0

        # Cross-cluster (boundary) edges
        self.boundary_in = sum(
            1 for u in urls
            for src in inbound.get(u, set())
            if src not in self.urls
        )
        self.boundary_out = sum(
            1 for u in urls
            for dst in outbound.get(u, set())
            if dst not in self.urls
        )

        # Depth proxy: URL path depth
        depths = [u.replace("https://acme.com/", "").count("/") for u in urls]
        mean_depth = sum(depths) / len(depths) if depths else 0
        self.depth_stddev = math.sqrt(sum((d - mean_depth) ** 2 for d in depths) / len(depths)) if depths else 0

        # Per-page in-degree (intra) for page-level scoring
        self.page_in_degree = intra_in

        # Degree Gini
        degrees = sorted(intra_in.values())
        if sum(degrees) > 0:
            n = len(degrees)
            numerator = sum((2 * (i + 1) - n - 1) * d for i, d in enumerate(degrees))
            self.degree_gini = numerator / (n * sum(degrees))
        else:
            self.degree_gini = 0


cluster_metrics = {name: ClusterMetrics(name, urls) for name, urls in clusters.items()}


# ── Citation probability model ────────────────────────────────────────────────
# Maps structural metrics to a per-page citation probability.
#
# The model captures the research findings:
#   - Hub dominance (positive, strongest)       → high hub_dom = higher base prob
#   - Link density (negative)                   → high density = lower base prob
#   - Cross-section connectivity (positive)     → boundary_in boosts prob
#   - Depth variation (positive)                → depth_stddev boosts prob
#   - Reciprocity (negative)                    → high reciprocity = lower prob
#   - Page-level: hub pages (high in-degree) get cited more than spokes
#   - Zero-inflation: many pages in bad clusters get 0 probability

def sigmoid(x: float) -> float:
    """Squash to (0, 1)."""
    return 1.0 / (1.0 + math.exp(-x))


def cluster_base_score(m: ClusterMetrics) -> float:
    """Compute a cluster-level citation affinity score in (-inf, +inf).

    Calibrated so that:
    - Clique/mesh clusters (resources, products) score strongly negative
    - Sparse/flat clusters (about, pricing) score near zero
    - Well-structured hubs (solutions, blog) score positive
    - The overall cited-page rate lands around 50-60%
    """
    score = 0.0

    # Hub dominance: strong positive (research: partial rho = +0.214)
    # Range: 0-1. Well-structured clusters ~0.2-0.5, mesh ~0.02
    score += 4.0 * m.hub_dominance

    # Link density: strong negative (research: rho = -0.352)
    # Range: 0-1. Cliques = 1.0, mesh ~0.23, good clusters ~0.02-0.08
    score -= 6.0 * m.link_density

    # Reciprocity: negative (research: rho = -0.268)
    score -= 2.0 * m.reciprocity

    # Degree Gini: positive (research: rho = +0.369) — inequality is good
    score += 2.0 * m.degree_gini

    # Cross-section connectivity: positive (research: rho = +0.400)
    boundary_per_page = m.boundary_in / m.n if m.n > 0 else 0
    score += 1.5 * min(boundary_per_page, 2.0)

    # Depth variation: positive (research: r_pb = +0.253)
    score += 1.0 * min(m.depth_stddev, 1.0)

    return score


def page_citation_probability(url: str, cluster_name: str) -> float:
    """Compute per-page citation probability for 100 views.

    Target distribution:
    - ~40-50% of pages should have 0 citations (prob < ~5%)
    - Hub pages in good clusters: 30-70% per view
    - Leaf pages in bad clusters: 0-3% per view
    """
    m = cluster_metrics[cluster_name]
    base = cluster_base_score(m)

    # Page-level modifier: hub pages get cited much more
    page_in = m.page_in_degree.get(url, 0)
    total_in = in_degree.get(url, 0)  # includes cross-cluster
    if m.max_in_degree > 0:
        hub_factor = page_in / m.max_in_degree
    else:
        hub_factor = 0

    # Hub pages get a strong boost; leaf pages get penalized
    page_score = base + 3.0 * hub_factor

    # Pages with zero inbound links (orphans) are almost never cited
    if total_in == 0:
        page_score -= 5.0
    elif page_in == 0:
        # Has cross-cluster links but no intra-cluster links
        page_score -= 2.5

    # Leaf pages in bad clusters get extra penalty
    # (mesh/clique leaves have high density but no individual authority)
    if m.link_density > 0.15 and hub_factor < 0.1:
        page_score -= 2.0

    # Cross-cluster inbound links boost individual pages
    cross_in = total_in - page_in
    if cross_in > 0:
        page_score += 0.5 * min(cross_in, 5)

    # Convert to probability via sigmoid
    # Shift of 2.0 means score=0 → ~12% prob, score=-2 → ~2%, score=+2 → ~50%
    prob = sigmoid(page_score - 2.0)

    # Apply floor and ceiling
    prob = max(0.0, min(0.75, prob))

    # Zero-gate: pages with low structural scores may never enter the LLM's
    # retrieval index at all. This produces the zero-inflation seen in the
    # research (41-50% of loci uncited).
    # Below threshold, there's a probability the page is simply invisible.
    if prob < 0.25:
        # Quadratic ramp: prob=0.25 → 100%, prob=0 → 0%
        # Quadratic makes it harder for marginal pages to be visible
        visibility_chance = (prob / 0.25) ** 2
        if random.random() > visibility_chance:
            return 0.0

    return prob


# ── Query templates ───────────────────────────────────────────────────────────
# Realistic queries that an LLM might receive, organized by the topic area
# that would make each cluster's pages relevant retrieval candidates.

query_templates = {
    "blog": [
        "What is {topic} and how does it affect brand visibility?",
        "How should I approach {topic} for my website?",
        "What are the best practices for {topic}?",
        "Explain {topic} in the context of AI search optimization",
        "What's the difference between {topic} and traditional SEO?",
        "How do I improve my site's {topic}?",
        "What role does {topic} play in content discovery?",
        "Why is {topic} important for AI citations?",
    ],
    "products": [
        "What tools are available for AI search {topic}?",
        "Compare AI search {topic} platforms",
        "What features should an AI {topic} tool have?",
        "Best {topic} software for enterprise teams",
        "How do {topic} tools work?",
    ],
    "docs": [
        "How do I configure {topic} in the Acme platform?",
        "What is the {topic} API endpoint?",
        "Acme documentation for {topic}",
        "How to set up {topic} step by step",
        "Troubleshooting {topic} issues",
    ],
    "case-studies": [
        "How did companies in {topic} improve their AI visibility?",
        "What results can {topic} brands expect from content structure optimization?",
        "Case study: {topic} company AI search success",
        "Real-world examples of {topic} AI optimization",
        "ROI of content structure for {topic} companies",
    ],
    "resources": [
        "What does {topic} mean in AI search?",
        "Download a guide to {topic}",
        "Compare {topic} approaches for AI visibility",
        "{topic} benchmark data for my industry",
        "Evaluation checklist for {topic}",
    ],
    "pricing": [
        "How much does AI search optimization software cost?",
        "What's included in the {topic} plan?",
        "Compare AI search tool pricing options",
        "Enterprise pricing for AI visibility tools",
    ],
    "solutions": [
        "How can I improve my brand's {topic}?",
        "What solutions exist for {topic}?",
        "Best approach to {topic} for content teams",
        "Tools for measuring and improving {topic}",
        "How does {topic} affect AI citation rates?",
    ],
    "about": [
        "What is Acme and what do they do?",
        "Tell me about Acme's {topic}",
        "Who is behind the Acme platform?",
    ],
    "integrations": [
        "Does Acme integrate with {topic}?",
        "How to connect {topic} to an AI search platform",
        "Best AI search tool for {topic} users",
        "{topic} integration for AI visibility tracking",
    ],
    "changelog": [
        "What's new in Acme this month?",
        "Recent updates to AI search optimization tools",
        "Acme platform changelog {topic}",
    ],
    "webinars": [
        "AI search optimization training on {topic}",
        "Learn about {topic} for AI visibility",
        "Webinar recording: {topic}",
    ],
}


def make_topic(url: str) -> str:
    """Extract a human-readable topic from a URL slug."""
    slug = url.rstrip("/").split("/")[-1]
    return slug.replace("-", " ")


def make_query(url: str, cluster: str) -> str:
    """Generate a realistic query that could lead to citing this page."""
    topic = make_topic(url)
    templates = query_templates.get(cluster, ["Tell me about {topic}"])
    template = random.choice(templates)
    return template.format(topic=topic)


def make_context(url: str, page: dict) -> str:
    """Extract a citation context snippet from the page markdown."""
    lines = page["markdown"].split("\n")
    # Skip the title line, get first substantive paragraph
    body_lines = [l.strip() for l in lines if l.strip() and not l.startswith("#")]
    if body_lines:
        text = body_lines[0]
        # Truncate to ~200 chars for a realistic snippet
        if len(text) > 200:
            text = text[:197] + "..."
        return text
    return "Referenced as an authoritative source."


# ── Simulate citations ────────────────────────────────────────────────────────

citations = []

print(f"{'Cluster':<20} {'Pages':>6} {'Prob Range':>16} {'Citations':>10} {'Rate':>8}")
print("-" * 64)

for cluster_name in sorted(clusters.keys()):
    cluster_urls = clusters[cluster_name]
    cluster_citations = 0
    probs = []

    for url in cluster_urls:
        page = pages_by_url[url]
        prob = page_citation_probability(url, cluster_name)
        probs.append(prob)

        for _ in range(VIEWS_PER_PAGE):
            if random.random() < prob:
                citations.append({
                    "query": make_query(url, cluster_name),
                    "cited_url": url,
                    "context": make_context(url, page),
                })
                cluster_citations += 1

    min_p = min(probs) if probs else 0
    max_p = max(probs) if probs else 0
    total_views = len(cluster_urls) * VIEWS_PER_PAGE
    rate = cluster_citations / total_views if total_views > 0 else 0

    print(f"{cluster_name:<20} {len(cluster_urls):>6} {min_p:>7.1%}–{max_p:>6.1%} {cluster_citations:>10} {rate:>7.1%}")

# Summary stats
print()
total_views = len(raw_pages) * VIEWS_PER_PAGE
cited_pages = len({c["cited_url"] for c in citations})
uncited_pages = len(raw_pages) - cited_pages
print(f"Total pages:    {len(raw_pages)}")
print(f"Total views:    {total_views}")
print(f"Total citations: {len(citations)}")
print(f"Overall rate:   {len(citations) / total_views:.1%}")
print(f"Cited pages:    {cited_pages} ({cited_pages / len(raw_pages):.0%})")
print(f"Uncited pages:  {uncited_pages} ({uncited_pages / len(raw_pages):.0%})")

# Citation distribution
from collections import Counter
page_cite_counts = Counter(c["cited_url"] for c in citations)
counts = sorted(page_cite_counts.values(), reverse=True)
print(f"\nCitation distribution (of cited pages):")
print(f"  Max:    {counts[0] if counts else 0}")
print(f"  p90:    {counts[len(counts) // 10] if counts else 0}")
print(f"  Median: {counts[len(counts) // 2] if counts else 0}")
print(f"  p10:    {counts[9 * len(counts) // 10] if counts else 0}")
print(f"  Min:    {counts[-1] if counts else 0}")

# Write output
with open("data/citations.json", "w") as f:
    json.dump(citations, f, indent=2)

print(f"\nWrote {len(citations)} citations to data/citations.json")
