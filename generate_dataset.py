"""
Generate a synthetic dataset of 500 web pages with realistic internal link structures.

The dataset exhibits the full range of structural patterns identified in the research:
- Hub-spoke clusters (high hub_dominance, low density)
- Clique clusters (high density, high reciprocity)
- Mesh clusters (moderate density, uniform degree distribution)
- Tree clusters (hierarchical depth, low density)
- Chain clusters (sequential linking)
- Mixed/heterogeneous clusters (organic structure, most citable)
- Cross-section linking between clusters

Run: python generate_dataset.py
Output: data/pages.json
"""

import json
import random
from pathlib import Path

random.seed(42)

pages: dict[str, dict] = {}


def add_page(url: str, markdown: str, links: list[str] | None = None):
    pages[url] = {
        "url": url,
        "markdown": markdown,
        "links": links or [],
    }


def pick(lst, k):
    return random.sample(lst, min(k, len(lst)))


# ---------------------------------------------------------------------------
# Cluster 1: /blog/ — HUB-SPOKE (65 pages)
# One dominant index page, posts link to index but rarely to each other.
# High hub_dominance, low density, low reciprocity.
# ---------------------------------------------------------------------------

blog_index = "https://acme.com/blog"
blog_posts = [f"https://acme.com/blog/{slug}" for slug in [
    "what-is-ai-search", "seo-vs-aio", "future-of-search", "llm-citations-explained",
    "content-structure-guide", "internal-linking-strategy", "hub-spoke-model",
    "pillar-content-101", "topic-clusters-explained", "how-chatgpt-picks-sources",
    "brand-visibility-ai", "ai-overviews-google", "perplexity-for-brands",
    "measuring-ai-traffic", "citation-tracking-tools", "content-audit-checklist",
    "site-architecture-basics", "crawl-depth-matters", "link-equity-explained",
    "anchor-text-best-practices", "canonical-urls-guide", "redirect-chains",
    "xml-sitemaps", "robots-txt-guide", "core-web-vitals", "page-speed-seo",
    "mobile-first-indexing", "structured-data-howto", "schema-markup-guide",
    "faq-schema-benefits", "breadcrumb-navigation", "pagination-seo",
    "faceted-navigation", "javascript-seo", "rendering-strategies",
    "ssr-vs-csr-vs-isr", "headless-cms-seo", "api-first-content",
    "content-freshness", "evergreen-content", "updating-old-posts",
    "content-pruning", "thin-content-fix", "duplicate-content",
    "keyword-cannibalization", "search-intent-types", "informational-queries",
    "transactional-queries", "navigational-queries", "long-tail-keywords",
    "semantic-search", "entity-seo", "knowledge-graph-optimization",
    "people-also-ask", "featured-snippets", "zero-click-searches",
    "voice-search-optimization", "visual-search-seo", "video-seo-basics",
    "youtube-seo", "podcast-seo", "image-alt-text", "webp-images",
    "lazy-loading", "infinite-scroll-seo", "link-building-2025",
    "digital-pr", "haro-outreach", "guest-posting-strategy",
    "broken-link-building", "resource-page-links", "skyscraper-technique",
    "content-syndication", "medium-vs-blog", "linkedin-articles-seo",
    "reddit-for-seo", "quora-for-seo", "community-driven-seo",
    "user-generated-content", "review-schema", "product-schema",
    "local-seo-basics", "google-business-profile", "multi-location-seo",
    "ecommerce-seo-guide", "category-page-optimization", "product-page-seo",
]]

add_page(blog_index, "# Acme Blog\n\nInsights on AI search optimization, content strategy, and technical SEO.", [])

for i, post in enumerate(blog_posts):
    title = post.split("/")[-1].replace("-", " ").title()
    # Every post links to the index (hub pattern)
    links = [blog_index]
    # ~15% of posts link to 1-2 other posts (sparse cross-linking)
    if random.random() < 0.15:
        links += pick([p for p in blog_posts if p != post], random.randint(1, 2))
    add_page(post, f"# {title}\n\nA deep dive into {title.lower()} and why it matters for AI visibility.", links)

# Hub links back to ~8 featured posts (asymmetric — hub gets many inbound, few outbound)
pages[blog_index]["links"] = pick(blog_posts, 8)


# ---------------------------------------------------------------------------
# Cluster 2: /products/ — MESH (55 pages)
# Every product links to every product in its category via shared nav.
# High density, high reciprocity, low degree_gini. The "bad" pattern.
# ---------------------------------------------------------------------------

product_categories = {
    "analytics": 14,
    "optimization": 13,
    "monitoring": 14,
    "reporting": 14,
}

all_products = []
for cat, count in product_categories.items():
    cat_products = [f"https://acme.com/products/{cat}/{cat}-{j}" for j in range(1, count + 1)]
    all_products.extend(cat_products)

    for prod in cat_products:
        slug = prod.split("/")[-1].replace("-", " ").title()
        # Each product links to ALL other products in same category (mesh/nav pattern)
        siblings = [p for p in cat_products if p != prod]
        # Plus the category index
        cat_index = f"https://acme.com/products/{cat}"
        add_page(prod, f"# {slug}\n\nEnterprise-grade {cat} solution with real-time dashboards and API access.", siblings + [cat_index])

    # Category index links to all its products
    add_page(f"https://acme.com/products/{cat}", f"# {cat.title()} Products\n\nExplore our {cat} product suite.", cat_products)

products_index = "https://acme.com/products"
cat_indices = [f"https://acme.com/products/{cat}" for cat in product_categories]
add_page(products_index, "# Products\n\nAll-in-one platform for AI search optimization.", cat_indices)


# ---------------------------------------------------------------------------
# Cluster 3: /docs/ — TREE (70 pages)
# Strict hierarchy: index → sections → subsections → leaf pages.
# Low density, clear depth variation, moderate hub structure.
# ---------------------------------------------------------------------------

docs_index = "https://acme.com/docs"
docs_sections = {}

section_defs = {
    "getting-started": ["installation", "quickstart", "configuration", "authentication", "first-project", "cli-reference"],
    "api-reference": ["rest-api", "graphql-api", "webhooks", "rate-limits", "error-codes", "pagination", "filtering", "sdks", "authentication-api", "batch-api", "streaming-api"],
    "guides": ["crawl-setup", "citation-tracking", "brand-monitoring", "competitor-analysis", "custom-reports", "integrations", "data-export", "bulk-operations", "white-labeling", "multi-brand", "agency-setup"],
    "concepts": ["how-crawling-works", "embedding-model", "citation-detection", "scoring-algorithm", "content-classification", "topic-clustering", "graph-analysis", "authority-signals", "freshness-scoring"],
    "admin": ["team-management", "billing", "sso-setup", "audit-logs", "permissions", "data-retention", "api-keys", "workspace-settings"],
    "tutorials": ["build-first-dashboard", "automate-reports", "set-up-alerts", "track-competitors", "optimize-content", "measure-roi", "import-data", "connect-cms", "share-reports"],
    "troubleshooting": ["common-errors", "connectivity-issues", "data-sync-delays", "missing-citations", "crawl-failures", "permission-errors", "webhook-debugging", "api-timeouts"],
}

all_docs = []
section_indices = []

for section, subsections in section_defs.items():
    section_url = f"https://acme.com/docs/{section}"
    section_indices.append(section_url)
    sub_urls = [f"https://acme.com/docs/{section}/{sub}" for sub in subsections]
    all_docs.extend(sub_urls)

    # Section index links down to its children only
    section_title = section.replace("-", " ").title()
    add_page(section_url, f"# {section_title}\n\nDocumentation for {section_title.lower()}.", sub_urls + [docs_index])
    all_docs.append(section_url)

    for sub_url in sub_urls:
        sub_title = sub_url.split("/")[-1].replace("-", " ").title()
        # Leaf links up to parent section and docs index (tree pattern — upward only)
        links = [section_url]
        # ~20% link to a sibling doc
        if random.random() < 0.20:
            links += pick([s for s in sub_urls if s != sub_url], 1)
        add_page(sub_url, f"# {sub_title}\n\n{sub_title} reference documentation with examples and code samples.", links)

add_page(docs_index, "# Documentation\n\nComplete reference for the Acme platform.", section_indices)


# ---------------------------------------------------------------------------
# Cluster 4: /case-studies/ — MIXED (45 pages)
# Organic structure: some hub pages, some chains, some clusters.
# The most common pattern in real sites and the most citable (62.3%).
# ---------------------------------------------------------------------------

cs_index = "https://acme.com/case-studies"
cs_industries = ["saas", "ecommerce", "fintech", "healthcare", "education", "media", "manufacturing"]
cs_pages = []

for industry in cs_industries:
    industry_index = f"https://acme.com/case-studies/{industry}"
    studies = [f"https://acme.com/case-studies/{industry}/{industry}-study-{j}" for j in range(1, random.randint(6, 9))]
    cs_pages.append(industry_index)
    cs_pages.extend(studies)

    # Industry index is a mini-hub
    add_page(industry_index, f"# {industry.title()} Case Studies\n\nHow {industry} companies improved AI visibility.", studies + [cs_index])

    for k, study in enumerate(studies):
        title = f"{industry.title()} Case Study {k + 1}"
        links = [industry_index]
        # Organic: ~40% link to a study in a DIFFERENT industry (cross-cluster)
        if random.random() < 0.40:
            other_industry = random.choice([i for i in cs_industries if i != industry])
            cross_link = f"https://acme.com/case-studies/{other_industry}"
            links.append(cross_link)
        # ~25% link to 1-2 sibling studies
        if random.random() < 0.25:
            links += pick([s for s in studies if s != study], random.randint(1, 2))
        # Some link to blog posts (cross-section)
        if random.random() < 0.20:
            links += pick(blog_posts, 1)
        add_page(study, f"# {title}\n\nHow this {industry} brand achieved 3x citation growth in 90 days.", links)

add_page(cs_index, "# Case Studies\n\nReal results from real brands.", [f"https://acme.com/case-studies/{ind}" for ind in cs_industries])


# ---------------------------------------------------------------------------
# Cluster 5: /resources/ — CLIQUE (20 pages)
# Every page links to every other page. High density, high reciprocity.
# Only 36.4% citation rate in the research.
# ---------------------------------------------------------------------------

resource_topics = [
    "ai-search-glossary", "seo-glossary", "citation-metrics-guide",
    "benchmark-report-2025", "industry-survey", "roi-calculator",
    "comparison-chart", "buyer-guide", "implementation-checklist",
    "migration-guide", "integration-matrix", "feature-comparison",
    "pricing-guide", "vendor-evaluation", "security-whitepaper",
    "compliance-overview", "data-sheet", "architecture-diagram",
    "api-overview", "platform-roadmap",
]
resource_urls = [f"https://acme.com/resources/{t}" for t in resource_topics]

for res_url in resource_urls:
    title = res_url.split("/")[-1].replace("-", " ").title()
    # Clique: every page links to every other page
    links = [r for r in resource_urls if r != res_url]
    add_page(res_url, f"# {title}\n\nDownloadable resource for AI search optimization planning.", links)


# ---------------------------------------------------------------------------
# Cluster 6: /pricing/ — CHAIN (12 pages)
# Sequential flow: overview → tier comparisons → add-ons → checkout.
# Low density, no hub, linear structure.
# ---------------------------------------------------------------------------

pricing_chain = [
    "https://acme.com/pricing",
    "https://acme.com/pricing/plans-overview",
    "https://acme.com/pricing/starter",
    "https://acme.com/pricing/professional",
    "https://acme.com/pricing/enterprise",
    "https://acme.com/pricing/compare-plans",
    "https://acme.com/pricing/add-ons",
    "https://acme.com/pricing/api-pricing",
    "https://acme.com/pricing/volume-discounts",
    "https://acme.com/pricing/custom-quote",
    "https://acme.com/pricing/faq",
    "https://acme.com/pricing/contact-sales",
]

pricing_titles = [
    "Pricing", "Plans Overview", "Starter Plan", "Professional Plan",
    "Enterprise Plan", "Compare Plans", "Add-Ons", "API Pricing",
    "Volume Discounts", "Custom Quote", "Pricing FAQ", "Contact Sales",
]

for i, (url, title) in enumerate(zip(pricing_chain, pricing_titles)):
    links = []
    if i > 0:
        links.append(pricing_chain[i - 1])  # previous
    if i < len(pricing_chain) - 1:
        links.append(pricing_chain[i + 1])  # next
    add_page(url, f"# {title}\n\nTransparent pricing for teams of all sizes.", links)


# ---------------------------------------------------------------------------
# Cluster 7: /solutions/ — WELL-STRUCTURED HUB (70 pages)
# Clear pillar pages with supporting content. High hub_dominance,
# moderate density, good depth variation. The "ideal" pattern.
# ---------------------------------------------------------------------------

solutions_index = "https://acme.com/solutions"
solution_pillars = {
    "ai-visibility": [
        "brand-mention-tracking", "citation-monitoring", "sentiment-analysis",
        "competitor-benchmarking", "share-of-voice", "trend-detection",
        "alert-configuration", "executive-dashboard", "weekly-reports",
    ],
    "content-optimization": [
        "content-scoring", "gap-analysis", "keyword-opportunities",
        "content-calendar", "brief-generation", "performance-tracking",
        "ab-testing-content", "content-refresh", "pruning-recommendations",
        "topic-clustering", "semantic-analysis",
    ],
    "technical-seo": [
        "site-audit", "crawl-analysis", "indexation-monitoring",
        "core-web-vitals", "schema-validation", "redirect-management",
        "log-file-analysis", "javascript-rendering", "mobile-optimization",
        "international-seo", "hreflang-validation",
    ],
    "competitive-intelligence": [
        "competitor-tracking", "market-landscape", "feature-comparison",
        "positioning-analysis", "pricing-intelligence", "content-gap-finder",
        "backlink-analysis", "traffic-estimation", "win-loss-analysis",
        "market-share-tracking", "brand-perception",
    ],
    "reporting": [
        "custom-dashboards", "automated-reports", "stakeholder-views",
        "data-export", "api-access", "white-label-reports",
        "roi-attribution", "kpi-tracking", "executive-summary",
        "team-performance", "channel-breakdown",
    ],
}

pillar_urls = []
all_solution_pages = []

for pillar, subtopics in solution_pillars.items():
    pillar_url = f"https://acme.com/solutions/{pillar}"
    pillar_urls.append(pillar_url)
    sub_urls = [f"https://acme.com/solutions/{pillar}/{sub}" for sub in subtopics]
    all_solution_pages.extend(sub_urls)

    pillar_title = pillar.replace("-", " ").title()
    # Pillar links down to its children AND to 2 other pillars (cross-section)
    other_pillars = pick([f"https://acme.com/solutions/{p}" for p in solution_pillars if p != pillar], 2)
    add_page(pillar_url, f"# {pillar_title}\n\nComprehensive {pillar_title.lower()} solution for enterprise brands.", sub_urls + other_pillars + [solutions_index])

    for sub_url in sub_urls:
        sub_title = sub_url.split("/")[-1].replace("-", " ").title()
        # Each page links to pillar (hub) and 1-3 siblings
        links = [pillar_url]
        links += pick([s for s in sub_urls if s != sub_url], random.randint(1, 3))
        # ~30% link to a page in another pillar (cross-section connectivity)
        if random.random() < 0.30:
            other_pillar = random.choice([p for p in solution_pillars if p != pillar])
            other_subs = [f"https://acme.com/solutions/{other_pillar}/{s}" for s in solution_pillars[other_pillar]]
            links += pick(other_subs, 1)
        add_page(sub_url, f"# {sub_title}\n\nDetailed guide to {sub_title.lower()} capabilities and best practices.", links)

add_page(solutions_index, "# Solutions\n\nEverything you need for AI search optimization.", pillar_urls)


# ---------------------------------------------------------------------------
# Cluster 8: /about/ — SPARSE/FLAT (30 pages)
# Minimal internal linking. Most pages only link to the index.
# Low density, low hub_dominance, low everything.
# ---------------------------------------------------------------------------

about_pages_list = [
    "company", "team", "leadership", "careers", "culture", "values",
    "mission", "history", "press", "newsroom", "awards", "partners",
    "investors", "board", "advisors", "offices", "contact",
    "diversity", "sustainability", "community", "events", "webinars",
    "brand-guidelines", "media-kit", "legal", "privacy", "terms",
    "security", "status", "accessibility",
    "customers", "testimonials", "case-studies-overview", "blog-overview",
    "social-responsibility", "engineering-blog", "open-source",
    "referral-program", "affiliate-program", "student-program",
]

about_index = "https://acme.com/about"
about_urls = [f"https://acme.com/about/{p}" for p in about_pages_list]

add_page(about_index, "# About Acme\n\nWe help brands win in the age of AI search.", pick(about_urls, 5))

for about_url in about_urls:
    title = about_url.split("/")[-1].replace("-", " ").title()
    # Sparse: most pages only link to the about index
    links = [about_index]
    # ~10% link to one sibling
    if random.random() < 0.10:
        links += pick([a for a in about_urls if a != about_url], 1)
    add_page(about_url, f"# {title}\n\nLearn more about Acme's {title.lower()}.", links)


# ---------------------------------------------------------------------------
# Cluster 9: /integrations/ — MODERATE HUB (50 pages)
# Integration directory with a clear index hub, moderate linking.
# Mid-range hub_dominance, moderate density.
# ---------------------------------------------------------------------------

integration_index = "https://acme.com/integrations"
integration_categories = {
    "cms": ["wordpress", "contentful", "sanity", "strapi", "ghost", "webflow", "drupal"],
    "analytics": ["google-analytics", "mixpanel", "amplitude", "heap", "segment", "plausible"],
    "crm": ["salesforce", "hubspot", "pipedrive", "zoho", "monday"],
    "marketing": ["mailchimp", "klaviyo", "activecampaign", "marketo", "braze"],
    "ecommerce": ["shopify", "woocommerce", "magento", "bigcommerce", "squarespace"],
    "collaboration": ["slack", "notion", "confluence", "asana", "jira", "linear", "clickup"],
    "data": ["snowflake", "bigquery", "databricks", "looker", "tableau", "powerbi"],
}

all_integration_urls = []
int_cat_indices = []

for cat, integrations in integration_categories.items():
    cat_url = f"https://acme.com/integrations/{cat}"
    int_cat_indices.append(cat_url)
    int_urls = [f"https://acme.com/integrations/{cat}/{name}" for name in integrations]
    all_integration_urls.extend(int_urls)

    add_page(cat_url, f"# {cat.upper()} Integrations\n\nConnect Acme with your {cat} tools.", int_urls + [integration_index])

    for int_url in int_urls:
        name = int_url.split("/")[-1].replace("-", " ").title()
        links = [cat_url, integration_index]
        # ~30% link to 1-2 integrations in same category
        if random.random() < 0.30:
            links += pick([u for u in int_urls if u != int_url], random.randint(1, 2))
        # ~15% link to an integration in a different category
        if random.random() < 0.15:
            other_cat = random.choice([c for c in integration_categories if c != cat])
            other_url = f"https://acme.com/integrations/{other_cat}/{random.choice(integration_categories[other_cat])}"
            links.append(other_url)
        add_page(int_url, f"# {name} Integration\n\nConnect {name} to Acme for automated AI visibility tracking.", links)

add_page(integration_index, "# Integrations\n\n50+ integrations to fit your workflow.", int_cat_indices)


# ---------------------------------------------------------------------------
# Cluster 10: /changelog/ — REVERSE CHAIN (25 pages)
# Chronological entries, each linking to next/previous.
# Like pricing chain but longer and with occasional category links.
# ---------------------------------------------------------------------------

changelog_entries = [f"https://acme.com/changelog/2025-{month:02d}" for month in range(1, 13)] + \
                    [f"https://acme.com/changelog/2024-{month:02d}" for month in range(1, 13)] + \
                    ["https://acme.com/changelog"]

changelog_index = "https://acme.com/changelog"
changelog_months = [e for e in changelog_entries if e != changelog_index]

add_page(changelog_index, "# Changelog\n\nAll platform updates and releases.", changelog_months[:6])

for i, entry in enumerate(changelog_months):
    month_label = entry.split("/")[-1]
    links = [changelog_index]
    if i > 0:
        links.append(changelog_months[i - 1])
    if i < len(changelog_months) - 1:
        links.append(changelog_months[i + 1])
    # ~20% link to a docs or solutions page
    if random.random() < 0.20:
        links += pick(all_docs[:10], 1)
    add_page(entry, f"# Changelog — {month_label}\n\nNew features, improvements, and bug fixes.", links)


# ---------------------------------------------------------------------------
# Cluster 11: /webinars/ — SMALL HUB-SPOKE (20 pages)
# Archive page links to all webinars; webinars link back to archive only.
# Very clean hub-spoke, smaller than /blog/.
# ---------------------------------------------------------------------------

webinar_index = "https://acme.com/webinars"
webinar_pages = [f"https://acme.com/webinars/{slug}" for slug in [
    "ai-search-masterclass", "citation-tracking-deep-dive", "content-structure-workshop",
    "seo-to-aio-transition", "brand-visibility-summit", "technical-seo-2025",
    "content-ops-at-scale", "measuring-ai-roi", "competitive-intel-playbook",
    "enterprise-onboarding", "agency-partner-training", "product-demo-live",
    "customer-success-stories", "roadmap-preview-q2", "api-workshop",
    "data-driven-content", "international-expansion", "healthcare-vertical",
    "ecommerce-vertical", "fintech-vertical",
]]

add_page(webinar_index, "# Webinars\n\nLive and on-demand webinars on AI search optimization.", pick(webinar_pages, 6))

for wb in webinar_pages:
    title = wb.split("/")[-1].replace("-", " ").title()
    links = [webinar_index]
    # ~10% link to a blog post
    if random.random() < 0.10:
        links += pick(blog_posts, 1)
    add_page(wb, f"# {title}\n\nWatch the recording and download the slides.", links)


# ---------------------------------------------------------------------------
# Cross-section links: wire up connections between clusters
# The research shows cross-section connectivity is +738% for top-cited loci
# ---------------------------------------------------------------------------

# Solutions link to relevant docs
for page_url, page_data in list(pages.items()):
    if page_url.startswith("https://acme.com/solutions/") and "/solutions/" in page_url:
        if random.random() < 0.15:
            page_data["links"].append(random.choice(all_docs[:20]))

# Blog posts link to solutions and case studies
for post in blog_posts:
    if random.random() < 0.12:
        pages[post]["links"].append(random.choice(pillar_urls))
    if random.random() < 0.08:
        pages[post]["links"].append(random.choice(cs_pages[:5]))

# Case studies link to solutions
for page_url in list(pages.keys()):
    if page_url.startswith("https://acme.com/case-studies/") and "study" in page_url:
        if random.random() < 0.25:
            pages[page_url]["links"].append(random.choice(pillar_urls))

# Homepage
homepage = "https://acme.com"
add_page(homepage, "# Acme — AI Search Optimization Platform\n\nGet your brand cited by AI.", [
    solutions_index, products_index, blog_index, docs_index,
    cs_index, integration_index, "https://acme.com/pricing",
    about_index,
])


# ---------------------------------------------------------------------------
# Deduplicate links and remove self-links
# ---------------------------------------------------------------------------

for url, page in pages.items():
    seen = set()
    clean = []
    for link in page["links"]:
        if link != url and link not in seen:
            seen.add(link)
            clean.append(link)
    page["links"] = clean


# ---------------------------------------------------------------------------
# Output
# ---------------------------------------------------------------------------

output = sorted(pages.values(), key=lambda p: p["url"])

Path("data").mkdir(exist_ok=True)
with open("data/pages.json", "w") as f:
    json.dump(output, f, indent=2)

# Print summary stats
print(f"Total pages: {len(output)}")
print(f"Total links: {sum(len(p['links']) for p in output)}")
print()

# Per-cluster stats
clusters = {}
for p in output:
    parts = p["url"].replace("https://acme.com/", "").split("/")
    cluster = parts[0] if parts[0] else "root"
    clusters.setdefault(cluster, []).append(p)

print(f"{'Cluster':<20} {'Pages':>6} {'Links':>6} {'Avg Deg':>8} {'Density':>8}")
print("-" * 52)
for name, cpages in sorted(clusters.items(), key=lambda x: -len(x[1])):
    n = len(cpages)
    total_links = sum(len(p["links"]) for p in cpages)
    # Count only intra-cluster links for density
    cluster_urls = {p["url"] for p in cpages}
    intra = sum(1 for p in cpages for l in p["links"] if l in cluster_urls)
    max_edges = n * (n - 1) if n > 1 else 1
    density = intra / max_edges
    avg_deg = intra / n if n > 0 else 0
    print(f"{name:<20} {n:>6} {total_links:>6} {avg_deg:>8.1f} {density:>8.4f}")
