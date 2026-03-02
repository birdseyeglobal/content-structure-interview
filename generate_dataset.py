"""
Generate a synthetic dataset of ~500 web pages with realistic internal link structures.

The dataset exhibits the full range of structural patterns identified in the research:
- Hub-spoke clusters (high hub_dominance, low density)
- Clique clusters (high density, high reciprocity)
- Mesh clusters (moderate density, uniform degree distribution)
- Tree clusters (hierarchical depth, low density)
- Chain clusters (sequential linking)
- Mixed/heterogeneous clusters (organic structure, most citable)
- Cross-section linking between clusters

Content within each cluster is topically coherent — pages share vocabulary,
reference each other's concepts, and read like a real site section.

Run: python generate_dataset.py
Output: data/pages.json
"""

import json
import random
from pathlib import Path

random.seed(42)

pages: dict[str, dict] = {}


def add_page(url: str, markdown: str, links: list[str] | None = None):
    pages[url] = {"url": url, "markdown": markdown, "links": links or []}


def pick(lst, k):
    return random.sample(lst, min(k, len(lst)))


# =============================================================================
# BLOG — HUB-SPOKE (~88 pages)
# One dominant index, posts link to index but rarely to each other.
# High hub_dominance, low density, low reciprocity.
# =============================================================================

blog_index = "https://acme.com/blog"

# Content organized into topical sub-themes that flow into each other.
# Each tuple: (slug, title, content paragraphs)
blog_entries = [
    # --- AI search fundamentals (posts 1-10) ---
    ("what-is-ai-search",
     "What Is AI Search and Why It Matters for Your Brand",
     "AI search refers to the shift from traditional keyword-based search engines toward large language models that synthesize answers from multiple sources. Instead of returning a list of blue links, platforms like ChatGPT, Perplexity, and Google AI Overviews generate prose responses that cite specific web pages as evidence.\n\nFor brands, this changes the visibility equation entirely. It no longer matters whether you rank on page one — what matters is whether the LLM selects your page as a source when composing its answer. This is a fundamentally different optimization problem that requires understanding how these models evaluate and select content."),

    ("seo-vs-aio",
     "SEO vs AIO: How AI Optimization Differs from Traditional Search",
     "Traditional SEO optimizes for ranking algorithms that weigh backlinks, keyword density, and page authority. AI optimization (AIO) targets a different pipeline: the retrieval-augmented generation process where an LLM retrieves candidate pages, evaluates their relevance, and decides which to cite.\n\nThe signals that drive AIO overlap with but diverge from SEO signals. Internal link structure, content specificity, and topical authority matter more in AIO because LLMs prefer pages that serve as clear, authoritative references rather than pages optimized for click-through rate. This post explores the concrete differences between the two disciplines."),

    ("future-of-search",
     "The Future of Search: How LLMs Are Reshaping Content Discovery",
     "Search is transitioning from a retrieval problem to a generation problem. Users increasingly ask complex, multi-part questions and expect synthesized answers rather than lists of links. This shift has profound implications for how brands structure their online presence.\n\nThe brands that will thrive in AI-mediated search are those that organize their content as authoritative, well-structured reference material rather than SEO-optimized landing pages. Internal linking, topical depth, and clear content hierarchies become the primary levers of visibility."),

    ("llm-citations-explained",
     "How LLM Citations Work: A Technical Overview",
     "When an LLM generates a response, it draws on a retrieval step that identifies candidate pages from its index or a live search. The model then selects which pages to cite based on relevance, specificity, and structural signals in the content.\n\nCitations are not random or arbitrary — our research across millions of LLM responses shows that structural properties of web pages strongly predict citation likelihood. Pages with clear authority hierarchies, topical focus, and strong internal linking are cited significantly more often than isolated or poorly structured pages."),

    ("content-structure-guide",
     "The Complete Guide to Content Structure for AI Visibility",
     "Content structure is the arrangement of pages, links, and hierarchies that define how information flows through your website. For AI visibility, structure matters as much as content quality because LLMs use structural signals to assess page authority and relevance.\n\nA well-structured site organizes content into clear topical clusters with pillar pages that serve as authoritative hubs. Supporting pages link inward to the pillar, creating an asymmetric authority pattern that signals to both crawlers and LLMs which pages represent the definitive resource on a topic."),

    ("internal-linking-strategy",
     "Internal Linking Strategy for AI Search Optimization",
     "Internal links are the connective tissue of your website's information architecture. For AI search optimization, not all linking patterns are equal. Our analysis shows that asymmetric link structures — where supporting pages point to a central hub — outperform mesh patterns where every page links to every other.\n\nThe key insight is that link density (the ratio of actual links to possible links) is a negative predictor of citation rate when it reflects uniform navigation patterns rather than intentional editorial connections. Focus on building clear authority paths rather than saturating pages with links."),

    ("hub-spoke-model",
     "The Hub-Spoke Content Model: Building Authority Through Structure",
     "The hub-spoke model organizes content around a central pillar page (the hub) surrounded by supporting articles (the spokes) that link inward. This creates an asymmetric authority structure where the hub accumulates link equity from its spokes.\n\nOur research shows that hub dominance — the fraction of a cluster's internal links pointing to the top page — is the strongest size-independent predictor of whether content gets cited by LLMs. Clusters with clear hub-spoke topology outperform flat, mesh-like structures by a wide margin."),

    ("pillar-content-101",
     "Pillar Content 101: Creating Authoritative Hub Pages",
     "A pillar page is the comprehensive, authoritative resource on a topic that serves as the hub of a content cluster. It covers the topic broadly while linking to detailed supporting pages that go deeper on subtopics.\n\nEffective pillar pages share several characteristics: they provide a complete overview of the topic, they link to and are linked from all related supporting pages, and they maintain topical focus without straying into tangential subjects. The pages that perform best as pillars have high in-degree (many pages link to them) and low embedding variance with their cluster."),

    ("topic-clusters-explained",
     "Topic Clusters: How Topical Coherence Drives AI Citations",
     "A topic cluster is a group of semantically related pages that together provide comprehensive coverage of a subject area. The cluster's internal coherence — measured by the variance of page embeddings from the cluster centroid — predicts how often the cluster's pages get cited.\n\nFor large clusters (40+ pages), topical coherence becomes especially important. Our data shows that the most semantically coherent quintile of large clusters has 11x the citation rate of the least coherent. This suggests that sprawling, unfocused content sections dilute their authority signal."),

    ("how-chatgpt-picks-sources",
     "How ChatGPT Picks Sources: Inside the Citation Pipeline",
     "ChatGPT and similar LLMs follow a retrieval-augmented generation pipeline when answering questions. First, a retrieval step identifies candidate pages from a search index. Then the model evaluates each candidate for relevance, authority, and specificity before deciding which to cite.\n\nThe structural properties of your site influence both stages. Well-linked pages are more likely to appear in the retrieval step because crawlers discover them more easily. Pages with clear topical authority — established through hub-spoke linking and cross-section connectivity — are more likely to survive the citation selection step."),

    # --- AI visibility & monitoring (posts 11-18) ---
    ("brand-visibility-ai",
     "Brand Visibility in AI: Measuring Your Share of LLM Citations",
     "Brand visibility in AI search is the frequency with which your brand's pages are cited in LLM-generated responses. Unlike traditional search where visibility is measured by rank position, AI visibility is binary per response — you're either cited or you're not.\n\nMeasuring AI visibility requires monitoring LLM responses across a representative set of queries in your domain, tracking which URLs are cited, and computing your share of voice relative to competitors. This is fundamentally different from tracking Google rankings and requires new tooling and metrics."),

    ("ai-overviews-google",
     "Google AI Overviews: What They Mean for Brand Visibility",
     "Google AI Overviews are AI-generated summaries that appear at the top of search results for informational queries. They synthesize information from multiple sources and cite the pages they drew from, making them a new battleground for brand visibility.\n\nThe pages cited in AI Overviews tend to be those with clear topical authority, structured content, and strong internal linking. Our analysis of AI Overview citations shows the same structural patterns that predict citations across other LLM platforms — hub dominance, cross-section connectivity, and content hierarchy depth."),

    ("perplexity-for-brands",
     "Perplexity for Brands: Optimizing for Answer Engine Visibility",
     "Perplexity is an answer engine that generates cited responses to user queries. Unlike traditional search, Perplexity provides direct answers with inline citations, making the citation itself the primary unit of brand visibility.\n\nBrands that structure their content as reference material — with clear hierarchies, comprehensive topic coverage, and well-organized internal links — are cited more frequently by Perplexity. The platform's retrieval system favors pages that serve as authoritative sources rather than pages optimized for click-through rate."),

    ("measuring-ai-traffic",
     "Measuring AI-Referred Traffic: Analytics Beyond Google",
     "AI-referred traffic comes from users who click through from LLM-generated citations to your website. Tracking this traffic requires identifying referral sources from AI platforms and attributing conversions to citation-driven visits.\n\nTraditional analytics setups often miscategorize AI traffic as direct or organic. Proper measurement requires configuring referral detection for AI platforms, setting up UTM-independent attribution for citation clicks, and correlating citation frequency with traffic patterns to understand the true impact of AI visibility."),

    ("citation-tracking-tools",
     "Citation Tracking Tools: How to Monitor LLM References",
     "Citation tracking monitors which of your pages are being cited by LLMs and how often. This requires systematically querying AI platforms with relevant prompts, parsing responses for URLs, and matching citations to your page inventory.\n\nEffective citation tracking goes beyond counting mentions. It tracks citation context (what question was being answered), citation position (inline vs. footnote), and whether the citation was accompanied by a brand mention. These dimensions help you understand not just how often you're cited but how you're being represented."),

    ("content-audit-checklist",
     "Content Audit Checklist for AI Search Readiness",
     "An AI search readiness audit evaluates your site's content and structure against the signals that predict LLM citation. The audit examines internal linking patterns, content hierarchy depth, topical coherence within clusters, and cross-section connectivity.\n\nStart by mapping your site's content clusters and computing structural metrics for each: hub dominance, link density, boundary connectivity, and embedding variance. Compare each cluster against the profiles of highly-cited content from our research to identify specific structural gaps."),

    ("site-architecture-basics",
     "Site Architecture Basics: Foundations for AI-Friendly Structure",
     "Site architecture is the blueprint for how content is organized, linked, and accessed on your website. A strong architecture creates clear pathways for both users and crawlers to navigate from broad topic areas to specific, detailed content.\n\nFor AI search optimization, architecture matters because crawlers and LLMs use the link graph to infer authority and relevance. Pages buried deep in the hierarchy with few inbound links are less likely to be discovered and cited. Pages connected to the rest of the site through intentional, topically relevant links are more likely to be treated as authoritative."),

    ("crawl-depth-matters",
     "Why Crawl Depth Matters for AI Discovery",
     "Crawl depth is the number of clicks from the homepage required to reach a page. Pages at shallow depths are discovered more quickly and more frequently by crawlers, making them more likely to appear in LLM retrieval indices.\n\nOur analysis shows that clusters with pages at varying depths — indicating a real content hierarchy rather than a flat list — have higher citation rates. The depth variation signal (depth_stddev) is the strongest predictor of whether a cluster gets cited at all, suggesting that hierarchical organization is a prerequisite for AI visibility."),

    # --- Technical SEO for AI (posts 19-30) ---
    ("link-equity-explained",
     "Link Equity Explained: How Authority Flows Through Internal Links",
     "Link equity is the authority signal that passes from one page to another through hyperlinks. When a page with high authority links to another page, some of that authority transfers to the target. Internal links distribute equity across your site.\n\nIn the context of AI search, link equity helps establish which pages are the authoritative references within a topic cluster. Pages that accumulate link equity from many supporting pages are treated as hub pages — and our research shows that clusters with clear hub pages are cited significantly more often than those with flat link distributions."),

    ("anchor-text-best-practices",
     "Anchor Text Best Practices for Internal Linking",
     "Anchor text — the clickable text in a hyperlink — provides context about the linked page's topic. For internal links, descriptive anchor text helps both users and crawlers understand the relationship between pages.\n\nWhen building internal links for AI optimization, use anchor text that accurately describes the target page's content. Avoid generic text like 'click here' or 'read more.' Instead, use descriptive phrases that reinforce the topical connection between source and target pages, strengthening the semantic coherence of your content clusters."),

    ("canonical-urls-guide",
     "Canonical URLs: Preventing Duplicate Content in Your Link Graph",
     "Canonical URLs tell search engines and crawlers which version of a page is the authoritative one. When multiple URLs serve the same content (HTTP vs HTTPS, www vs non-www, parameterized variants), canonical tags prevent link equity from being split across duplicates.\n\nFor AI search optimization, canonical URLs are essential for maintaining a clean link graph. Duplicate pages create noise in your internal linking structure, diluting the authority signals that help LLMs identify your hub pages. Ensure every page has a self-referencing canonical tag and that internal links point to canonical URLs."),

    ("redirect-chains",
     "Redirect Chains: How They Break Your Internal Link Structure",
     "A redirect chain occurs when a URL redirects to another URL, which redirects to yet another URL, forming a sequence of hops before reaching the final destination. Each hop in the chain degrades link equity and slows crawl efficiency.\n\nRedirect chains are particularly harmful for AI optimization because they obscure the true link graph of your site. A crawler following a chain may not attribute the link equity to the correct destination page, weakening the hub-spoke structures you've built. Audit your site for redirect chains and resolve them to direct, single-hop redirects."),

    ("xml-sitemaps",
     "XML Sitemaps: Helping Crawlers Discover Your Content",
     "An XML sitemap lists all the pages on your site that you want crawlers to discover. It provides metadata about each page including last modification date, update frequency, and relative priority.\n\nWhile sitemaps don't directly influence LLM citations, they ensure that crawlers discover all your content — especially pages that might be poorly linked internally. For AI optimization, sitemaps complement a strong internal linking strategy by providing a fallback discovery mechanism for pages that haven't yet been fully integrated into your link graph."),

    ("robots-txt-guide",
     "Robots.txt Guide: Controlling Crawler Access for AI Optimization",
     "The robots.txt file controls which pages crawlers can access on your site. For AI optimization, it's critical to ensure that your most important content clusters are accessible to the crawlers that feed LLM training and retrieval indices.\n\nReview your robots.txt to ensure you're not accidentally blocking hub pages, pillar content, or key supporting pages. Some sites inadvertently block entire sections through overly broad disallow rules, removing those pages from the LLM discovery pipeline entirely."),

    ("core-web-vitals",
     "Core Web Vitals: Performance Metrics That Affect AI Crawling",
     "Core Web Vitals measure page load performance, interactivity, and visual stability. While they primarily affect traditional search rankings, they also influence how effectively AI crawlers can render and extract content from your pages.\n\nPages with poor performance may timeout during crawling, resulting in incomplete content extraction. If a crawler can't fully render your page, it can't extract the internal links, structured data, or content that would help your page get cited. Optimize Core Web Vitals to ensure reliable crawl coverage."),

    ("page-speed-seo",
     "Page Speed and AI Crawling: Why Load Time Matters",
     "Page speed affects AI optimization through the crawl pipeline. Slower pages take longer to render, may be deprioritized in crawl schedules, and risk incomplete content extraction if timeouts occur during rendering.\n\nAI crawlers typically have time budgets per page. If your page doesn't load within that budget, the crawler moves on with whatever content it managed to extract — potentially missing internal links, structured data, or key content sections. Prioritize speed for your hub pages and pillar content to ensure complete extraction."),

    ("mobile-first-indexing",
     "Mobile-First Indexing and AI Content Extraction",
     "Mobile-first indexing means crawlers use the mobile version of your page as the primary source of content. If your mobile experience omits content, navigation, or internal links present in the desktop version, that content won't exist in the crawl index.\n\nFor AI optimization, ensure that your mobile experience includes the same internal links and content hierarchy as your desktop version. Hidden navigation, collapsed sections, and JavaScript-rendered content that doesn't load on mobile can all create gaps in your crawled link graph."),

    ("structured-data-howto",
     "How to Implement Structured Data for AI Search",
     "Structured data uses schema.org vocabulary to provide explicit signals about page content type, relationships, and metadata. For AI search, structured data helps crawlers understand the role of each page within your site's information architecture.\n\nImplement BreadcrumbList markup to reinforce your content hierarchy, Article markup to signal editorial content, and HowTo or FAQ markup where applicable. These structured signals complement your internal linking by providing an explicit semantic layer on top of the link graph."),

    ("schema-markup-guide",
     "Schema Markup Guide: Structured Data for Every Content Type",
     "Schema markup annotates your HTML with machine-readable metadata about the content's type, author, date, topic, and relationships. Different content types benefit from different schema types, and implementing the right markup helps AI systems categorize and prioritize your content.\n\nFor pillar pages, use Article or WebPage schema with comprehensive about and mentions properties. For product pages, use Product schema with pricing and review data. For how-to content, use HowTo schema with step-by-step structure. Each schema type helps AI systems understand your content's role in the broader site architecture."),

    ("faq-schema-benefits",
     "FAQ Schema: Earning Featured Answers in AI Responses",
     "FAQ schema markup identifies question-and-answer pairs on your page. AI systems that parse structured data can extract these Q&A pairs directly, making your content more likely to be cited when users ask related questions.\n\nPages with FAQ schema provide pre-structured answers that map cleanly to the question-answer format of LLM responses. Implement FAQ markup on hub pages and pillar content where you address common questions about your topic, creating direct pathways between user queries and your authoritative answers."),

    ("breadcrumb-navigation",
     "Breadcrumb Navigation: Reinforcing Content Hierarchy",
     "Breadcrumbs show the path from the homepage to the current page, reinforcing your site's hierarchical structure for both users and crawlers. They provide an explicit signal about where a page sits in your content architecture.\n\nFor AI optimization, breadcrumbs serve double duty: they create additional internal links upward in the hierarchy (strengthening hub pages), and they provide structured data signals about content depth and categorization. Implement BreadcrumbList schema alongside visual breadcrumbs for maximum impact."),

    ("pagination-seo",
     "Pagination and AI Crawling: Handling Multi-Page Content",
     "Paginated content splits a single topic across multiple pages using next/previous navigation. For AI optimization, pagination can fragment your content's authority signal across multiple URLs rather than concentrating it on a single authoritative page.\n\nWhere possible, consolidate paginated content into single, comprehensive pages. If pagination is necessary (product listings, archives), ensure that the first page serves as a clear hub with links to all subsequent pages, and implement rel=next/prev markup to help crawlers understand the sequence."),

    ("faceted-navigation",
     "Faceted Navigation: Managing Link Density in Product Sections",
     "Faceted navigation lets users filter product listings by attributes like price, category, size, and color. Each combination generates a unique URL, creating a dense mesh of cross-linked pages that can inflate your site's link graph.\n\nOur research shows that high link density in product sections — where every page links to every other through navigation — is a negative predictor of AI citation. Manage faceted navigation by canonicalizing filter combinations, using noindex on low-value filter pages, and ensuring that your primary product category pages maintain clear hub-spoke structure."),

    ("javascript-seo",
     "JavaScript SEO: Ensuring AI Crawlers Can Read Your Content",
     "JavaScript-heavy sites render content client-side, which poses challenges for crawlers that may not execute JavaScript fully. If your content and internal links are rendered via JavaScript, they may not be present in the initial HTML that crawlers parse.\n\nFor AI optimization, ensure that critical content, internal links, and navigation are present in the initial HTML response or properly rendered during server-side rendering. Test your pages with JavaScript disabled to verify that crawlers can discover your content structure without client-side execution."),

    ("rendering-strategies",
     "Rendering Strategies: SSR, CSR, and ISR for AI Crawlability",
     "Server-side rendering (SSR), client-side rendering (CSR), and incremental static regeneration (ISR) each have different implications for how crawlers discover and extract your content. SSR and ISR provide complete HTML on first request, while CSR requires JavaScript execution.\n\nFor AI optimization, SSR and ISR are strongly preferred because they ensure that crawlers receive fully rendered content including all internal links, structured data, and text. CSR-only pages risk incomplete extraction, which means missing links in your graph and missing content in LLM retrieval indices."),

    ("ssr-vs-csr-vs-isr",
     "SSR vs CSR vs ISR: Choosing the Right Rendering for AI",
     "The choice between server-side rendering, client-side rendering, and incremental static regeneration affects both performance and crawlability. For content that needs to be discovered and cited by AI systems, the rendering strategy determines whether crawlers see your complete page content.\n\nSSR renders each page on the server per request — reliable but potentially slow. ISR pre-renders pages at build time and refreshes periodically — fast and crawlable. CSR renders in the browser — fast for users but invisible to many crawlers. For hub pages and pillar content, always use SSR or ISR."),

    ("headless-cms-seo",
     "Headless CMS and AI Optimization: Decoupling Content from Presentation",
     "A headless CMS separates content management from the presentation layer, delivering content via API to any frontend. This architecture provides flexibility but requires careful attention to ensure that the rendered pages maintain proper internal linking and crawlability.\n\nWhen using a headless CMS, ensure that your internal links are generated consistently from a centralized link graph rather than hardcoded in content. This makes it easier to maintain the hub-spoke structures and cross-section connectivity that drive AI citation. Use the CMS's relationship features to model topical connections between content items."),

    ("api-first-content",
     "API-First Content: Building for Both Humans and AI Crawlers",
     "An API-first content strategy creates content as structured data that can be served to multiple consumers — web pages, mobile apps, and AI crawlers. By treating content as structured data rather than embedded HTML, you gain control over how it's organized and linked.\n\nFor AI optimization, API-first content makes it easier to generate consistent internal linking, maintain topical relationships between content items, and produce machine-readable structured data alongside human-readable pages. The key is ensuring that the rendered output preserves the link graph and hierarchical structure."),

    # --- Content lifecycle (posts 38-44) ---
    ("content-freshness",
     "Content Freshness: How Recency Affects AI Citations",
     "Content freshness refers to how recently a page was published or updated. LLMs may prefer fresher content for time-sensitive queries, and crawlers may prioritize recently updated pages in their discovery cycle.\n\nFor AI optimization, maintain a regular update schedule for your hub pages and pillar content. Updated pages signal ongoing authority and relevance. Add last-modified dates, refresh statistics and examples, and update internal links to newly published supporting content to keep your content clusters fresh and well-connected."),

    ("evergreen-content",
     "Evergreen Content: Building Pages That Get Cited Year After Year",
     "Evergreen content remains relevant and accurate over time without requiring frequent updates. For AI citation, evergreen pages are valuable because they accumulate link equity and authority steadily, becoming increasingly established as reference material.\n\nThe best-performing content clusters combine evergreen pillar pages with regularly updated supporting content. The pillar provides stable authority that LLMs learn to reference, while supporting pages bring fresh perspectives and keep the cluster topically current. This combination maximizes both long-term citation accumulation and ongoing relevance."),

    ("updating-old-posts",
     "Updating Old Posts: Refreshing Content for AI Relevance",
     "Old posts with outdated information can drag down your cluster's authority signal. LLMs trained on recent data may learn to avoid citing pages with stale information, and crawlers deprioritize pages that haven't changed in a long time.\n\nRegularly audit your content clusters for outdated posts. Update statistics, refresh examples, add links to newer related content, and ensure that internal links still point to current hub pages. Each update triggers a recrawl that refreshes the page in LLM retrieval indices."),

    ("content-pruning",
     "Content Pruning: When to Remove Pages for Better Structure",
     "Content pruning is the deliberate removal or consolidation of low-performing pages to improve overall site quality and structure. Removing thin, duplicate, or outdated content concentrates link equity on your strongest pages.\n\nFor AI optimization, pruning improves your content clusters by removing noise that dilutes topical coherence. Our research shows that smaller, focused clusters outperform sprawling ones on a per-page basis. Prune pages that don't contribute to your cluster's topical authority, redirecting their URLs to the most relevant remaining page."),

    ("thin-content-fix",
     "Fixing Thin Content: Adding Substance for AI Citation",
     "Thin content — pages with little substantive information — rarely gets cited by LLMs because it doesn't provide enough value to serve as a source. Pages with fewer than 300 words, pages that mostly duplicate other content, and pages that don't address a specific question are all candidates for thin content remediation.\n\nFix thin content by either expanding it with substantive, original information or consolidating it into a more comprehensive page. For content clusters, thin pages weaken the overall authority signal because they receive internal links without contributing meaningful content to the topic."),

    ("duplicate-content",
     "Duplicate Content: How It Fragments Your Authority Signal",
     "Duplicate content occurs when substantially similar content appears at multiple URLs on your site. For AI optimization, duplicates fragment your link equity and confuse the authority signal that determines which page should be cited.\n\nIdentify duplicates by comparing content hashes or similarity scores across your page inventory. Consolidate duplicates into a single canonical page and redirect the redundant URLs. This concentrates link equity on a single authoritative version and prevents LLMs from encountering conflicting signals about which page represents your authoritative position on a topic."),

    # --- Keyword & intent (posts 45-52) ---
    ("keyword-cannibalization",
     "Keyword Cannibalization: When Your Pages Compete Against Themselves",
     "Keyword cannibalization occurs when multiple pages on your site target the same query, causing them to compete for the same citation opportunities. In AI search, this means the LLM may encounter multiple pages from your site on the same topic and select neither — or cite the wrong one.\n\nResolve cannibalization by consolidating competing pages into a single authoritative page, differentiating the remaining pages to target distinct subtopics, or establishing a clear hub-spoke relationship where the hub targets the primary query and spokes target long-tail variations."),

    ("search-intent-types",
     "Search Intent Types: Matching Content to What Users Actually Want",
     "Search intent is the purpose behind a user's query — informational, navigational, transactional, or commercial investigation. AI systems categorize queries by intent to select appropriate sources, and your content should match the intent it targets.\n\nInformational queries ('what is...', 'how does...') are best served by comprehensive guide pages that function as cluster hubs. Transactional queries ('buy', 'pricing') are served by product and pricing pages. Commercial investigation queries ('best', 'vs', 'review') are served by comparison content. Align your content structure to the intent landscape of your topic."),

    ("informational-queries",
     "Optimizing for Informational Queries in AI Search",
     "Informational queries are questions where users seek knowledge rather than products. LLMs cite informational content heavily because their primary use case is answering questions. Pages that provide clear, comprehensive, well-structured answers to common questions are prime citation targets.\n\nStructure your informational content as topic clusters with a hub page that provides a broad overview and spoke pages that go deep on subtopics. This mirrors how users explore topics and how LLMs decompose complex questions into sub-queries, increasing the chances that your content matches at least one stage of the answer generation process."),

    ("transactional-queries",
     "Transactional Queries and AI: When Users Want to Buy",
     "Transactional queries signal purchase intent. While LLMs handle these less frequently than informational queries, they do generate shopping advice and product recommendations that include citations. Product pages with rich, structured content and clear differentiation are most likely to be cited.\n\nFor transactional content, focus on providing comprehensive product information, transparent pricing, and genuine comparisons rather than marketing copy. LLMs select sources that provide useful information to the user, and product pages that read like marketing collateral are passed over in favor of pages that provide substantive, decision-useful content."),

    ("navigational-queries",
     "Navigational Queries: When Users Search for Your Brand",
     "Navigational queries are searches where users are looking for a specific brand or website. For these queries, LLMs typically cite the brand's own pages — making it essential that your site is structured to surface the right page for each branded query.\n\nEnsure that your hub pages are clearly the authoritative resource for your brand's key topics. If someone asks an LLM about your product's pricing, you want your pricing page cited — not a third-party review site. Strong internal linking from your homepage to key landing pages reinforces which pages should represent your brand."),

    ("long-tail-keywords",
     "Long-Tail Keywords in AI Search: Specificity Wins",
     "Long-tail keywords are specific, multi-word queries that reflect detailed questions. LLMs handle long-tail queries well because they can synthesize answers from multiple specific sources rather than relying on broad, general pages.\n\nFor AI optimization, long-tail content works best as spoke pages within a topic cluster. Each spoke targets a specific long-tail query while linking back to the hub page for broader context. This structure creates many citation opportunities across the long tail while concentrating authority on the hub for head queries."),

    ("semantic-search",
     "Semantic Search: How LLMs Understand Meaning Beyond Keywords",
     "Semantic search matches user queries to content based on meaning rather than exact keyword matches. LLMs use embeddings — numerical representations of text meaning — to assess similarity between queries and candidate pages.\n\nFor AI optimization, semantic search means that your content's topical coherence matters as much as its keyword targeting. Pages within a content cluster should share semantic vocabulary and concepts, reinforcing the cluster's topical signal. Our research shows that embedding variance (how semantically spread out a cluster's pages are) predicts citation rates, especially for larger clusters."),

    ("entity-seo",
     "Entity SEO: Building Your Brand's Knowledge Graph Presence",
     "Entity SEO focuses on establishing your brand and products as recognized entities in search knowledge graphs. When LLMs recognize your brand as an entity with known attributes, they're more likely to include it in relevant responses.\n\nBuild entity presence by maintaining consistent structured data across your site, ensuring your brand is accurately represented in knowledge bases like Wikipedia and Wikidata, and creating content that clearly associates your brand with specific topics and capabilities. Entity recognition helps LLMs connect your content to relevant queries."),

    # --- SERP features & platforms (posts 53-60) ---
    ("knowledge-graph-optimization",
     "Knowledge Graph Optimization: Getting Your Brand Recognized by AI",
     "Knowledge graphs are structured databases of entities and relationships that AI systems use to understand the world. Optimizing for knowledge graph inclusion means ensuring your brand, products, and key topics are represented as entities with clear, consistent attributes.\n\nImplement Organization, Product, and SoftwareApplication schema markup to establish your entities. Maintain consistent naming across all your pages and external references. Link your entity declarations to authoritative external sources (your Wikipedia page, industry directories) to reinforce entity recognition."),

    ("people-also-ask",
     "People Also Ask: Mining Questions for AI Content Optimization",
     "People Also Ask (PAA) boxes reveal the questions users commonly ask about a topic. These questions map directly to the queries that LLMs receive, making them a valuable source of content ideas for AI optimization.\n\nMine PAA questions to identify gaps in your content clusters. Each question is a potential spoke page that links back to your hub, expanding your cluster's topical coverage while targeting specific queries. Answer PAA questions comprehensively and structure your answers with clear headings that match the question format."),

    ("featured-snippets",
     "Featured Snippets and AI Citations: The Connection",
     "Featured snippets are concise answers displayed prominently in search results. The content selected for featured snippets often overlaps with content that LLMs choose to cite, because both systems favor clear, well-structured, authoritative answers.\n\nOptimize for featured snippets by structuring your content with clear question-answer patterns, using tables and lists for structured data, and ensuring your answers are concise yet comprehensive. Pages that earn featured snippets tend to have strong internal linking and clear topical authority — the same structural signals that predict LLM citation."),

    ("zero-click-searches",
     "Zero-Click Searches: When the Answer Is the Search Result",
     "Zero-click searches occur when users get their answer directly from the search results page without clicking through to any website. AI Overviews and featured snippets are the primary drivers of zero-click behavior.\n\nFor AI optimization, zero-click searches are not necessarily bad — if your page is cited in the AI Overview, your brand gets visibility even without a click. The goal is to be the cited source. Structure your content to provide the kind of clear, authoritative answers that AI systems extract for direct display."),

    ("voice-search-optimization",
     "Voice Search Optimization: Conversational Queries and AI",
     "Voice search queries tend to be more conversational and question-oriented than typed searches. As voice assistants increasingly use LLMs to generate answers, optimizing for voice search aligns closely with optimizing for AI citation.\n\nStructure your content to answer conversational questions directly. Use natural language in your headings, provide concise answers in the first paragraph followed by detailed elaboration, and ensure your FAQ content covers the question formats people use in voice search."),

    ("visual-search-seo",
     "Visual Search SEO: Image Content for AI Discovery",
     "Visual search allows users to search using images rather than text. AI systems that process visual queries need to match images to relevant web pages, making image content and metadata important for discovery.\n\nOptimize images with descriptive alt text, captions, and surrounding context that reinforce your page's topical focus. Ensure images are included in your XML sitemap and that image-heavy pages are well-linked within your content clusters. Visual content strengthens a page's topical signal when the image context aligns with the cluster's theme."),

    ("video-seo-basics",
     "Video SEO: Making Video Content Discoverable by AI",
     "Video content is increasingly important for AI search, as LLMs incorporate multimodal content into their responses. Videos hosted on your site with proper markup, transcripts, and metadata can contribute to your page's authority and citability.\n\nEmbed videos within your content hierarchy and provide full transcripts that reinforce your cluster's topical vocabulary. Use VideoObject schema markup to help AI systems understand your video content. Pages with video plus text content tend to be richer reference sources than text-only pages."),

    ("youtube-seo",
     "YouTube SEO: Video Content That Supports Your AI Visibility Strategy",
     "YouTube videos can reinforce your brand's topical authority and drive AI visibility when they're integrated into your broader content strategy. YouTube descriptions and transcripts are indexed and can influence how LLMs perceive your brand's expertise.\n\nLink YouTube videos to related pages on your site and embed them in relevant hub pages. Use consistent topical vocabulary across your video titles, descriptions, and associated web content. This cross-platform consistency strengthens the topical signal that AI systems use to identify authoritative sources."),

    ("podcast-seo",
     "Podcast SEO: Making Audio Content Work for AI Discovery",
     "Podcasts generate long-form content that, when transcribed and published, creates valuable text assets for AI discovery. Each episode transcript can serve as a supporting page within a content cluster, linking back to the relevant hub page.\n\nPublish podcast transcripts as individual pages on your site with proper headings, timestamps, and links to related content. Structure transcripts with clear topic sections that reinforce your cluster's vocabulary and link to your pillar pages for deeper reading."),

    # --- Image & media optimization (posts 61-64) ---
    ("image-alt-text",
     "Image Alt Text: Accessibility and AI Content Understanding",
     "Alt text provides textual descriptions of images that help both accessibility tools and AI crawlers understand image content. Well-written alt text reinforces your page's topical focus and provides additional context for content extraction.\n\nWrite alt text that describes the image's content and relevance to the page topic. Avoid keyword stuffing — instead, use natural descriptions that would help someone who can't see the image understand what it shows and why it's relevant to the surrounding content."),

    ("webp-images",
     "WebP Images: Performance and AI Crawling Efficiency",
     "WebP is a modern image format that provides superior compression without significant quality loss. Smaller image files lead to faster page loads, which improves both user experience and crawler efficiency.\n\nConvert your images to WebP format with appropriate quality settings. Faster-loading pages are crawled more completely within time budgets, ensuring that all your internal links and content are extracted. This is especially important for image-heavy pages in product and portfolio clusters."),

    ("lazy-loading",
     "Lazy Loading: Performance vs AI Crawl Completeness",
     "Lazy loading defers the loading of below-the-fold images and content until the user scrolls to them. While this improves initial page load times, it can hide content from crawlers that don't simulate scrolling.\n\nFor AI optimization, be selective about what you lazy-load. Internal links, text content, and navigation should always be present in the initial HTML. Only lazy-load images and supplementary media that don't contain essential content or linking. Test with JavaScript disabled to verify that critical content and links are accessible without lazy loading."),

    ("infinite-scroll-seo",
     "Infinite Scroll: AI Crawling Challenges and Solutions",
     "Infinite scroll replaces pagination with continuous content loading as users scroll. For AI crawlers, this creates challenges because the crawler may only see the initial batch of content, missing pages and links that load dynamically.\n\nIf your site uses infinite scroll, implement a hybrid approach: provide a paginated HTML fallback for crawlers while showing infinite scroll to users. Ensure that all content items and their internal links are discoverable through the paginated version so crawlers can map your complete link graph."),

    # --- Link building (posts 65-71) ---
    ("link-building-2025",
     "Link Building in 2025: Authority Signals for AI Search",
     "Link building in the AI era focuses on acquiring links that signal genuine authority rather than simply boosting PageRank. External links from authoritative sources in your domain help LLMs recognize your brand as a trusted reference.\n\nPrioritize earning links from industry publications, academic sources, and recognized authority sites in your niche. These links signal to AI systems that your content is valued by domain experts. Combine external link building with strong internal linking to create a comprehensive authority signal."),

    ("digital-pr",
     "Digital PR: Earning Authority Through Media Coverage",
     "Digital PR generates media coverage and backlinks from authoritative publications. For AI search, PR-generated links from news sites, industry publications, and influential blogs provide strong external authority signals.\n\nFocus your digital PR on generating coverage that links to your hub pages and pillar content rather than one-off campaign pages. This directs external authority into the center of your content clusters, reinforcing the hub pages that LLMs are most likely to cite."),

    ("haro-outreach",
     "HARO Outreach: Earning Expert Citations from Journalists",
     "HARO (Help A Reporter Out) connects subject matter experts with journalists seeking sources. Responding to relevant queries can earn your brand citations and backlinks from high-authority media sites.\n\nWhen responding to HARO queries, link journalists to your most authoritative content — your hub pages and pillar articles. This creates external links pointing into the center of your content clusters, strengthening the authority signal that drives AI citations."),

    ("guest-posting-strategy",
     "Guest Posting Strategy: Building Authority Through Contributed Content",
     "Guest posting on relevant industry publications builds external authority and creates backlinks to your content. For AI search optimization, the key is targeting publications that AI systems recognize as authoritative in your domain.\n\nFocus guest posts on topics aligned with your content clusters and link back to your hub pages. Each guest post should reinforce your brand's association with specific topics, strengthening the entity signal that helps LLMs connect your brand to relevant queries."),

    ("broken-link-building",
     "Broken Link Building: Reclaiming Lost Authority",
     "Broken link building identifies pages that link to dead URLs and offers your content as a replacement. This reclaims link equity that would otherwise be lost and builds new authority signals pointing to your content.\n\nTarget broken links on authoritative sites in your domain that pointed to content similar to your hub pages. When offering replacements, link to your most authoritative content cluster pages to direct the reclaimed authority where it has the most impact."),

    ("resource-page-links",
     "Resource Page Links: Getting Listed as an Authority Source",
     "Resource pages curate links to the best content on a topic. Getting listed on authoritative resource pages signals domain expertise and creates high-value backlinks to your content.\n\nTarget resource pages in your topic area and submit your hub pages and comprehensive guides for inclusion. Resource page links are particularly valuable for AI search because they represent editorial endorsements of your content's authority — exactly the kind of signal that helps LLMs identify trusted sources."),

    ("skyscraper-technique",
     "The Skyscraper Technique: Building Better Content for AI Citation",
     "The skyscraper technique involves finding high-performing content in your niche, creating something substantially better, and reaching out to sites that linked to the original to suggest your improved version.\n\nFor AI search, the skyscraper technique works best when you create comprehensive hub pages that surpass existing content in depth, structure, and topical coverage. A well-structured pillar page with supporting spoke content is inherently more citable than a single long-form article because it provides the hierarchical organization that LLMs prefer."),

    # --- Content distribution (posts 72-76) ---
    ("content-syndication",
     "Content Syndication: Amplifying Reach Without Diluting Authority",
     "Content syndication republishes your content on third-party platforms to reach wider audiences. For AI search, syndication creates risks of duplicate content but can also increase your brand's visibility across the sources that LLMs draw from.\n\nWhen syndicating content, always use canonical tags pointing back to your original page. Syndicate supporting content rather than hub pages, and ensure the syndicated versions link back to your authoritative site. This amplifies reach while concentrating authority on your primary content clusters."),

    ("medium-vs-blog",
     "Medium vs Your Blog: Where to Publish for AI Visibility",
     "Publishing on Medium gives you access to a built-in audience but means your content lives on a domain you don't control. For AI search optimization, content published on your own site contributes directly to your domain's authority and content cluster structure.\n\nUse your blog as the primary publication venue for content you want cited by AI. Use Medium and other platforms for abbreviated versions that drive traffic back to your full articles. Your site's internal link graph — which drives AI citation — only benefits from content published on your domain."),

    ("linkedin-articles-seo",
     "LinkedIn Articles: Professional Content for AI Discovery",
     "LinkedIn articles reach professional audiences and can be indexed by search engines and AI crawlers. Publishing thought leadership on LinkedIn extends your brand's topical presence across platforms that LLMs may draw from.\n\nUse LinkedIn articles to reinforce your expertise in topics aligned with your content clusters. Reference and link to your hub pages, encouraging readers to explore your site's comprehensive resources. Cross-platform topical consistency strengthens the association between your brand and your key topics."),

    ("reddit-for-seo",
     "Reddit for SEO: Community Content That AI Citations Draw From",
     "Reddit discussions are increasingly cited by AI systems because they contain authentic, detailed user perspectives. Brands that participate genuinely in relevant subreddits can influence the information landscape that LLMs draw from.\n\nContribute substantive, helpful answers in subreddits related to your domain. Reference your site's authoritative content when genuinely relevant, but prioritize being helpful over promoting links. Reddit participation builds brand recognition across a platform that LLMs increasingly index and cite."),

    ("quora-for-seo",
     "Quora for SEO: Answering Questions That LLMs Also Answer",
     "Quora is a question-and-answer platform where users post questions that closely mirror the queries people ask LLMs. Providing authoritative answers on Quora positions your brand as an expert in your domain.\n\nAnswer Quora questions that align with your content clusters, referencing your hub pages for comprehensive coverage. Well-written Quora answers can be cited by LLMs directly, and they reinforce your brand's association with specific topics across the platforms that feed LLM training data."),

    ("community-driven-seo",
     "Community-Driven SEO: How User-Generated Content Builds Authority",
     "Community-driven content — forums, comments, user reviews — adds depth and authenticity to your site. When users contribute relevant content, they expand your topical coverage and create additional pages within your content clusters.\n\nModerate community content to ensure quality and topical relevance. Integrate user-generated pages into your internal link structure by linking them to relevant hub pages and ensuring they follow your site's naming and organizational conventions. Quality community content strengthens your cluster's topical signal."),

    ("user-generated-content",
     "User-Generated Content: Harnessing Customer Voices for AI Authority",
     "User-generated content (UGC) including reviews, testimonials, case studies, and forum posts adds authentic perspectives that enrich your content clusters. LLMs value diverse, genuine content and may prefer pages with real user input over corporate marketing copy.\n\nCurate and showcase UGC within your content hierarchy. Feature customer reviews on product hub pages, highlight community discussions on topic pages, and link user-contributed content to your authoritative pillar pages. This creates organic depth that signals genuine topical authority."),

    # --- Schema types (posts 77-78) ---
    ("review-schema",
     "Review Schema: Structured Ratings for AI Product Recommendations",
     "Review schema markup provides structured rating and review data that AI systems can extract and incorporate into product recommendations. Pages with review schema are more likely to be cited in comparative and evaluative queries.\n\nImplement AggregateRating and Review schema on product and service pages. Include structured review data from verified customers, and link review pages to your product hub pages to strengthen the connection between social proof and your core product content."),

    ("product-schema",
     "Product Schema: Helping AI Understand Your Offerings",
     "Product schema provides structured data about your products including pricing, availability, specifications, and ratings. AI systems use product schema to generate accurate product recommendations and comparisons.\n\nImplement detailed Product schema on all product pages, including offers, reviews, and brand information. Link product pages to relevant category hubs and comparison content within your product cluster. Comprehensive product schema helps AI systems cite your pages accurately in shopping and comparison queries."),

    # --- Local & ecommerce (posts 79-87) ---
    ("local-seo-basics",
     "Local SEO: Geographic Content Structure for AI Discovery",
     "Local SEO optimizes your content for geographically specific queries. AI systems handle local queries by looking for content with clear geographic signals — location pages, local service descriptions, and regional content.\n\nCreate dedicated location pages for each area you serve and organize them within a geographic content cluster. Link location pages to your main service hub pages and include structured LocalBusiness data. This geographic content structure helps AI systems cite your pages for region-specific queries."),

    ("google-business-profile",
     "Google Business Profile: Local Entity Signals for AI",
     "Your Google Business Profile establishes your brand as a recognized local entity. AI systems that incorporate Google's knowledge graph use business profile data to verify and enrich their understanding of your brand.\n\nMaintain an accurate, complete Google Business Profile with consistent information matching your website. Link your profile to your site's location hub pages and ensure that your business name, address, and phone number are consistent across your site and external directories."),

    ("multi-location-seo",
     "Multi-Location SEO: Scaling Geographic Content Structure",
     "Multi-location businesses need a content structure that provides unique, valuable content for each location while maintaining overall brand authority. Simply duplicating templates across location pages creates thin content that won't get cited.\n\nCreate a location hub page that links to individual location pages, each with unique local content including local team information, regional services, community involvement, and local customer stories. This creates a geographic content cluster with genuine depth rather than templated repetition."),

    ("ecommerce-seo-guide",
     "Ecommerce SEO Guide: Product Content Structure for AI",
     "Ecommerce sites face unique AI optimization challenges due to large page counts, dynamic inventory, and faceted navigation. The structural patterns that predict citation apply to ecommerce: hub-spoke product categories outperform flat product meshes.\n\nOrganize your product catalog into category hub pages that link to individual product pages. Each category should function as a content cluster with the category page as the hub. Avoid mesh patterns where every product links to every other through category navigation — this creates the high-density, low-citability pattern identified in our research."),

    ("category-page-optimization",
     "Category Page Optimization: Building Product Hubs That Get Cited",
     "Category pages serve as hub pages for your product clusters. A well-optimized category page provides comprehensive overview content, organizes products logically, and functions as the authoritative reference for that product area.\n\nGo beyond simple product grids. Add editorial category descriptions, buying guides, comparison information, and links to detailed resources. Category pages with rich, original content serve as genuine hub pages that attract internal links from supporting content and earn AI citations for category-level queries."),

    ("product-page-seo",
     "Product Page SEO: Individual Product Content for AI Citations",
     "Individual product pages are the spoke content in your ecommerce clusters. For AI citation, product pages need to provide substantive, unique content that goes beyond specifications and marketing copy.\n\nInclude detailed product descriptions, use cases, comparison information, and customer context on each product page. Link each product page to its category hub and to related products within the same cluster. Product pages with genuine editorial content are more likely to be cited in product recommendation and comparison queries."),
]

add_page(
    blog_index,
    "# Acme Blog\n\nExpert insights on AI search optimization, content structure strategy, and the "
    "evolving landscape of LLM-driven content discovery. Our blog covers everything from foundational "
    "concepts in AI visibility to advanced technical SEO tactics and real-world content architecture "
    "patterns that drive LLM citations.",
    [],
)

blog_posts = [f"https://acme.com/blog/{slug}" for slug, _, _ in blog_entries]

for slug, title, body in blog_entries:
    url = f"https://acme.com/blog/{slug}"
    links = [blog_index]
    if random.random() < 0.15:
        links += pick([p for p in blog_posts if p != url], random.randint(1, 2))
    add_page(url, f"# {title}\n\n{body}", links)

pages[blog_index]["links"] = pick(blog_posts, 8)


# =============================================================================
# PRODUCTS — MESH (~60 pages)
# Every product links to every product in its category via shared nav.
# High density, high reciprocity, low degree_gini. The "bad" pattern.
# =============================================================================

product_descriptions = {
    "analytics": {
        "intro": "Real-time analytics for understanding how your brand appears across AI search platforms.",
        "items": {
            "analytics-1": ("Citation Volume Tracker", "Monitors the total number of times your pages are cited across all tracked LLM platforms. Aggregates citation counts by page, query category, and time period to show trends in your AI visibility over time."),
            "analytics-2": ("Share of Voice Dashboard", "Compares your brand's citation frequency against competitors for your tracked topics. Calculates share-of-voice percentages and visualizes competitive positioning across AI platforms."),
            "analytics-3": ("Query Coverage Analyzer", "Maps which queries in your topic space result in citations of your content and identifies gaps where competitors are cited but you are not. Prioritizes query gaps by search volume and relevance."),
            "analytics-4": ("Citation Context Analyzer", "Extracts and categorizes the context in which your pages are cited — whether as a primary source, supporting evidence, comparison reference, or product recommendation. Understanding citation context reveals how LLMs perceive your content."),
            "analytics-5": ("Platform Breakdown Report", "Breaks down your AI visibility by platform — ChatGPT, Perplexity, Google AI Overviews, Claude, and others. Each platform's retrieval system has different biases, and this report reveals where your content structure performs best and worst."),
            "analytics-6": ("Trend Detection Engine", "Identifies emerging trends in your citation patterns before they become obvious. Uses time-series analysis to detect acceleration or deceleration in citation rates across topics, platforms, and content clusters."),
            "analytics-7": ("Audience Insight Module", "Analyzes the types of queries that generate citations to your content, revealing what audiences are asking about your brand and how AI systems characterize your expertise."),
            "analytics-8": ("Custom Metric Builder", "Lets you define custom metrics by combining citation data with your own KPIs — revenue attribution, lead quality, conversion rates — to measure the business impact of AI visibility."),
            "analytics-9": ("Historical Benchmarking", "Tracks your AI visibility metrics over time against historical baselines. Shows whether structural improvements to your site are translating into measurable citation gains."),
            "analytics-10": ("Anomaly Detector", "Alerts you when citation patterns deviate significantly from expected trends. Catches sudden drops in visibility that may indicate crawl issues, content problems, or competitive displacement."),
            "analytics-11": ("Geographic Visibility Map", "Shows your citation rates broken down by geographic region, revealing where your content resonates most strongly and where regional competitors may be capturing your potential citations."),
            "analytics-12": ("Topic Authority Score", "Computes a composite authority score for each of your tracked topics based on citation frequency, citation context, and competitive positioning. Tracks authority scores over time to measure progress."),
            "analytics-13": ("Engagement Correlation", "Correlates your AI citation data with website engagement metrics — traffic, bounce rate, conversion — to understand the downstream impact of AI visibility on business outcomes."),
            "analytics-14": ("Executive Summary Generator", "Auto-generates executive-ready summaries of your AI visibility performance, highlighting key wins, risks, and recommended actions based on the latest citation data."),
        },
    },
    "optimization": {
        "intro": "Tools for improving your site's content structure to maximize LLM citation rates.",
        "items": {
            "optimization-1": ("Content Structure Scorer", "Analyzes your site's internal link topology and produces a structural health score for each content cluster. Scores are based on the structural signals that predict LLM citation — hub dominance, link density, cross-section connectivity, and topical coherence."),
            "optimization-2": ("Internal Link Auditor", "Maps your site's complete internal link graph and identifies structural issues — orphan pages with no inbound links, link density hotspots that create mesh anti-patterns, and missing connections between topically related clusters."),
            "optimization-3": ("Hub Page Identifier", "Detects existing hub pages in your content clusters by analyzing in-degree distribution and PageRank concentration. Recommends which pages should serve as hubs and which pages need to be restructured as supporting spoke content."),
            "optimization-4": ("Link Recommendation Engine", "Generates specific internal link suggestions — which pages should link to which, with recommended anchor text — to improve your content cluster structure based on the patterns that predict high citation rates."),
            "optimization-5": ("Cluster Health Monitor", "Continuously monitors the structural health of your content clusters and alerts you when metrics drift. Detects when new content has been published without proper internal linking or when structural changes have degraded cluster quality."),
            "optimization-6": ("Content Gap Finder", "Identifies topical gaps within your content clusters where supporting spoke content is missing. Recommends new pages to create and where they should sit in your link hierarchy."),
            "optimization-7": ("Topology Visualizer", "Renders interactive network visualizations of your content clusters showing link structure, hub pages, spoke pages, and cross-cluster connections. Color-codes by structural health to identify problem areas at a glance."),
            "optimization-8": ("A/B Structure Tester", "Tests structural changes in controlled experiments. Apply link modifications to a subset of clusters, measure citation impact over time, and determine whether structural optimizations translate to measurable visibility gains."),
            "optimization-9": ("Batch Link Optimizer", "Applies link recommendations in bulk across your site. Previews the projected impact of each batch of changes and simulates the resulting graph structure before committing any modifications."),
            "optimization-10": ("Freshness Scheduler", "Schedules content updates based on freshness signals and citation performance. Prioritizes updates to hub pages and high-value cluster content that would benefit most from a refresh cycle."),
            "optimization-11": ("Redirect Mapper", "Manages URL redirects during content restructuring to preserve link equity. Plans redirect chains, validates that equity flows to the intended target, and monitors for redirect loops or chains."),
            "optimization-12": ("Cannibalization Resolver", "Detects pages competing for the same queries and recommends consolidation, differentiation, or hub-spoke restructuring to eliminate internal competition."),
            "optimization-13": ("Pruning Advisor", "Identifies low-value pages that weaken cluster quality — thin content, outdated pages, duplicates — and recommends removal or consolidation strategies that preserve link equity."),
        },
    },
    "monitoring": {
        "intro": "Continuous monitoring of your brand's presence across AI search platforms.",
        "items": {
            "monitoring-1": ("Real-Time Citation Feed", "Streams citation events as they're detected across monitored AI platforms. Each event includes the citing query, the AI platform, the cited URL, citation context, and whether your brand was mentioned in the original query."),
            "monitoring-2": ("Competitor Citation Tracker", "Monitors your competitors' citation rates across the same queries and topics you track. Shows when competitors gain or lose visibility and correlates changes with their content structure modifications."),
            "monitoring-3": ("Brand Mention Monitor", "Tracks mentions of your brand name across AI responses, distinguishing between cited mentions (with URL) and uncited mentions (brand name only). Uncited mentions represent conversion opportunities — pages the LLM knows about but doesn't link to."),
            "monitoring-4": ("Alert Configuration Panel", "Configures real-time alerts for citation events — new citations, lost citations, competitor gains, anomalous patterns. Routes alerts to Slack, email, or webhooks based on severity and type."),
            "monitoring-5": ("Crawl Health Dashboard", "Monitors how effectively AI crawlers are discovering and indexing your content. Tracks crawl frequency, coverage completeness, and extraction quality for each content cluster."),
            "monitoring-6": ("Index Coverage Report", "Shows which of your pages are present in each AI platform's retrieval index. Pages missing from the index can't be cited regardless of their content quality, making index coverage a prerequisite for visibility."),
            "monitoring-7": ("Response Quality Analyzer", "Evaluates how accurately AI responses represent your brand when citing your pages. Detects mischaracterizations, outdated information, or misleading context surrounding your citations."),
            "monitoring-8": ("Sentiment Tracker", "Analyzes the sentiment of AI responses that mention or cite your brand. Tracks whether your brand is being described positively, neutrally, or negatively across different topics and platforms."),
            "monitoring-9": ("Citation Decay Monitor", "Tracks the lifecycle of individual citations — how long they persist across model updates. Detects when previously stable citations are lost, which may indicate changes in the model's training data or retrieval system."),
            "monitoring-10": ("Multi-Brand Tracker", "Manages monitoring across multiple brands for agencies and enterprise clients. Provides unified dashboards with brand-specific filtering and comparative analytics."),
            "monitoring-11": ("Query Drift Detector", "Monitors how the queries generating citations to your content evolve over time. Detects when the query landscape shifts — new question patterns emerging, old patterns declining."),
            "monitoring-12": ("Compliance Monitor", "Verifies that AI responses citing your content comply with your brand guidelines, include required disclaimers, and accurately represent your products and services."),
            "monitoring-13": ("Integration Health Check", "Monitors the status and data freshness of all connected integrations — CMS, analytics, CRM — ensuring your monitoring data is complete and up-to-date."),
            "monitoring-14": ("Weekly Digest Generator", "Compiles a weekly summary of all monitoring signals — new citations, lost citations, competitor changes, anomalies — into a digestible report for stakeholders."),
        },
    },
    "reporting": {
        "intro": "Comprehensive reporting tools for communicating AI visibility performance to stakeholders.",
        "items": {
            "reporting-1": ("Executive Dashboard", "High-level overview of AI visibility KPIs for leadership. Shows total citations, share of voice, citation trend, and competitive positioning in a format designed for executive consumption."),
            "reporting-2": ("Team Performance Report", "Breaks down AI visibility metrics by content team, topic area, or business unit. Shows which teams are producing content that earns citations and where additional investment would have the highest impact."),
            "reporting-3": ("ROI Attribution Model", "Attributes revenue and pipeline impact to AI visibility by correlating citation data with conversion events. Calculates the ROI of content structure improvements based on citation-driven traffic and engagement."),
            "reporting-4": ("Competitive Intelligence Brief", "Monthly competitive analysis showing how your AI visibility compares to tracked competitors across topics, platforms, and query categories. Highlights competitive threats and opportunities."),
            "reporting-5": ("Content Performance Scorecard", "Scores each piece of content by its contribution to AI visibility — citation count, citation context quality, cluster structural impact. Ranks content from highest to lowest impact to inform editorial decisions."),
            "reporting-6": ("Client Report Builder", "For agencies: builds branded client reports with customizable sections, white-label options, and automated delivery schedules. Includes commentary templates and benchmark comparisons."),
            "reporting-7": ("Board Presentation Export", "Exports key metrics in presentation-ready format with trend charts, competitive comparisons, and strategic recommendations suitable for board-level reporting."),
            "reporting-8": ("Quarterly Business Review", "Comprehensive quarterly analysis covering AI visibility trends, structural improvements, competitive landscape changes, and forward-looking recommendations with prioritized action items."),
            "reporting-9": ("Data Export API", "Programmatic access to all reporting data via REST API. Enables integration with external BI tools, data warehouses, and custom reporting workflows."),
            "reporting-10": ("Scheduled Report Delivery", "Automates report generation and delivery on daily, weekly, or monthly schedules. Routes different report types to different stakeholders based on their role and information needs."),
            "reporting-11": ("Custom Dashboard Builder", "Drag-and-drop dashboard creation with widgets for citation metrics, competitive data, structural health scores, and trend visualizations. Share dashboards with team members and stakeholders."),
            "reporting-12": ("Annotation Layer", "Add notes, milestones, and context to your reporting data. Mark content launches, structural changes, and competitor events on your trend charts to correlate actions with outcomes."),
            "reporting-13": ("Benchmark Library", "Industry benchmarks for AI visibility metrics based on aggregated, anonymized data from the platform. Compare your performance against peers in your industry vertical."),
            "reporting-14": ("Goal Tracking", "Set AI visibility goals — target citation rates, share-of-voice thresholds, structural health scores — and track progress with visual indicators and projected timelines."),
        },
    },
}

all_products = []
products_index = "https://acme.com/products"
cat_indices = []

for cat, cat_data in product_descriptions.items():
    cat_index = f"https://acme.com/products/{cat}"
    cat_indices.append(cat_index)
    cat_products = [f"https://acme.com/products/{cat}/{slug}" for slug in cat_data["items"]]
    all_products.extend(cat_products)

    for prod_url in cat_products:
        slug = prod_url.split("/")[-1]
        name, desc = cat_data["items"][slug]
        siblings = [p for p in cat_products if p != prod_url]
        add_page(prod_url, f"# {name}\n\n{desc}", siblings + [cat_index])

    add_page(cat_index, f"# {cat.title()} Products\n\n{cat_data['intro']}", cat_products)

add_page(products_index, "# Products\n\nThe complete AI search optimization platform. Monitor your brand's visibility across LLM platforms, optimize your content structure for maximum citation rates, and measure the business impact of AI-driven discovery.", cat_indices)


# =============================================================================
# DOCS — TREE (~70 pages)
# Strict hierarchy: index → sections → subsections → leaf pages.
# Low density, clear depth variation, moderate hub structure.
# =============================================================================

docs_index = "https://acme.com/docs"

# Each section has coherent technical documentation that builds progressively.
section_defs = {
    "getting-started": {
        "desc": "Everything you need to set up the Acme platform, from installation through your first analysis project. Follow these guides in order to get up and running quickly.",
        "pages": {
            "installation": ("Installation", "Install the Acme platform using Docker, package manager, or direct download. System requirements include Python 3.11+, PostgreSQL 15+ with pgvector, and 4GB RAM minimum. The platform runs as a set of microservices that can be deployed locally for development or on Kubernetes for production."),
            "quickstart": ("Quickstart Guide", "Get your first content analysis running in under 10 minutes. This quickstart walks you through connecting your first brand, triggering a site crawl, and viewing your initial content structure analysis. Prerequisites: complete installation and have your site URL ready."),
            "configuration": ("Configuration Reference", "Acme is configured through environment variables and a YAML configuration file. Key settings include database connection, crawl parameters (depth limits, rate limiting, user agent), embedding model selection, and citation monitoring schedules. This page covers all configuration options with defaults and examples."),
            "authentication": ("Authentication Setup", "Configure authentication for platform access. Acme supports SSO via SAML 2.0 and OIDC, API key authentication for programmatic access, and session-based authentication for the web interface. This guide covers each authentication method with configuration examples."),
            "first-project": ("Your First Project", "Create your first content analysis project by connecting a brand, configuring crawl parameters, and running your initial structural analysis. This tutorial walks through each step with screenshots and explains what each metric means."),
            "cli-reference": ("CLI Reference", "The Acme CLI provides command-line access to all platform features. Commands include crawl management, analysis triggers, report generation, and data export. This reference covers every command with usage examples and flags."),
        },
    },
    "api-reference": {
        "desc": "Complete API documentation for the Acme platform. All endpoints require authentication via API key or session token. Responses are JSON with consistent error handling.",
        "pages": {
            "rest-api": ("REST API Overview", "The Acme REST API provides programmatic access to all platform features. Base URL is your instance domain followed by /api/v1/. All endpoints accept and return JSON. Authentication is via Bearer token in the Authorization header. Rate limits are 1000 requests per minute per API key."),
            "graphql-api": ("GraphQL API", "The GraphQL API provides flexible querying for complex data retrieval needs. The schema exposes brands, pages, citations, clusters, and structural metrics with full relationship traversal. Use the GraphQL playground at /graphql for interactive schema exploration."),
            "webhooks": ("Webhooks", "Configure webhooks to receive real-time notifications when events occur — new citations detected, crawl completed, structural score changed, competitor alert triggered. Webhooks deliver signed JSON payloads to your configured endpoint with automatic retry on failure."),
            "rate-limits": ("Rate Limits", "API rate limits are enforced per API key. Standard keys allow 1000 requests per minute with burst up to 50 concurrent requests. Enterprise keys have configurable limits. Rate limit headers are included in every response: X-RateLimit-Limit, X-RateLimit-Remaining, X-RateLimit-Reset."),
            "error-codes": ("Error Codes", "Acme API uses standard HTTP status codes with additional error codes in the response body. 400-series errors include validation details. 500-series errors include a trace ID for support escalation. All errors return a consistent JSON structure with code, message, and details fields."),
            "pagination": ("Pagination", "List endpoints return paginated results using cursor-based pagination. Each response includes a next_cursor field — pass this as the cursor query parameter to fetch the next page. Default page size is 50, configurable up to 200. Total count is returned in the X-Total-Count header."),
            "filtering": ("Filtering and Sorting", "List endpoints support filtering via query parameters. Filters use the field[operator]=value syntax — for example, created_at[gte]=2024-01-01. Sorting uses the sort parameter with field name and optional direction: sort=citations_count:desc. Multiple sort fields are comma-separated."),
            "sdks": ("SDKs and Client Libraries", "Official SDKs are available for Python, TypeScript, and Go. Each SDK provides typed interfaces, automatic pagination handling, rate limit management, and webhook signature verification. Install via pip, npm, or go get."),
            "authentication-api": ("Authentication API", "The authentication API manages API keys, session tokens, and SSO integration. Endpoints include key generation, rotation, revocation, and scope management. SSO configuration endpoints handle SAML and OIDC provider setup."),
            "batch-api": ("Batch API", "The batch API allows submitting multiple operations in a single request. Submit up to 100 operations per batch, each independently processed. Responses include per-operation results with status codes. Use batch operations for bulk updates, mass analysis triggers, or multi-brand operations."),
            "streaming-api": ("Streaming API", "The streaming API provides real-time event streams via Server-Sent Events (SSE). Connect to event streams for citation events, crawl progress, analysis updates, and alert notifications. Each stream includes heartbeat events and supports resumption via Last-Event-ID."),
        },
    },
    "guides": {
        "desc": "Step-by-step guides for common workflows and advanced usage patterns. Each guide walks through a complete workflow from start to finish.",
        "pages": {
            "crawl-setup": ("Setting Up Your First Crawl", "Configure and run a site crawl for content structure analysis. Set crawl depth (recommended: 3-5 levels), page limits, rate limiting to respect target site performance, and content extraction parameters. The crawler extracts page content, internal links, metadata, and structural signals."),
            "citation-tracking": ("Setting Up Citation Tracking", "Configure citation monitoring for your tracked topics. Define the queries you want to monitor, select the AI platforms to track, set monitoring frequency, and configure citation matching rules. The system uses URL normalization and fuzzy matching to identify your pages in AI responses."),
            "brand-monitoring": ("Brand Monitoring Configuration", "Set up comprehensive brand monitoring across AI platforms. Configure brand name variants, competitor brands, topic areas, and monitoring schedules. The system tracks brand mentions, citations, sentiment, and competitive positioning across all configured platforms."),
            "competitor-analysis": ("Running Competitor Analysis", "Analyze competitor content structures alongside your own. Add competitor domains, trigger comparative crawls, and view side-by-side structural metrics. Identify structural advantages competitors have that correlate with their higher citation rates."),
            "custom-reports": ("Building Custom Reports", "Create tailored reports for different stakeholders using the report builder. Select metrics, set date ranges, add comparative benchmarks, and configure automated delivery. Reports can combine citation data, structural metrics, competitive intelligence, and business impact data."),
            "integrations": ("Integration Setup Guide", "Connect Acme with your existing tools — CMS, analytics, CRM, and communication platforms. Each integration requires API credentials and permission configuration. This guide covers setup for all supported integrations."),
            "data-export": ("Data Export and Warehousing", "Export your Acme data to external systems for custom analysis. Export formats include CSV, JSON, and Parquet. Schedule automated exports to cloud storage (S3, GCS) or data warehouses (Snowflake, BigQuery). The export API supports incremental exports for efficient data pipelines."),
            "bulk-operations": ("Bulk Operations Guide", "Perform operations at scale — bulk brand creation, mass crawl triggers, batch analysis runs, and multi-brand reporting. Use the batch API or CSV upload for operations exceeding what the UI supports efficiently."),
            "white-labeling": ("White-Label Configuration", "Configure white-label settings for agency or enterprise deployments. Customize branding, domain, email sender, and report templates. White-label settings apply to the web interface, email notifications, exported reports, and API responses."),
            "multi-brand": ("Multi-Brand Management", "Manage multiple brands within a single workspace. Organize brands into groups, configure shared monitoring settings, run cross-brand analyses, and generate comparative reports. Enterprise workspaces support unlimited brands with role-based access control."),
            "agency-setup": ("Agency Workspace Setup", "Configure Acme for agency use with multiple client brands. Set up client workspaces with isolated data and billing, configure white-label reporting, and establish cross-client benchmarking. Agency plans include delegated administration and client-facing dashboards."),
        },
    },
    "concepts": {
        "desc": "Conceptual documentation explaining how the Acme platform works under the hood. Understanding these concepts helps you make better decisions about configuration and optimization strategies.",
        "pages": {
            "how-crawling-works": ("How Crawling Works", "The Acme crawler is a recursive web crawler that discovers and extracts content from websites. Starting from a seed URL, it follows internal links to discover pages, extracting content as markdown, internal and external links as structured data, and page metadata. Crawl depth, rate limiting, and content extraction are all configurable."),
            "embedding-model": ("The Embedding Model", "Acme generates semantic embeddings for each page using the title, H1 heading, and introductory text. These 768-dimensional vectors capture the topical focus of each page and enable similarity analysis, coherence measurement, and semantic clustering. Embeddings are stored as pgvector columns with HNSW cosine indexes for efficient similarity search."),
            "citation-detection": ("How Citation Detection Works", "The citation detection pipeline runs configured queries against AI platforms, parses the generated responses for URLs and brand mentions, matches detected URLs against your page inventory using URL normalization and fuzzy matching, and records each citation with full context — the generating query, platform, citation position, and surrounding text."),
            "scoring-algorithm": ("The Scoring Algorithm", "Content structure scores are computed from a combination of graph metrics that our research has shown to predict LLM citation rates. Key metrics include hub dominance (authority concentration), link density (saturation level), boundary connectivity (cross-cluster links), embedding variance (topical coherence), and depth variation (hierarchical structure)."),
            "content-classification": ("Content Classification", "Each page is classified by content type — blog post, product page, documentation, case study, landing page — using a combination of URL patterns, structural signals, and content analysis. Classification influences how structural recommendations are generated, since optimal structure differs by content type."),
            "topic-clustering": ("Topic Clustering", "The platform groups pages into topical clusters using internal link graph analysis and embedding similarity. Clusters represent content sections that function as units for structural analysis. The clustering approach uses community detection on the link graph, validated by embedding coherence."),
            "graph-analysis": ("Graph Analysis Engine", "The graph analysis engine computes structural metrics on the internal link graph at the page, cluster, and site level. Metrics include degree distributions, centrality measures, clustering coefficients, community structure, and topology classification. Results are cached and incrementally updated as new crawl data arrives."),
            "authority-signals": ("Authority Signal Model", "Authority signals combine internal structural indicators (hub dominance, PageRank concentration) with external signals (backlink quality, entity recognition) to estimate each page's likelihood of being cited by AI systems. The model is calibrated against observed citation data."),
            "freshness-scoring": ("Content Freshness Scoring", "Freshness scores reflect how recently content was published or updated, weighted by content type. News and blog content decays faster than documentation and evergreen guides. Freshness affects crawl priority, recommendation urgency, and score weighting."),
        },
    },
    "admin": {
        "desc": "Administration and workspace management for the Acme platform. These guides cover user management, billing, security configuration, and operational settings.",
        "pages": {
            "team-management": ("Team Management", "Invite team members, assign roles (admin, editor, viewer), and manage permissions. Roles control access to features — admins can configure integrations and billing, editors can manage brands and trigger analyses, viewers can access dashboards and reports. Teams support up to 50 members on standard plans."),
            "billing": ("Billing and Subscription Management", "Manage your subscription, payment methods, and invoicing. View usage against plan limits — tracked brands, monitored queries, API calls, and crawl pages. Upgrade or downgrade plans from the billing dashboard. Enterprise plans include custom invoicing and volume pricing."),
            "sso-setup": ("SSO Configuration", "Configure Single Sign-On for your organization. Acme supports SAML 2.0 and OpenID Connect. Provide your identity provider's metadata URL, configure attribute mapping for user name and email, and optionally enable automatic team assignment based on IdP groups."),
            "audit-logs": ("Audit Logs", "Review all administrative actions taken in your workspace. Audit logs record user logins, configuration changes, data exports, and API key operations. Logs are retained for 90 days on standard plans and 1 year on enterprise plans. Export logs to your SIEM for compliance."),
            "permissions": ("Permissions Model", "Acme uses role-based access control with three built-in roles and support for custom roles on enterprise plans. Permissions control feature access (dashboards, reports, settings), data access (which brands a user can see), and action access (trigger crawls, modify configuration, export data)."),
            "data-retention": ("Data Retention Policies", "Configure how long different data types are retained. Crawl data defaults to 12 months, citation data to 24 months, and analysis results to indefinite retention. Adjust retention periods based on your compliance requirements and storage needs."),
            "api-keys": ("API Key Management", "Create, rotate, and revoke API keys for programmatic access. Each key has configurable scopes that restrict which endpoints it can access. Key rotation supports overlap periods for zero-downtime migration. Monitor key usage from the admin dashboard."),
            "workspace-settings": ("Workspace Settings", "Global workspace settings including timezone, default date ranges, notification preferences, and branding configuration. Workspace settings apply to all team members and affect report generation, scheduled operations, and notification timing."),
        },
    },
    "tutorials": {
        "desc": "Hands-on tutorials that walk through specific tasks from beginning to end. Each tutorial includes all steps, expected outcomes, and troubleshooting tips.",
        "pages": {
            "build-first-dashboard": ("Tutorial: Build Your First Dashboard", "Step-by-step guide to creating a custom dashboard with citation trends, competitive positioning, and structural health widgets. Start with a blank dashboard, add widgets one at a time, configure data sources and date ranges, and share with your team."),
            "automate-reports": ("Tutorial: Automate Weekly Reports", "Configure automated report generation and delivery. Select report template, set date range and comparison period, choose recipients and delivery channel (email or Slack), and schedule weekly delivery. Reports are generated with the latest data each delivery cycle."),
            "set-up-alerts": ("Tutorial: Configure Citation Alerts", "Set up real-time alerts for citation events. Define alert conditions (new citation for specific page, competitor cited for your topic, citation lost), configure notification channels, and set severity levels. Test alerts with a simulation before going live."),
            "track-competitors": ("Tutorial: Set Up Competitor Tracking", "Add competitor brands, configure comparative monitoring, and build competitive dashboards. Start by identifying your top 5 competitors, add their domains, trigger comparative crawls, and set up weekly competitive intelligence reports."),
            "optimize-content": ("Tutorial: Run Your First Content Optimization", "Walk through a complete content optimization cycle: run structural analysis, review cluster scores, accept link recommendations, apply changes, and measure the impact. This tutorial uses a real example to demonstrate the end-to-end workflow."),
            "measure-roi": ("Tutorial: Measure AI Visibility ROI", "Connect your analytics and CRM data to measure the business impact of AI citations. Configure revenue attribution, set up conversion tracking for citation-driven traffic, and build an ROI dashboard that shows the return on your content structure investment."),
            "import-data": ("Tutorial: Import Historical Data", "Import existing content inventories, historical citation data, or competitive intelligence from CSV files. Map your data fields to Acme's schema, validate the import, and trigger analysis on the imported data."),
            "connect-cms": ("Tutorial: Connect Your CMS", "Integrate your content management system with Acme for automatic content synchronization. Supported CMS platforms include WordPress, Contentful, Sanity, and Strapi. This tutorial covers API configuration, webhook setup, and sync verification."),
            "share-reports": ("Tutorial: Share Reports with Stakeholders", "Configure report sharing for different audiences. Create role-specific report views — executive summaries for leadership, detailed analyses for content teams, competitive briefs for strategy. Set up automated delivery and manage access permissions."),
        },
    },
    "troubleshooting": {
        "desc": "Solutions for common issues encountered when using the Acme platform. Each article covers symptoms, diagnosis, root cause, and resolution steps.",
        "pages": {
            "common-errors": ("Common Errors and Solutions", "A reference of the most frequently encountered errors with their solutions. Covers authentication failures, API errors, crawl failures, and data processing issues. Each error includes the error code, likely cause, and step-by-step resolution."),
            "connectivity-issues": ("Connectivity and Network Issues", "Troubleshoot network connectivity problems between the Acme platform and external services — your website (for crawling), AI platforms (for citation monitoring), and integrations (CMS, analytics, CRM). Covers firewall rules, proxy configuration, and SSL certificate issues."),
            "data-sync-delays": ("Data Synchronization Delays", "Diagnose and resolve delays in data appearing in your dashboards. Covers crawl queue backlogs, citation processing delays, embedding generation queues, and integration sync lag. Each scenario includes diagnosis steps and remediation options."),
            "missing-citations": ("Missing or Incorrect Citations", "Investigate cases where expected citations aren't being detected or citations are incorrectly attributed. Covers URL normalization issues, redirect handling, canonical URL mismatches, and citation matching threshold configuration."),
            "crawl-failures": ("Crawl Failures and Incomplete Crawls", "Diagnose crawl failures including timeout errors, blocked requests (robots.txt, rate limiting), rendering failures on JavaScript-heavy pages, and incomplete content extraction. Each failure type includes diagnosis steps and configuration adjustments."),
            "permission-errors": ("Permission and Access Errors", "Resolve permission errors including 403 responses to API calls, feature access denials in the web interface, and integration authentication failures. Covers role verification, API key scope checking, and SSO configuration issues."),
            "webhook-debugging": ("Webhook Delivery Issues", "Debug webhook delivery failures including timeout errors, signature verification failures, and payload parsing issues. Covers endpoint requirements, retry behavior, and testing tools for webhook integration."),
            "api-timeouts": ("API Timeout and Performance Issues", "Resolve API performance issues including slow responses, timeout errors, and rate limit exhaustion. Covers query optimization, pagination best practices, caching strategies, and when to use the batch API for large operations."),
        },
    },
}

all_docs = []
section_indices = []

for section, section_data in section_defs.items():
    section_url = f"https://acme.com/docs/{section}"
    section_indices.append(section_url)
    sub_urls = [f"https://acme.com/docs/{section}/{sub}" for sub in section_data["pages"]]
    all_docs.extend(sub_urls)

    section_title = section.replace("-", " ").title()
    add_page(section_url, f"# {section_title}\n\n{section_data['desc']}", sub_urls + [docs_index])
    all_docs.append(section_url)

    for sub_slug, (sub_title, sub_body) in section_data["pages"].items():
        sub_url = f"https://acme.com/docs/{section}/{sub_slug}"
        links = [section_url]
        if random.random() < 0.20:
            links += pick([s for s in sub_urls if s != sub_url], 1)
        add_page(sub_url, f"# {sub_title}\n\n{sub_body}", links)

add_page(docs_index, "# Documentation\n\nComplete reference for the Acme platform. Browse by section or search for specific topics. Each section builds on the previous — start with Getting Started if you're new to the platform.", section_indices)


# =============================================================================
# CASE STUDIES — MIXED (~50 pages)
# Organic structure: some hubs, some chains, some clusters within.
# The most common real-world pattern and the most citable (62.3%).
# =============================================================================

cs_index = "https://acme.com/case-studies"

industry_details = {
    "saas": {
        "desc": "How SaaS companies use content structure optimization to increase their visibility in AI-generated software recommendations and comparisons.",
        "studies": [
            ("How CloudMetrics Increased AI Citations by 340% Through Hub-Spoke Restructuring", "CloudMetrics was struggling with low AI visibility despite having extensive product documentation. Their content was organized as a flat list of feature pages with uniform cross-linking — a classic mesh anti-pattern. We restructured their documentation into hub-spoke clusters around core product areas, each with a comprehensive pillar page linking to detailed feature pages. Within 90 days, their citation rate increased 340% and their content appeared in AI responses for competitive comparison queries for the first time."),
            ("DataSync's Journey from Zero to Category Leader in AI Search", "DataSync had no presence in AI search when they started. Their site had 200+ pages but minimal internal linking — most pages only linked to the homepage. We built a complete content architecture with topic clusters for each product category, cross-section links between related clusters, and hub pages that established authority for each core topic. Over six months, they went from zero AI citations to being the most-cited brand in their category."),
            ("How TaskFlow Restructured Their Blog for 5x More AI Citations", "TaskFlow's blog had 150+ posts published over three years with no internal linking strategy. Posts were isolated pages that linked only to the homepage. We reorganized the blog into topic clusters with pillar pages, added contextual internal links between related posts, and created navigation that reinforced the hub-spoke structure. Blog citations increased 5x within four months."),
            ("PipelineHQ's Content Consolidation: Fewer Pages, More Citations", "PipelineHQ had 400+ pages with severe keyword cannibalization — multiple pages targeting the same topics, diluting authority across duplicates. We pruned 40% of their pages, consolidated duplicates into comprehensive hub pages, and rebuilt internal linking around the remaining content. Despite having fewer pages, their per-page citation rate increased 8x."),
            ("How NexusCRM Used Cross-Section Linking to Dominate AI Comparisons", "NexusCRM's product content was siloed — their CRM features section, integrations section, and pricing section had zero links between them. We added strategic cross-section links connecting related content across clusters, creating pathways that helped crawlers understand the full breadth of their offering. Their pages began appearing in AI comparison queries that previously only cited competitors."),
            ("ScaleDB's Technical Documentation: From Ignored to Authoritative", "ScaleDB had excellent technical documentation that was being ignored by AI systems because it lacked structural signals. The docs were a flat wiki with no hierarchy or internal linking. We restructured them as a tree with clear section hubs, progressive depth, and cross-references between related concepts. Documentation citations increased 12x."),
        ],
    },
    "ecommerce": {
        "desc": "How ecommerce brands optimize their product content structure to earn AI citations in shopping recommendations and product comparisons.",
        "studies": [
            ("How LuxeHome Turned Product Categories into Citation Magnets", "LuxeHome's product categories were classic mesh topology — every product linked to every other through category navigation, creating the high-density pattern that suppresses citations. We restructured categories as hub-spoke clusters with editorial category pages as hubs, reduced navigation link density, and added buying guide content that served as authoritative reference material. Category page citations increased from zero to 200+ per month."),
            ("Outdoor Gear Co's Content Architecture Overhaul", "Outdoor Gear Co had 3,000+ product pages with thin, templated content. We identified their top 20 product categories and built dedicated content clusters for each — category hub pages with buying guides, comparison tables, and expert recommendations linked to detailed product pages. The enriched categories earned 15x more AI citations than the original templated structure."),
            ("How PetSupply Built AI Visibility Through Expert Content Clusters", "PetSupply's content was product-focused with no informational content. We built expert content clusters around pet care topics — nutrition, health, training — with each cluster centered on a comprehensive guide that linked to relevant products. This informational content became their primary source of AI citations, with product pages benefiting from the authority flowing through the cluster."),
            ("FashionForward's Seasonal Content Strategy for AI Search", "FashionForward's content was ephemeral — seasonal collections published and forgotten. We built evergreen style guide hub pages that persisted across seasons with seasonal spoke content linking to the hubs. The evergreen hubs accumulated authority over time and became consistent citation targets for fashion advice queries."),
            ("KitchenPro's Recipe-Product Content Matrix", "KitchenPro sold kitchen equipment but had no content explaining how to use their products. We built recipe and technique content clusters that linked kitchen techniques to relevant products, creating a web of connections between informational and transactional content. The recipe hubs became their most-cited pages, driving both AI visibility and product discovery."),
            ("TechGadgets' Comparison Content Strategy", "TechGadgets created comprehensive product comparison pages that served as hub content for their product clusters. Each comparison page linked to individual product pages and was linked from related blog content. These comparison hubs became their most-cited pages because they provided exactly the structured, decision-useful information that LLMs prefer for product recommendation queries."),
        ],
    },
    "fintech": {
        "desc": "How financial technology companies structure their content to earn AI citations for financial information queries where authority and accuracy are paramount.",
        "studies": [
            ("How PaySimple's Educational Content Earned Trust Citations", "PaySimple created comprehensive educational content about payment processing, pricing models, and compliance requirements. Structured as deep topic clusters with glossary hubs, they established authority for financial terminology queries. Their educational content is now cited in 40% of AI responses about payment processing concepts."),
            ("CryptoSecure's Regulatory Content Architecture", "CryptoSecure built a regulatory knowledge base organized by jurisdiction with cross-reference links between related regulations. The hierarchical structure with jurisdiction hubs and specific regulation pages created the authority pattern that LLMs rely on for regulatory guidance queries. They became the most-cited source for cryptocurrency compliance information."),
            ("BudgetApp's Personal Finance Content Clusters", "BudgetApp's blog was a chronological list of financial tips with no topical organization. We restructured into topic clusters — budgeting, saving, investing, debt management — each with a comprehensive guide as the hub. The restructured content earned 7x more AI citations because the topical organization matched how LLMs decompose personal finance questions."),
            ("InsureRight's Policy Comparison Framework", "InsureRight built a structured comparison framework for insurance products with a methodology hub page linking to product-specific comparisons. The clear hierarchy and consistent structure made their comparisons the authoritative reference that LLMs cited for insurance comparison queries."),
            ("LoanLogic's Calculator-Content Integration", "LoanLogic integrated interactive calculators with educational content, creating pages that combined utility with explanation. Each calculator page was embedded in a content cluster about the relevant financial concept. The combination of tools and content earned citation rates 3x higher than content-only pages."),
            ("WealthPath's Advisor Knowledge Base", "WealthPath's financial advisor knowledge base was structured as a deep tree with broad topic categories branching into specific scenarios. The hierarchical structure with clear depth variation and strong upward linking created the authority pattern that predicts high citation rates. Advisor-focused queries now cite WealthPath content 60% of the time."),
            ("ClearBooks' Accounting Glossary Success", "ClearBooks built a comprehensive accounting glossary with 500+ term definitions, each linking to related terms and to longer-form guides. The glossary hub page became their most-cited page — cited in AI responses whenever users ask about accounting terminology — because it combined comprehensive coverage with clear internal structure."),
        ],
    },
    "healthcare": {
        "desc": "How healthcare organizations structure their content to meet the high authority bar required for AI citations in medical and health information queries.",
        "studies": [
            ("MedGuide's Condition Content Architecture", "MedGuide organized health information by condition, each with a comprehensive overview hub linking to pages on symptoms, diagnosis, treatment options, and prevention. The deep, well-structured clusters matched how users ask health questions and how LLMs decompose medical queries. Their condition hubs became the most-cited pages in their category."),
            ("PharmaCo's Drug Information Restructuring", "PharmaCo's drug information pages were isolated with no meaningful internal linking. We restructured them into therapeutic area clusters with drug class hubs linking to individual drug pages and cross-linking to related conditions. The structured hierarchy established the authority signal needed for medical content citations."),
            ("HealthFirst's Patient Education Content Clusters", "HealthFirst's patient education content was scattered across their site with no topical organization. We consolidated into condition-based clusters with clear hub-spoke structure, progressive reading paths from overview to detail, and cross-references between related conditions. Patient education citations increased 400%."),
            ("WellnessHub's Nutrition Content Strategy", "WellnessHub built comprehensive nutrition content organized by dietary approach, nutrient type, and health goal. Each cluster had a definitive guide as its hub with supporting pages providing specific advice. The topically coherent clusters earned significantly more citations than their competitors' scattered nutrition content."),
            ("CareConnect's Provider Directory Content Architecture", "CareConnect's provider directory was a flat list of profiles. We restructured into specialty hubs with geographic sub-sections, each hub containing educational content about the specialty alongside provider listings. The added informational depth transformed a utility directory into a citable reference resource."),
            ("MindWell's Mental Health Resource Hub", "MindWell created a mental health resource center structured as interconnected topic clusters — anxiety, depression, stress management, therapy types — with comprehensive hub pages and detailed supporting content. The cross-referencing between related conditions created the mixed topology that our research identifies as the most citable structure."),
        ],
    },
    "education": {
        "desc": "How educational institutions and edtech companies structure their content to earn AI citations for learning and educational guidance queries.",
        "studies": [
            ("LearnCode's Curriculum Content Architecture", "LearnCode organized their programming courses into a tree structure — language hubs linking to course modules linking to individual lessons. The clear hierarchy matched how LLMs decompose learning queries ('how to learn Python' → prerequisites → beginner concepts → intermediate topics). Their curriculum pages became the most-cited programming education resource."),
            ("UniGuide's Program Comparison Framework", "UniGuide built a structured university program comparison system with program category hubs linking to institution-specific pages and cross-referencing related programs. The comparison framework provided the structured, decision-useful information that LLMs prefer for educational guidance queries."),
            ("SkillBridge's Career Path Content Clusters", "SkillBridge organized career guidance content into industry-specific clusters with career path hub pages linking to skill requirements, job descriptions, and training resources. The deep topical clusters with clear progression paths earned citations for career guidance queries."),
            ("EduPlatform's Course Review Content Strategy", "EduPlatform structured course reviews around topic hubs with individual course pages linking to the hub and cross-referencing similar courses. The review content provided genuine comparative information that LLMs cited for 'best course for X' queries."),
            ("TutorMatch's Subject-Specific Content Architecture", "TutorMatch built subject-specific content hubs for math, science, and languages, each with concept explanations, practice problems, and tutor recommendations. The educational depth of each cluster — with content progressing from basic to advanced — created the authority hierarchy that drives citations."),
            ("ResearchGate's Paper Discovery Content Structure", "ResearchGate organized research papers into topic clusters with field-level hubs, sub-field sections, and individual paper pages. The hierarchical organization with clear topical grouping and cross-field references created a navigable structure that LLMs cited when summarizing research areas."),
        ],
    },
    "media": {
        "desc": "How media companies and publishers structure their content archives to maximize ongoing AI citations across news, analysis, and reference content.",
        "studies": [
            ("TechReview's Evergreen Content Hub Strategy", "TechReview had thousands of articles but no structural organization beyond chronological archives. We created topic hubs for their key coverage areas — AI, cybersecurity, cloud computing — each with an evergreen overview page that linked to the best recent and archival articles. The hub pages became their most-cited content, earning references in AI responses about technology trends."),
            ("NewsDaily's Topic Architecture Transformation", "NewsDaily restructured their news archive from chronological to topical, creating living topic pages that aggregated the latest reporting on ongoing stories. Each topic page served as a hub linking to individual articles, creating the authority concentration that drives AI citations for current events queries."),
            ("MediaCorp's Investigative Series Content Structure", "MediaCorp's investigative series were published as disconnected articles. We restructured them as series hubs with chronological and thematic navigation, cross-linking related investigations, and summary pages that provided comprehensive overviews. The structured series earned 5x more citations than individual articles."),
            ("PodcastNetwork's Show Notes Content Architecture", "PodcastNetwork transformed show notes from simple episode lists into structured content hubs. Each show had a topic-organized page linking to episode pages with full transcripts, guest information, and related resources. The enriched structure earned citations for queries about the topics discussed."),
            ("MagazineOnline's Archive Restructuring", "MagazineOnline's 20-year archive was a chronological dump of articles. We created topical indexes that curated the best archival content into organized collections with editorial introductions. These curated hubs became authoritative references that LLMs cited for historical context and background information."),
            ("DataJournal's Dataset Content Structure", "DataJournal structured their data journalism around methodology hubs linking to individual data stories, source data, and analytical tools. The transparent, well-organized structure established the credibility signal that LLMs require for citing data-driven claims."),
        ],
    },
    "manufacturing": {
        "desc": "How manufacturing companies structure technical content to earn AI citations for industrial knowledge, specifications, and process guidance queries.",
        "studies": [
            ("MetalWorks' Technical Specification Content Architecture", "MetalWorks organized their technical specifications into material-type clusters with comprehensive hub pages covering properties, applications, and processing guidelines. Individual alloy specification pages linked to the hub and cross-referenced related materials. The structured technical content became the authoritative reference for material selection queries."),
            ("AutoParts' Product Compatibility Content Structure", "AutoParts built compatibility content clusters organized by vehicle system — engine, transmission, braking, electrical — with system hubs linking to component pages and cross-referencing compatible parts. The structured compatibility information earned citations for automotive repair and parts selection queries."),
            ("ChemProcess' Safety Data Content Architecture", "ChemProcess structured their chemical safety data as a hierarchical system with chemical family hubs, individual chemical pages, and cross-referenced safety procedures. The deep, well-organized safety content became the cited reference for chemical handling queries."),
            ("PrecisionTools' Application Guide Content Strategy", "PrecisionTools organized their tooling content by application rather than product, creating process-focused hubs — milling, turning, drilling — with tool selection guides as hub content and individual tool pages as supporting content. The application-oriented structure matched how users search for tooling solutions."),
            ("IndustrialFlow's Process Documentation Content Clusters", "IndustrialFlow structured their process documentation as interconnected workflows with process hubs linking to step-by-step procedures, equipment specifications, and troubleshooting guides. The comprehensive process coverage with clear internal navigation earned citations for industrial process queries."),
            ("PackagingSolutions' Material Comparison Framework", "PackagingSolutions built a material comparison framework with packaging type hubs linking to material-specific pages, environmental impact data, and cost comparisons. The structured comparison content earned citations for packaging selection and sustainability queries."),
        ],
    },
}

cs_pages = []

for industry, ind_data in industry_details.items():
    industry_index = f"https://acme.com/case-studies/{industry}"
    studies = [f"https://acme.com/case-studies/{industry}/{industry}-study-{j}" for j in range(1, len(ind_data["studies"]) + 1)]
    cs_pages.append(industry_index)
    cs_pages.extend(studies)

    add_page(industry_index, f"# {industry.title()} Case Studies\n\n{ind_data['desc']}", studies + [cs_index])

    for k, (study_url, (study_title, study_body)) in enumerate(zip(studies, ind_data["studies"])):
        links = [industry_index]
        if random.random() < 0.40:
            other_industry = random.choice([i for i in industry_details if i != industry])
            links.append(f"https://acme.com/case-studies/{other_industry}")
        if random.random() < 0.25:
            links += pick([s for s in studies if s != study_url], random.randint(1, 2))
        if random.random() < 0.20:
            links += pick(blog_posts, 1)
        add_page(study_url, f"# {study_title}\n\n{study_body}", links)

add_page(cs_index, "# Case Studies\n\nReal results from real brands across every industry. See how companies like yours used content structure optimization to increase their AI visibility and earn more LLM citations.", [f"https://acme.com/case-studies/{ind}" for ind in industry_details])


# =============================================================================
# RESOURCES — CLIQUE (20 pages)
# Every page links to every other. High density, high reciprocity.
# Only 36.4% citation rate in the research.
# =============================================================================

resource_content = {
    "ai-search-glossary": ("AI Search Glossary", "Comprehensive glossary of AI search terms — from citation tracking and embedding similarity to hub dominance and retrieval-augmented generation. Each term includes a definition, context, and cross-references to related terms throughout this resource library."),
    "seo-glossary": ("SEO Glossary", "Complete glossary of search engine optimization terms covering traditional SEO concepts alongside emerging AI optimization terminology. Cross-referenced with the AI Search Glossary for terms that span both disciplines."),
    "citation-metrics-guide": ("Citation Metrics Guide", "Detailed explanation of every citation metric tracked by the platform — citation count, citation rate, share of voice, citation context, and citation quality. Includes formulas, interpretation guidelines, and benchmarks from the industry survey."),
    "benchmark-report-2025": ("Benchmark Report 2025", "Annual benchmark data for AI visibility metrics across industries. Includes median citation rates by industry, structural health scores by site size, and competitive density metrics for major categories. Use alongside the ROI calculator to set realistic goals."),
    "industry-survey": ("Industry Survey: AI Visibility Landscape", "Survey of 500+ marketing leaders on their AI search optimization priorities, budgets, and challenges. Key findings inform the benchmark report and provide context for the buyer guide. Conducted in partnership with industry analysts."),
    "roi-calculator": ("AI Visibility ROI Calculator", "Interactive calculator for estimating the business impact of AI visibility improvements. Input your traffic, conversion rate, and average deal size to project the revenue impact of increasing your citation rate. Methodology detailed in the citation metrics guide."),
    "comparison-chart": ("Platform Comparison Chart", "Side-by-side feature comparison of AI search optimization platforms. Covers monitoring capabilities, optimization tools, reporting features, integrations, and pricing. Complements the buyer guide with detailed feature-level comparisons."),
    "buyer-guide": ("Buyer's Guide: Choosing an AI Search Platform", "Evaluation framework for selecting an AI search optimization platform. Covers requirements gathering, vendor evaluation criteria, implementation considerations, and total cost of ownership. References the comparison chart and feature comparison for specifics."),
    "implementation-checklist": ("Implementation Checklist", "Step-by-step checklist for implementing an AI search optimization program. Covers initial setup, content audit, structural analysis, optimization execution, and measurement. Timeline estimates based on the benchmark report data."),
    "migration-guide": ("Migration Guide: Switching Platforms", "Guide for migrating from another AI search platform to Acme. Covers data export, configuration mapping, historical data import, and parallel-run validation. Uses the integration matrix to verify compatibility."),
    "integration-matrix": ("Integration Compatibility Matrix", "Complete matrix of supported integrations with version compatibility, feature support levels, and known limitations. Cross-references the implementation checklist for integration setup steps."),
    "feature-comparison": ("Feature Comparison: Acme vs Competitors", "Detailed feature-by-feature comparison between Acme and competing platforms. Each feature is rated on capability level, ease of use, and maturity. Complements the comparison chart with deeper analysis."),
    "pricing-guide": ("Pricing Guide: Understanding Plan Options", "Detailed breakdown of pricing plans, included features, usage limits, and add-on options. Includes cost modeling examples for different team sizes and use cases. References the ROI calculator for value estimation."),
    "vendor-evaluation": ("Vendor Evaluation Template", "Downloadable evaluation scorecard for assessing AI search optimization vendors. Criteria are weighted based on the industry survey findings about what matters most to marketing teams."),
    "security-whitepaper": ("Security and Compliance Whitepaper", "Comprehensive overview of Acme's security architecture, data handling practices, and compliance certifications. Covers SOC 2 Type II, GDPR, CCPA, and industry-specific requirements. Referenced by the compliance overview for regulatory details."),
    "compliance-overview": ("Compliance Overview", "Summary of regulatory compliance relevant to AI search optimization tools. Covers data privacy regulations, AI transparency requirements, and industry-specific mandates. Cross-references the security whitepaper for Acme's specific compliance measures."),
    "data-sheet": ("Product Data Sheet", "Technical specifications for the Acme platform including infrastructure requirements, performance benchmarks, data capacity limits, and SLA guarantees. Complements the architecture diagram with quantitative specifications."),
    "architecture-diagram": ("Platform Architecture Diagram", "Visual overview of the Acme platform architecture showing component relationships, data flow, and integration points. Accompanies the data sheet and API overview with architectural context."),
    "api-overview": ("API Overview for Evaluators", "Non-technical overview of Acme's API capabilities for evaluators and decision-makers. Covers what the API enables, integration patterns, and example use cases. For technical details, reference the full API documentation."),
    "platform-roadmap": ("Platform Roadmap: What's Coming", "Public roadmap of upcoming features and capabilities. Organized by quarter with committed, planned, and exploratory items. Updated monthly based on customer feedback and market developments."),
}

resource_urls = [f"https://acme.com/resources/{slug}" for slug in resource_content]

for slug, (title, body) in resource_content.items():
    url = f"https://acme.com/resources/{slug}"
    links = [r for r in resource_urls if r != url]
    add_page(url, f"# {title}\n\n{body}", links)


# =============================================================================
# PRICING — CHAIN (12 pages)
# Sequential flow: overview → tiers → comparison → purchase.
# Low density, no hub, linear structure.
# =============================================================================

pricing_pages = [
    ("https://acme.com/pricing", "Pricing", "Transparent pricing for AI search optimization. Choose the plan that fits your team's needs — from startup to enterprise. All plans include core monitoring, structural analysis, and citation tracking with usage-based limits."),
    ("https://acme.com/pricing/plans-overview", "Plans Overview", "Three plans designed for different stages of AI search maturity. Starter for teams beginning their AI visibility journey, Professional for growing programs with multiple brands, and Enterprise for organizations requiring advanced features, custom integrations, and dedicated support."),
    ("https://acme.com/pricing/starter", "Starter Plan", "The Starter plan includes monitoring for 1 brand, 50 tracked queries, weekly citation reports, and basic structural analysis. Ideal for teams exploring AI search optimization for the first time. Crawl limit: 500 pages per brand. API access included with standard rate limits."),
    ("https://acme.com/pricing/professional", "Professional Plan", "The Professional plan supports 5 brands, 500 tracked queries, daily citation monitoring, full structural analysis with optimization recommendations, and competitor tracking for up to 3 competitors per brand. Crawl limit: 5,000 pages per brand. Priority API access with elevated rate limits."),
    ("https://acme.com/pricing/enterprise", "Enterprise Plan", "Enterprise plans are customized to your organization's needs. Unlimited brands and queries, real-time citation monitoring, advanced optimization with direct structural editing, unlimited competitor tracking, SSO, custom integrations, dedicated support, and SLA guarantees. Contact sales for pricing."),
    ("https://acme.com/pricing/compare-plans", "Compare Plans", "Side-by-side comparison of Starter, Professional, and Enterprise plans across all features. Compare monitoring capabilities, analysis depth, optimization tools, reporting, integrations, and support levels to choose the right fit for your team."),
    ("https://acme.com/pricing/add-ons", "Add-Ons", "Extend your plan with add-on capabilities. Available add-ons include additional brands, extra tracked queries, premium competitor intelligence, white-label reporting, API rate limit increases, and dedicated crawl infrastructure. Add-ons can be added to any plan."),
    ("https://acme.com/pricing/api-pricing", "API Pricing", "API access is included in all plans with plan-specific rate limits. Additional API capacity is available as an add-on. Enterprise plans include custom rate limits and dedicated API infrastructure. Volume pricing available for high-throughput integrations."),
    ("https://acme.com/pricing/volume-discounts", "Volume Discounts", "Volume discounts are available for organizations managing 10+ brands or requiring high API throughput. Discount tiers are based on total usage across all features — brands, queries, pages, and API calls. Contact sales for a custom volume proposal."),
    ("https://acme.com/pricing/custom-quote", "Request a Custom Quote", "For organizations with specific requirements, we provide custom pricing proposals. Tell us about your brand portfolio, monitoring needs, integration requirements, and team size, and we'll build a proposal tailored to your situation."),
    ("https://acme.com/pricing/faq", "Pricing FAQ", "Answers to common pricing questions. How does billing work? What happens if I exceed my plan limits? Can I switch plans mid-cycle? Is there a free trial? What's included in the setup fee? Can I cancel anytime?"),
    ("https://acme.com/pricing/contact-sales", "Contact Sales", "Connect with our sales team to discuss your AI search optimization needs. We'll help you choose the right plan, estimate your ROI, and plan your implementation. Available for live demos, custom proposals, and enterprise negotiations."),
]

pricing_chain = [url for url, _, _ in pricing_pages]

for i, (url, title, body) in enumerate(pricing_pages):
    links = []
    if i > 0:
        links.append(pricing_chain[i - 1])
    if i < len(pricing_chain) - 1:
        links.append(pricing_chain[i + 1])
    add_page(url, f"# {title}\n\n{body}", links)


# =============================================================================
# SOLUTIONS — WELL-STRUCTURED HUB (~59 pages)
# Clear pillar pages with supporting content. High hub_dominance,
# moderate density, good depth variation. The "ideal" pattern.
# =============================================================================

solutions_index = "https://acme.com/solutions"

solution_pillars = {
    "ai-visibility": {
        "desc": "Comprehensive AI visibility monitoring and analysis. Track how your brand appears across every major LLM platform, measure your share of voice against competitors, and understand the citation patterns that drive AI-mediated brand discovery.",
        "pages": {
            "brand-mention-tracking": ("Brand Mention Tracking", "Monitor every mention of your brand across AI-generated responses. Track both cited mentions (with URL) and uncited mentions (name only), distinguishing between direct references and contextual mentions. Brand mention data feeds into share-of-voice calculations and competitive positioning analysis."),
            "citation-monitoring": ("Citation Monitoring", "Real-time monitoring of pages cited in AI responses across all tracked platforms. Each citation is recorded with full context — the generating query, AI platform, response text, citation position, and whether your brand was mentioned in the original query."),
            "sentiment-analysis": ("Sentiment Analysis", "Analyze the sentiment of AI responses that reference your brand. Track whether your brand is described positively, neutrally, or negatively across different topics and platforms. Sentiment trends reveal how AI systems are characterizing your brand over time."),
            "competitor-benchmarking": ("Competitor Benchmarking", "Compare your AI visibility metrics against tracked competitors across shared topics. Benchmark citation rates, share of voice, sentiment, and structural health to identify competitive advantages and gaps."),
            "share-of-voice": ("Share of Voice", "Calculate your brand's share of AI citations relative to competitors for each tracked topic. Share of voice is computed as your citation count divided by total citations across all tracked brands for a query set. Track share of voice trends over time."),
            "trend-detection": ("Trend Detection", "Automated detection of emerging trends in your AI visibility data. Identifies acceleration or deceleration in citation rates, emerging query patterns, competitive displacement events, and seasonal citation variations."),
            "alert-configuration": ("Alert Configuration", "Configure alerts for critical AI visibility events — citation rate drops, competitor gains, new brand mentions, and anomalous patterns. Route alerts to email, Slack, or webhooks with configurable severity thresholds."),
            "executive-dashboard": ("Executive Dashboard", "High-level AI visibility dashboard designed for leadership. Shows key metrics — total citations, share of voice, competitive position, and trend direction — in a format that communicates status and priority without technical detail."),
            "weekly-reports": ("Weekly Reports", "Automated weekly AI visibility reports delivered to stakeholders. Each report includes citation summary, competitive changes, notable events, and recommended actions based on the week's data."),
        },
    },
    "content-optimization": {
        "desc": "Tools and workflows for optimizing your content structure to maximize LLM citation rates. Analyze your site's structural health, receive specific recommendations, and measure the impact of structural improvements.",
        "pages": {
            "content-scoring": ("Content Scoring", "Score each content cluster's structural health against the metrics that predict LLM citation rates. Scores incorporate hub dominance, link density, cross-section connectivity, topical coherence, and depth variation. Track scores over time to measure the impact of structural improvements."),
            "gap-analysis": ("Content Gap Analysis", "Identify topical gaps in your content coverage by analyzing competitor content structures and citation patterns. Discover topics where competitors are cited but you have no content, and prioritize gap creation based on citation volume and competitive density."),
            "keyword-opportunities": ("Keyword Opportunities", "Discover query opportunities where your content structure is strong enough to compete for citations. Combines citation gap data with structural health scores to identify queries where creating or improving content would have the highest citation impact."),
            "content-calendar": ("Content Calendar", "Plan content creation and updates with a calendar that incorporates AI visibility priorities. Scheduling considers content freshness requirements, competitive gap urgency, and structural improvement timelines."),
            "brief-generation": ("Content Brief Generation", "Generate detailed content briefs for new pages based on competitive citation analysis, structural requirements, and topical gap data. Each brief specifies the target topic, required depth, internal linking instructions, and structural role within the cluster."),
            "performance-tracking": ("Performance Tracking", "Track the citation performance of individual pages and clusters over time. Correlate performance changes with structural modifications, content updates, and competitive actions to understand what drives citation improvements."),
            "ab-testing-content": ("Content A/B Testing", "Test structural changes in controlled experiments. Apply link modifications or content restructuring to test clusters while keeping control clusters unchanged. Measure the citation impact of structural changes with statistical confidence."),
            "content-refresh": ("Content Refresh Scheduler", "Schedule content updates based on freshness signals, citation decay, and competitive changes. Prioritize refreshes for hub pages and high-value cluster content that would benefit most from updated information and strengthened internal links."),
            "pruning-recommendations": ("Pruning Recommendations", "Identify pages that weaken cluster quality through thin content, outdated information, or topic drift. Recommend removal or consolidation that would improve the cluster's structural metrics while preserving link equity through redirects."),
            "topic-clustering": ("Topic Clustering Analysis", "Analyze how your content naturally clusters by topic using internal link graph analysis and embedding similarity. Compare detected clusters against your intended content architecture to identify structural misalignments."),
            "semantic-analysis": ("Semantic Coherence Analysis", "Measure the semantic coherence of your content clusters using page embedding analysis. Compute embedding variance within each cluster and compare against the coherence levels that predict high citation rates. Identify pages that reduce cluster coherence."),
        },
    },
    "technical-seo": {
        "desc": "Technical SEO tools adapted for the AI search era. Audit your site's crawlability, indexation, and structural health from the perspective of AI crawlers and LLM retrieval systems.",
        "pages": {
            "site-audit": ("Site Audit", "Comprehensive technical audit covering crawlability, indexation, internal link structure, and AI-specific optimization factors. The audit identifies issues that prevent AI crawlers from discovering and correctly evaluating your content."),
            "crawl-analysis": ("Crawl Analysis", "Deep analysis of how AI crawlers interact with your site. Reviews crawl coverage, crawl frequency, content extraction completeness, and internal link discovery rates. Identifies pages that are under-crawled or incompletely extracted."),
            "indexation-monitoring": ("Indexation Monitoring", "Monitor which of your pages are present in AI platform retrieval indices. Pages missing from the index can't be cited regardless of content quality. Track indexation rates over time and diagnose indexation issues."),
            "core-web-vitals": ("Core Web Vitals Monitoring", "Track Core Web Vitals performance for your pages with emphasis on metrics that affect AI crawling. Pages with poor performance may experience timeout failures during AI crawl cycles, resulting in incomplete content extraction."),
            "schema-validation": ("Schema Validation", "Validate structured data markup across your site. Check for schema correctness, completeness, and consistency. Identify pages missing schema that would benefit from structured data for AI content understanding."),
            "redirect-management": ("Redirect Management", "Manage URL redirects to preserve link equity during content restructuring. Identify redirect chains, loops, and broken redirects. Plan redirect strategies that maintain your content cluster structures through URL changes."),
            "log-file-analysis": ("Log File Analysis", "Analyze server access logs to understand AI crawler behavior — which pages they request, crawl frequency, rendering patterns, and content extraction. Log analysis reveals how AI crawlers actually interact with your site versus how you expect them to."),
            "javascript-rendering": ("JavaScript Rendering Audit", "Audit your site's JavaScript rendering to ensure AI crawlers can access your content. Test pages with JavaScript disabled, check server-side rendering completeness, and identify content or links hidden behind client-side rendering."),
            "mobile-optimization": ("Mobile Optimization", "Evaluate your mobile experience for AI crawl compatibility. With mobile-first indexing, AI crawlers primarily use the mobile version of your pages. Ensure mobile pages include the same content, links, and structured data as desktop."),
            "international-seo": ("International SEO", "Manage multi-language and multi-region content for AI visibility. Configure hreflang tags, language-specific content clusters, and geographic targeting to ensure AI systems cite the correct language version for each user's query."),
            "hreflang-validation": ("Hreflang Validation", "Validate hreflang implementation across your international content. Check for return tag consistency, language code accuracy, and canonical URL alignment. Incorrect hreflang can cause AI systems to cite the wrong language version."),
        },
    },
    "competitive-intelligence": {
        "desc": "Competitive intelligence for the AI search landscape. Understand how competitors structure their content, where they earn citations, and where you can gain structural advantages.",
        "pages": {
            "competitor-tracking": ("Competitor Tracking", "Monitor competitors' AI visibility across your shared topics. Track their citation rates, content changes, and structural modifications. Set up alerts for competitive changes that could affect your positioning."),
            "market-landscape": ("Market Landscape Analysis", "Map the competitive landscape for AI visibility in your industry. Identify which brands dominate which topics, where the competitive density is highest, and where underserved opportunities exist for your content."),
            "feature-comparison": ("Feature Comparison", "Compare the content features and structural approaches of competing brands. Analyze their content types, linking patterns, hub-spoke structures, and topical organization to identify structural advantages you can replicate or improve upon."),
            "positioning-analysis": ("Positioning Analysis", "Analyze how AI systems position your brand relative to competitors. Review the context in which your brand and competitors are cited — as leaders, alternatives, specialists, or budget options — to understand your AI brand positioning."),
            "pricing-intelligence": ("Pricing Intelligence", "Monitor competitor pricing pages for changes in pricing structure, plan features, and positioning. Track how pricing content structure affects citation rates for comparison and evaluation queries."),
            "content-gap-finder": ("Content Gap Finder", "Identify topics where competitors earn AI citations but you don't. Prioritize gaps by citation volume, competitive intensity, and strategic importance to build a targeted content roadmap."),
            "backlink-analysis": ("Backlink Analysis", "Analyze the external backlink profiles of competing sites to understand their authority signals. Compare domain authority, linking domain diversity, and editorial link quality to identify authority advantages and opportunities."),
            "traffic-estimation": ("Traffic Estimation", "Estimate competitor traffic from AI sources based on their citation rates and click-through modeling. Understand the business scale of competitors' AI visibility to inform your investment decisions."),
            "win-loss-analysis": ("Win-Loss Analysis", "Analyze queries where you and competitors are both considered for citation. Understand which structural and content factors determine whether your page or a competitor's page gets cited in head-to-head situations."),
            "market-share-tracking": ("Market Share Tracking", "Track your share of AI visibility across your total addressable market. Measure progress toward category leadership by tracking citation share across all relevant topics over time."),
            "brand-perception": ("Brand Perception Analysis", "Analyze how AI systems describe your brand across different contexts. Track the adjectives, comparisons, and categorizations used when AI systems reference your brand to understand and influence your AI brand perception."),
        },
    },
    "reporting": {
        "desc": "Reporting and analytics tools for communicating AI visibility performance to every stakeholder — from content teams to executive leadership.",
        "pages": {
            "custom-dashboards": ("Custom Dashboards", "Build tailored dashboards with drag-and-drop widgets for citation metrics, structural health scores, competitive data, and trend visualizations. Share dashboards with team members with role-appropriate data access."),
            "automated-reports": ("Automated Reports", "Schedule automated report generation and delivery on any cadence — daily, weekly, monthly, quarterly. Each report is generated with the latest data and delivered via email or Slack to configured recipients."),
            "stakeholder-views": ("Stakeholder-Specific Views", "Create role-specific views of your AI visibility data. Executive views show high-level KPIs and trends. Content team views show detailed page-level metrics and recommendations. Strategy views show competitive positioning and market landscape."),
            "data-export": ("Data Export", "Export your AI visibility data in CSV, JSON, or Parquet format for analysis in external tools. Schedule automated exports to cloud storage or data warehouses. The export API supports incremental exports for efficient data pipeline integration."),
            "api-access": ("Reporting API", "Programmatic access to all reporting data via REST API. Build custom integrations with your existing BI tools, embed Acme visualizations in internal dashboards, or feed AI visibility data into your data warehouse."),
            "white-label-reports": ("White-Label Reports", "Generate branded reports with your organization's logo, colors, and styling for client-facing delivery. White-label settings are configurable per workspace for agencies managing multiple client brands."),
            "roi-attribution": ("ROI Attribution", "Connect citation data with business outcomes to measure the return on your AI visibility investment. Configure revenue attribution models that trace the path from AI citation to website visit to conversion to revenue."),
            "kpi-tracking": ("KPI Tracking", "Define and track AI visibility KPIs — target citation rates, share-of-voice thresholds, structural health goals. Visual dashboards show progress toward goals with projected timelines and trend indicators."),
            "executive-summary": ("Executive Summary Reports", "Auto-generated executive summaries that distill complex AI visibility data into clear narratives with key metrics, notable changes, competitive context, and recommended actions for leadership."),
            "team-performance": ("Team Performance Reports", "Track AI visibility performance by content team, topic owner, or business unit. Identify which teams produce content that earns citations and where additional investment or structural improvement would have the highest impact."),
            "channel-breakdown": ("Channel Breakdown", "Break down AI visibility by platform channel — ChatGPT, Perplexity, Google AI Overviews, Claude, and others. Understand which platforms cite your content most and tailor your optimization strategy by channel."),
        },
    },
}

pillar_urls = []
all_solution_pages = []

for pillar, pillar_data in solution_pillars.items():
    pillar_url = f"https://acme.com/solutions/{pillar}"
    pillar_urls.append(pillar_url)
    sub_urls = [f"https://acme.com/solutions/{pillar}/{sub}" for sub in pillar_data["pages"]]
    all_solution_pages.extend(sub_urls)

    other_pillars = pick([f"https://acme.com/solutions/{p}" for p in solution_pillars if p != pillar], 2)
    add_page(pillar_url, f"# {pillar.replace('-', ' ').title()}\n\n{pillar_data['desc']}", sub_urls + other_pillars + [solutions_index])

    for sub_slug, (sub_title, sub_body) in pillar_data["pages"].items():
        sub_url = f"https://acme.com/solutions/{pillar}/{sub_slug}"
        links = [pillar_url]
        links += pick([s for s in sub_urls if s != sub_url], random.randint(1, 3))
        if random.random() < 0.30:
            other_pillar = random.choice([p for p in solution_pillars if p != pillar])
            other_subs = [f"https://acme.com/solutions/{other_pillar}/{s}" for s in solution_pillars[other_pillar]["pages"]]
            links += pick(other_subs, 1)
        add_page(sub_url, f"# {sub_title}\n\n{sub_body}", links)

add_page(solutions_index, "# Solutions\n\nEverything you need for AI search optimization — from visibility monitoring and competitive intelligence to content structure optimization and performance reporting. Each solution area is built on the research showing that site structure predicts AI citation rates.", pillar_urls)


# =============================================================================
# ABOUT — SPARSE/FLAT (~40 pages)
# Minimal internal linking. Most pages only link to index.
# Low density, low hub_dominance.
# =============================================================================

about_index = "https://acme.com/about"

about_content = {
    "company": ("About Acme", "Acme was founded in 2023 to solve a new problem: helping brands get discovered by AI. As large language models increasingly mediate how people find information, products, and services, the brands that structure their content for AI discoverability gain an unfair advantage. We build the tools that make that possible."),
    "team": ("Our Team", "The Acme team combines expertise in search technology, machine learning, content strategy, and product design. We're a remote-first team of 45 people across 12 countries, united by the mission of helping brands navigate the shift from traditional search to AI-mediated discovery."),
    "leadership": ("Leadership", "Acme's leadership team brings experience from Google Search, Meta AI, HubSpot, and Moz. Our CTO previously led the search quality team at a major tech company, and our VP of Research has published over 20 papers on information retrieval and content recommendation."),
    "careers": ("Careers at Acme", "We're hiring across engineering, product, design, research, and go-to-market. Acme offers competitive compensation, full remote flexibility, generous equity, and the opportunity to shape a new category of software. See our open positions below."),
    "culture": ("Our Culture", "Acme's culture is built on intellectual curiosity, rigorous experimentation, and genuine care for our customers' success. We publish our research openly, contribute to open-source projects, and believe that the best products come from teams that question assumptions and measure outcomes."),
    "values": ("Our Values", "Our core values guide every decision: research-driven (we follow the data, not opinions), customer-centric (we succeed when our customers succeed), transparent (we share what we learn), and pragmatic (we ship solutions, not slideware)."),
    "mission": ("Our Mission", "Acme's mission is to give every brand a fair chance at AI visibility. The shift from traditional search to AI-mediated discovery shouldn't advantage incumbents or big budgets — it should reward genuine authority, clear structure, and useful content. We build the tools that make structural quality visible and improvable."),
    "history": ("Company History", "Acme started as a research project studying how LLMs select sources for citation. Our founding research analyzed millions of AI responses to identify the structural patterns that predict citation likelihood. We turned those findings into a product and launched commercially in 2024."),
    "press": ("Press Room", "Media coverage and press resources for Acme. Our research on AI citation patterns has been covered by major technology and marketing publications. Press inquiries can be directed to our communications team."),
    "newsroom": ("Newsroom", "The latest news from Acme — product launches, research publications, partnerships, and company milestones. Subscribe to our press list for embargoed announcements and briefing opportunities."),
    "awards": ("Awards and Recognition", "Acme has been recognized as a Category Leader in AI Search Optimization, named to the MarTech Top 100, and received the Innovation Award at SearchCon 2025 for our content structure research."),
    "partners": ("Partner Program", "Join the Acme partner ecosystem. We work with agencies, consultancies, technology providers, and system integrators who help brands optimize for AI visibility. Partners receive training, co-marketing support, and revenue sharing."),
    "investors": ("Investors", "Acme is backed by leading technology investors including Benchmark, Greylock, and Index Ventures. We raised our Series B in 2025 to expand our platform capabilities and accelerate market growth."),
    "board": ("Board of Directors", "Acme's board includes experienced operators and investors from the search, AI, and marketing technology sectors. Our board provides strategic guidance on product direction, market expansion, and company building."),
    "advisors": ("Advisory Board", "Our advisory board includes search industry veterans, AI researchers, and marketing leaders who provide domain expertise and customer perspective. Advisors contribute to our research program and product strategy."),
    "offices": ("Office Locations", "Acme is headquartered in San Francisco with offices in New York, London, and Singapore. As a remote-first company, most of our team works distributed, with offices serving as collaboration hubs for in-person work sessions."),
    "contact": ("Contact Us", "Reach our team for sales inquiries, support requests, press questions, or partnership discussions. Our sales team is available for demos and consultations. Support is available via email and chat during business hours."),
    "diversity": ("Diversity and Inclusion", "Acme is committed to building a diverse, inclusive team that reflects the global market we serve. We track representation metrics, invest in inclusive hiring practices, and foster an environment where every team member can contribute their full potential."),
    "sustainability": ("Sustainability", "Acme operates with environmental responsibility in mind. Our infrastructure runs on carbon-neutral cloud providers, we offset our team's travel emissions, and we prioritize efficient algorithms that minimize compute resources."),
    "community": ("Community", "The Acme community includes thousands of marketing professionals, SEO practitioners, and content strategists working on AI visibility. Join our Slack community, attend monthly meetups, and contribute to our open-source tools."),
    "events": ("Events", "Acme hosts and sponsors events focused on AI search optimization — from intimate workshops to large conference presentations. Check our events calendar for upcoming opportunities to learn and connect."),
    "webinars-page": ("Webinars", "Live and recorded webinars covering AI search optimization topics from fundamentals to advanced strategies. Each webinar includes Q&A, downloadable materials, and follow-up resources."),
    "brand-guidelines": ("Brand Guidelines", "Acme brand guidelines for partners, press, and team members. Covers logo usage, color palette, typography, tone of voice, and co-branding requirements. Download our brand kit for approved assets."),
    "media-kit": ("Media Kit", "Downloadable media kit with Acme logos, executive headshots, product screenshots, and boilerplate text for press use. All assets are provided in web and print resolutions."),
    "legal": ("Legal", "Legal information including our terms of service, privacy policy, data processing agreements, and acceptable use policy. Enterprise customers can request custom legal terms through their account manager."),
    "privacy": ("Privacy Policy", "Acme's privacy policy describes how we collect, use, and protect your data. We process only the data necessary to deliver our service, and we never sell customer data to third parties."),
    "terms": ("Terms of Service", "The terms governing your use of the Acme platform. Covers account responsibilities, acceptable use, service level commitments, data ownership, and dispute resolution."),
    "security": ("Security", "Overview of Acme's security practices including infrastructure security, data encryption, access controls, vulnerability management, and incident response. We maintain SOC 2 Type II certification and undergo annual penetration testing."),
    "status": ("System Status", "Real-time status of all Acme platform components. View current system health, active incidents, and historical uptime data. Subscribe to status notifications for proactive alerts about platform issues."),
    "accessibility": ("Accessibility", "Acme is committed to making our platform accessible to all users. We follow WCAG 2.1 AA guidelines and regularly audit our interfaces for accessibility compliance. Report accessibility issues to our team for priority resolution."),
    "customers": ("Our Customers", "Over 500 brands trust Acme for AI search optimization. Our customers span SaaS, ecommerce, healthcare, financial services, and media — from startups building their first AI presence to enterprises managing hundreds of brands."),
    "testimonials": ("Customer Testimonials", "Hear directly from Acme customers about their experience with the platform. Our customers share how content structure optimization transformed their AI visibility and drove measurable business results."),
    "case-studies-overview": ("Case Studies", "In-depth case studies documenting how brands across industries improved their AI visibility through content structure optimization. Each case study covers the challenge, approach, structural changes, and measured results."),
    "blog-overview": ("Blog", "Expert insights on AI search optimization from the Acme team and guest contributors. Covering strategy, technical implementation, industry trends, and original research."),
    "social-responsibility": ("Social Responsibility", "Acme's commitment to responsible AI practices includes publishing our research openly, advocating for fair AI content attribution, and contributing to standards for AI transparency in content citation."),
    "engineering-blog": ("Engineering Blog", "Technical articles from the Acme engineering team covering the systems, algorithms, and infrastructure behind the platform. Topics include graph analysis at scale, embedding systems, real-time citation detection, and infrastructure optimization."),
    "open-source": ("Open Source", "Acme contributes to and maintains open-source projects related to web crawling, content analysis, and graph metrics. Our open-source tools are used by researchers and developers working on content structure analysis."),
    "referral-program": ("Referral Program", "Earn credit by referring other brands to Acme. Referral rewards include account credits and plan upgrades for both the referrer and the referred brand. No limit on referral earnings."),
    "affiliate-program": ("Affiliate Program", "Content creators, consultants, and influencers can earn commission by recommending Acme through our affiliate program. Affiliates receive tracking links, marketing materials, and monthly commission payments."),
    "student-program": ("Student and Academic Program", "Free access to Acme for students and academic researchers studying AI search, content optimization, and information retrieval. Includes full platform access, research data exports, and academic support."),
}

about_urls = [f"https://acme.com/about/{slug}" for slug in about_content]
add_page(about_index, "# About Acme\n\nWe help brands win in the age of AI search. Acme was founded on the research showing that website structure predicts AI citation rates — and we build the tools that make structural optimization accessible to every brand.", pick(about_urls, 5))

for slug, (title, body) in about_content.items():
    url = f"https://acme.com/about/{slug}"
    links = [about_index]
    if random.random() < 0.10:
        links += pick([a for a in about_urls if a != url], 1)
    add_page(url, f"# {title}\n\n{body}", links)


# =============================================================================
# INTEGRATIONS — MODERATE HUB (~49 pages)
# Directory with clear index hub, moderate linking within categories.
# =============================================================================

integration_index = "https://acme.com/integrations"

integration_categories = {
    "cms": {
        "desc": "Connect Acme with your content management system for automatic content synchronization, structural analysis of published content, and link recommendation delivery directly in your editorial workflow.",
        "items": {
            "wordpress": ("WordPress", "The WordPress integration syncs your published content with Acme for real-time structural analysis. Automatically detects new pages, updated content, and internal link changes. Delivers optimization recommendations as WordPress admin notifications."),
            "contentful": ("Contentful", "Connect Contentful's headless CMS with Acme to analyze content structure across your content model. Maps Contentful references to internal links for structural analysis and delivers recommendations through Contentful webhooks."),
            "sanity": ("Sanity", "The Sanity integration uses GROQ queries to extract content relationships and map them to Acme's structural analysis framework. Supports real-time content change detection and bidirectional sync for link recommendations."),
            "strapi": ("Strapi", "Connect your Strapi CMS with Acme via REST or GraphQL API. The integration maps Strapi's relational content model to internal link graphs and synchronizes content updates in real time."),
            "ghost": ("Ghost", "The Ghost integration monitors your Ghost publication for content changes and analyzes the internal link structure of published posts. Delivers structural recommendations through the Ghost admin panel."),
            "webflow": ("Webflow", "Connect Webflow to Acme for structural analysis of your visually designed site. The integration handles Webflow's component-based architecture and dynamic collections, mapping CMS relationships to link graphs."),
            "drupal": ("Drupal", "The Drupal integration supports both Drupal core and popular contributed modules. Maps Drupal's content types, taxonomy, and menu system to Acme's structural analysis framework."),
        },
    },
    "analytics": {
        "desc": "Connect your analytics platform to Acme for citation-to-business attribution. Correlate AI visibility data with website traffic, engagement, and conversion metrics.",
        "items": {
            "google-analytics": ("Google Analytics", "Connect Google Analytics 4 to correlate AI citation data with website traffic and engagement metrics. The integration maps citation events to GA4 sessions for attribution analysis and ROI measurement."),
            "mixpanel": ("Mixpanel", "The Mixpanel integration sends citation events as Mixpanel events, enabling funnel analysis from AI citation to product engagement. Track how citation-driven visitors behave differently from other traffic sources."),
            "amplitude": ("Amplitude", "Connect Amplitude for behavioral analysis of citation-driven traffic. The integration sends citation attribution data as Amplitude events, enabling cohort analysis and retention tracking for AI-acquired users."),
            "heap": ("Heap", "The Heap integration automatically captures citation-driven visits without manual event configuration. Heap's autocapture combined with Acme's citation data enables retroactive analysis of AI traffic behavior."),
            "segment": ("Segment", "Route Acme citation data through Segment to any downstream analytics or marketing tool. The integration sends citation events as Segment track calls, enabling distribution to your entire analytics stack."),
            "plausible": ("Plausible", "Connect Plausible Analytics for privacy-friendly citation traffic analysis. The integration maps AI referral sources to Plausible's traffic attribution model without compromising visitor privacy."),
        },
    },
    "crm": {
        "desc": "Connect your CRM to Acme for end-to-end attribution from AI citation to revenue. Track which citations generate leads and which close deals.",
        "items": {
            "salesforce": ("Salesforce", "The Salesforce integration maps citation data to leads, opportunities, and accounts. Track which AI citations generate pipeline, attribute revenue to content clusters, and report AI visibility ROI in Salesforce dashboards."),
            "hubspot": ("HubSpot", "Connect HubSpot for full-funnel attribution from AI citation to customer. The integration creates HubSpot timeline events for citations, maps citation traffic to contacts, and attributes deals to AI visibility."),
            "pipedrive": ("Pipedrive", "The Pipedrive integration tracks AI citation-driven leads through your sales pipeline. Maps citation events to Pipedrive activities and attributes deal revenue to the content clusters that generated visibility."),
            "zoho": ("Zoho CRM", "Connect Zoho CRM to track AI-generated leads from citation to close. The integration maps citation traffic to Zoho contacts, creates citation activities, and feeds AI visibility data into Zoho Analytics."),
            "monday": ("Monday.com", "The Monday.com integration connects AI visibility data with your project management workflows. Create optimization tasks from recommendations, track structural improvement projects, and report progress alongside business metrics."),
        },
    },
    "marketing": {
        "desc": "Connect your marketing automation platform to Acme for citation-aware nurturing, segmentation, and campaign targeting.",
        "items": {
            "mailchimp": ("Mailchimp", "The Mailchimp integration segments your audience by AI citation engagement. Create email campaigns targeting visitors who arrived via AI citations, and report on citation-driven email performance."),
            "klaviyo": ("Klaviyo", "Connect Klaviyo to trigger automated flows based on citation events. Send personalized follow-ups to visitors who arrive via AI citations, and segment audiences by the topics they discovered through AI."),
            "activecampaign": ("ActiveCampaign", "The ActiveCampaign integration maps citation attribution to contact profiles, enabling citation-aware automation sequences and lead scoring that incorporates AI visibility signals."),
            "marketo": ("Marketo", "Connect Marketo for enterprise marketing automation with AI citation intelligence. The integration creates Marketo activities for citation events, enables citation-based lead scoring, and feeds AI data into Marketo Analytics."),
            "braze": ("Braze", "The Braze integration sends citation events as Braze custom events, enabling AI-aware messaging campaigns, user segmentation by citation-driven engagement, and cross-channel attribution."),
        },
    },
    "ecommerce": {
        "desc": "Connect your ecommerce platform to Acme for product content structure analysis, citation tracking for product pages, and shopping-query optimization.",
        "items": {
            "shopify": ("Shopify", "The Shopify integration analyzes your store's product content structure — category hierarchy, product relationships, and internal linking patterns. Identifies structural improvements that would increase product page citations in AI shopping recommendations."),
            "woocommerce": ("WooCommerce", "Connect WooCommerce for product content structure analysis. The integration maps WooCommerce's product categories, tags, and related products to Acme's structural analysis framework for citation optimization."),
            "magento": ("Magento", "The Magento integration handles Magento's complex category hierarchy and attribute-based navigation. Analyzes product content structure and identifies the mesh-like navigation patterns that suppress AI citations."),
            "bigcommerce": ("BigCommerce", "Connect BigCommerce for product catalog structure analysis. The integration maps BigCommerce's category tree and product relationships to link graphs for structural optimization."),
            "squarespace": ("Squarespace", "The Squarespace integration analyzes your Squarespace site's content structure including product pages, blog posts, and custom pages. Delivers structural recommendations compatible with Squarespace's design tools."),
        },
    },
    "collaboration": {
        "desc": "Connect your collaboration tools to Acme for team notifications, task management integration, and workflow automation.",
        "items": {
            "slack": ("Slack", "The Slack integration delivers real-time citation alerts, weekly reports, and optimization recommendations to your team's Slack channels. Configure notification routing by alert type, severity, and topic."),
            "notion": ("Notion", "Connect Notion to receive structured optimization recommendations as Notion database entries. Create content briefs, track structural improvement tasks, and maintain your AI visibility knowledge base in Notion."),
            "confluence": ("Confluence", "The Confluence integration publishes AI visibility reports and optimization documentation directly to your Confluence space. Keep your team's documentation current with automated structural health updates."),
            "asana": ("Asana", "Create Asana tasks from Acme optimization recommendations. The integration maps recommendations to Asana projects with priority, assignee, and due date based on the recommendation's expected citation impact."),
            "jira": ("Jira", "The Jira integration creates tickets from optimization recommendations with proper priority, labels, and descriptions. Track structural improvement work alongside your engineering sprints."),
            "linear": ("Linear", "Connect Linear for streamlined task creation from optimization recommendations. The integration creates Linear issues with priority, labels, and project assignment based on recommendation type and expected impact."),
            "clickup": ("ClickUp", "The ClickUp integration converts Acme recommendations into ClickUp tasks with custom fields for citation impact, structural metrics, and recommendation type. Track optimization work within your existing project management workflow."),
        },
    },
    "data": {
        "desc": "Connect your data platform to Acme for custom analysis, data warehousing, and integration with your broader analytics infrastructure.",
        "items": {
            "snowflake": ("Snowflake", "Export Acme data to Snowflake for custom analysis and integration with your broader data warehouse. The connector supports incremental loads, schema evolution, and direct query access through Snowflake's SQL interface."),
            "bigquery": ("BigQuery", "The BigQuery integration exports citation data, structural metrics, and competitive intelligence to your BigQuery dataset. Enables custom analysis, ML model training on citation data, and integration with Looker dashboards."),
            "databricks": ("Databricks", "Connect Databricks for advanced analysis of your AI visibility data. Export citation and structural data to Delta Lake tables, build custom ML models for citation prediction, and create advanced visualizations."),
            "looker": ("Looker", "The Looker integration provides pre-built LookML models for AI visibility analysis. Explore citation data, structural metrics, and competitive intelligence through Looker's semantic layer with your custom dimensions."),
            "tableau": ("Tableau", "Connect Tableau for visual analysis of your AI visibility data. The integration provides Tableau-ready data extracts with optimized schemas for citation analysis, structural health dashboards, and competitive reporting."),
            "powerbi": ("Power BI", "The Power BI integration provides DirectQuery access to your Acme data for real-time dashboard creation. Pre-built Power BI templates include citation trends, structural health, and competitive positioning visualizations."),
        },
    },
}

all_integration_urls = []
int_cat_indices = []

for cat, cat_data in integration_categories.items():
    cat_url = f"https://acme.com/integrations/{cat}"
    int_cat_indices.append(cat_url)
    int_urls = [f"https://acme.com/integrations/{cat}/{name}" for name in cat_data["items"]]
    all_integration_urls.extend(int_urls)

    add_page(cat_url, f"# {cat.title()} Integrations\n\n{cat_data['desc']}", int_urls + [integration_index])

    for int_slug, (int_name, int_body) in cat_data["items"].items():
        int_url = f"https://acme.com/integrations/{cat}/{int_slug}"
        links = [cat_url, integration_index]
        if random.random() < 0.30:
            links += pick([u for u in int_urls if u != int_url], random.randint(1, 2))
        if random.random() < 0.15:
            other_cat = random.choice([c for c in integration_categories if c != cat])
            other_slug = random.choice(list(integration_categories[other_cat]["items"].keys()))
            links.append(f"https://acme.com/integrations/{other_cat}/{other_slug}")
        add_page(int_url, f"# {int_name} Integration\n\n{int_body}", links)

add_page(integration_index, "# Integrations\n\n50+ integrations to connect Acme with your existing tools — CMS, analytics, CRM, marketing automation, ecommerce, collaboration, and data platforms. Each integration is designed to embed AI visibility data into your existing workflows.", int_cat_indices)


# =============================================================================
# CHANGELOG — REVERSE CHAIN (25 pages)
# Chronological entries with prev/next links.
# =============================================================================

changelog_index = "https://acme.com/changelog"
changelog_months = [f"https://acme.com/changelog/2025-{m:02d}" for m in range(1, 13)] + \
                   [f"https://acme.com/changelog/2024-{m:02d}" for m in range(1, 13)]

changelog_content = [
    "Launched real-time citation streaming API. Added support for Claude and Gemini citation tracking. Improved crawl performance by 40% through parallel content extraction. Fixed edge cases in URL normalization for redirect chains.",
    "Released content structure scoring v2 with graph-based cluster detection. Added topology archetype classification for content clusters. New competitive intelligence dashboard with side-by-side structural comparison. Bug fixes for webhook delivery reliability.",
    "Added automated content brief generation based on citation gap analysis. Launched integration with Contentful and Sanity CMS platforms. Improved embedding model with fine-tuned topic clustering. Performance improvements for large-site crawl analysis.",
    "Released hub-spoke detection algorithm with visual cluster maps. Added pruning recommendations based on cluster coherence analysis. New API endpoints for batch structural analysis. Fixed timezone handling in scheduled report delivery.",
    "Launched cross-section connectivity analysis showing how content clusters link to each other. Added boundary metric tracking for cluster-level optimization. New Slack integration with configurable alert routing. Improved mobile dashboard responsiveness.",
    "Released A/B testing framework for structural changes. Added link density warnings for mesh anti-patterns. New BigQuery and Snowflake export integrations. Performance optimization for enterprise accounts with 50+ brands.",
    "Added voice search optimization recommendations based on query intent analysis. Launched international SEO module with hreflang validation. New team performance reports by content owner. Bug fixes for citation matching with parameterized URLs.",
    "Released advanced competitor tracking with structural comparison. Added market landscape visualization. New Salesforce integration with full-funnel citation attribution. Improved crawl scheduling for sites with rapid content updates.",
    "Launched executive summary auto-generation for weekly reports. Added trend detection with configurable sensitivity thresholds. New Shopify and WooCommerce integrations for ecommerce structure analysis. Fixed pagination handling for API list endpoints.",
    "Released content refresh scheduler with freshness-based prioritization. Added semantic coherence analysis using embedding variance. New Linear and Jira integrations for task management. Performance improvements for real-time citation feed.",
    "Added ROI attribution model connecting citation data to revenue. Launched custom metric builder for business-specific KPIs. New Tableau and Power BI integrations. Bug fixes for SSO authentication with certain SAML providers.",
    "Released platform roadmap preview. Added goal tracking with visual progress indicators. New benchmark library with industry-specific AI visibility data. Improved API documentation with interactive examples.",
    "Initial platform launch with core citation monitoring, structural analysis, and basic reporting. Support for ChatGPT and Perplexity citation tracking. REST API with Python SDK.",
    "Added Google AI Overview citation tracking. Released internal link auditor with structural health scoring. New team management features with role-based access control. Integration with Google Analytics 4.",
    "Launched competitor tracking for up to 5 competitors per brand. Added content cluster detection using URL-path segmentation. New automated weekly report delivery. Bug fixes for crawl depth calculation.",
    "Released optimization recommendation engine with specific link suggestions. Added hub page identification algorithm. New HubSpot integration for lead attribution. Performance improvements for sites with 1000+ pages.",
    "Added white-label reporting for agency accounts. Released custom dashboard builder with drag-and-drop widgets. New Slack integration for real-time alerts. Improved crawl error handling and retry logic.",
    "Launched API key management with configurable scopes. Added audit logging for compliance. New Mixpanel and Amplitude integrations. Bug fixes for redirect chain detection in crawl analysis.",
    "Released batch API for bulk operations. Added webhook support with configurable event types. New data export in CSV and JSON formats. Performance optimization for structural metric computation.",
    "Added SSO support via SAML 2.0 and OIDC. Released workspace settings and team permission model. New Segment integration for analytics routing. Improved URL normalization for canonical URL detection.",
    "Launched GraphQL API for flexible data querying. Added streaming API for real-time event consumption. New WordPress integration for CMS synchronization. Bug fixes for citation matching with shortened URLs.",
    "Released content gap analysis based on competitive citation data. Added keyword opportunity scoring. New Pipedrive and Zoho CRM integrations. Performance improvements for large competitive analysis queries.",
    "Added multi-brand management for enterprise accounts. Released agency workspace configuration. New Databricks integration for advanced analytics. Improved embedding generation throughput.",
    "Launched citation decay monitoring to track citation lifecycle. Added response quality analyzer for brand representation accuracy. New Notion and Confluence integrations. Bug fixes for scheduled report timezone handling.",
]

add_page(changelog_index, "# Changelog\n\nAll platform updates, new features, and improvements. We ship updates monthly and document every change here. Subscribe to release notifications for automatic updates.", changelog_months[:6])

for i, entry in enumerate(changelog_months):
    month_label = entry.split("/")[-1]
    content = changelog_content[i] if i < len(changelog_content) else "Platform stability improvements, bug fixes, and performance optimizations based on customer feedback."
    links = [changelog_index]
    if i > 0:
        links.append(changelog_months[i - 1])
    if i < len(changelog_months) - 1:
        links.append(changelog_months[i + 1])
    if random.random() < 0.20:
        links += pick(all_docs[:10], 1)
    add_page(entry, f"# Changelog — {month_label}\n\n{content}", links)


# =============================================================================
# WEBINARS — SMALL HUB-SPOKE (21 pages)
# Archive links to all; recordings link back to archive only.
# =============================================================================

webinar_index = "https://acme.com/webinars"

webinar_content = {
    "ai-search-masterclass": ("AI Search Masterclass: From SEO to AIO", "A comprehensive 90-minute session covering the fundamentals of AI search optimization. We walk through how LLMs select sources, what structural patterns predict citation, and how to audit your site for AI readiness. Includes live Q&A and downloadable audit checklist."),
    "citation-tracking-deep-dive": ("Citation Tracking Deep Dive", "Technical deep dive into citation tracking methodology — how we monitor AI responses, parse citations, match URLs, and compute visibility metrics. Ideal for analytics teams implementing AI visibility measurement."),
    "content-structure-workshop": ("Content Structure Workshop", "Hands-on workshop where participants analyze their own site's content structure using our research framework. We walk through hub-spoke identification, link density analysis, and cluster health scoring with real examples."),
    "seo-to-aio-transition": ("Making the SEO to AIO Transition", "Practical guide for SEO teams expanding into AI search optimization. Covers what transfers from traditional SEO (content quality, technical health), what's different (link topology, cluster structure), and how to build an AIO program."),
    "brand-visibility-summit": ("Brand Visibility Summit 2025", "Our annual summit featuring customer presentations, research reveals, and product previews. This year's theme: structural intelligence — how data-driven content architecture is becoming the primary lever for AI visibility."),
    "technical-seo-2025": ("Technical SEO for AI: 2025 Update", "Updated guide to technical SEO factors that affect AI crawling and citation. Covers rendering strategies, structured data, crawl optimization, and the technical infrastructure needed for AI-friendly sites."),
    "content-ops-at-scale": ("Content Operations at Scale", "How enterprise teams manage content structure optimization across hundreds of brands and thousands of pages. Covers workflow design, team structure, tool integration, and measurement frameworks for scaled content operations."),
    "measuring-ai-roi": ("Measuring AI Visibility ROI", "Framework for connecting AI citation data to business outcomes. Covers attribution modeling, conversion tracking, revenue correlation, and building the business case for AI visibility investment."),
    "competitive-intel-playbook": ("The Competitive Intelligence Playbook", "How to use competitive structural analysis to identify and exploit content architecture advantages. Covers competitor crawl analysis, structural benchmarking, gap identification, and competitive response strategies."),
    "enterprise-onboarding": ("Enterprise Onboarding Session", "Guided onboarding for enterprise customers covering multi-brand setup, team configuration, SSO integration, custom reporting, and API access. Includes implementation timeline planning and success criteria definition."),
    "agency-partner-training": ("Agency Partner Training", "Training session for agency partners covering platform features, client management workflows, white-label reporting, and best practices for delivering AI visibility services to clients."),
    "product-demo-live": ("Live Product Demo", "Interactive platform walkthrough covering all major features — monitoring, analysis, optimization, and reporting. Includes live configuration of a real brand analysis with Q&A throughout."),
    "customer-success-stories": ("Customer Success Roundtable", "Panel discussion featuring customers from SaaS, ecommerce, and healthcare sharing their AI visibility optimization journeys. Covers challenges, strategies, results, and lessons learned."),
    "roadmap-preview-q2": ("Q2 Roadmap Preview", "Preview of upcoming features and capabilities planned for Q2 2025. Includes direct optimization tools, enhanced competitive intelligence, and new integration partnerships."),
    "api-workshop": ("API Integration Workshop", "Hands-on workshop for developers building integrations with the Acme API. Covers authentication, common API patterns, webhook setup, and building custom workflows with the API."),
    "data-driven-content": ("Data-Driven Content Strategy", "How to use AI citation data to inform your content strategy — from topic selection and content prioritization to structural planning and performance measurement."),
    "international-expansion": ("International AI Visibility", "Strategies for managing AI visibility across multiple languages and regions. Covers hreflang configuration, regional content clusters, and measuring AI visibility by market."),
    "healthcare-vertical": ("AI Visibility for Healthcare Brands", "Industry-specific session covering the unique challenges and opportunities for healthcare brands in AI search — authority requirements, compliance considerations, and content structure patterns that work in health information."),
    "ecommerce-vertical": ("AI Visibility for Ecommerce", "Industry-specific session covering ecommerce content structure optimization — product category architecture, comparison content strategy, and overcoming the mesh navigation anti-pattern."),
    "fintech-vertical": ("AI Visibility for Fintech", "Industry-specific session covering fintech content optimization — regulatory content architecture, trust signal establishment, and building authority in financial information queries."),
}

webinar_pages = [f"https://acme.com/webinars/{slug}" for slug in webinar_content]
add_page(webinar_index, "# Webinars\n\nLive and on-demand webinars on AI search optimization. Our webinar series covers strategy, implementation, and measurement for teams at every stage of their AI visibility journey.", pick(webinar_pages, 6))

for slug, (title, body) in webinar_content.items():
    url = f"https://acme.com/webinars/{slug}"
    links = [webinar_index]
    if random.random() < 0.10:
        links += pick(blog_posts, 1)
    add_page(url, f"# {title}\n\n{body}", links)


# =============================================================================
# CROSS-SECTION LINKS
# =============================================================================

for page_url, page_data in list(pages.items()):
    if page_url.startswith("https://acme.com/solutions/") and "/solutions/" in page_url:
        if random.random() < 0.15:
            page_data["links"].append(random.choice(all_docs[:20]))

for post in blog_posts:
    if random.random() < 0.12:
        pages[post]["links"].append(random.choice(pillar_urls))
    if random.random() < 0.08:
        pages[post]["links"].append(random.choice(cs_pages[:5]))

for page_url in list(pages.keys()):
    if page_url.startswith("https://acme.com/case-studies/") and "study" in page_url:
        if random.random() < 0.25:
            pages[page_url]["links"].append(random.choice(pillar_urls))

# Homepage
add_page("https://acme.com", "# Acme — AI Search Optimization Platform\n\nHelp your brand get cited by AI. Acme monitors your visibility across LLM platforms, analyzes your content structure against the signals that predict citation, and guides you toward the structural improvements that drive measurable AI visibility gains.", [
    solutions_index, products_index, blog_index, docs_index,
    cs_index, integration_index, "https://acme.com/pricing",
    about_index,
])


# =============================================================================
# DEDUPLICATE & OUTPUT
# =============================================================================

for url, page in pages.items():
    seen = set()
    clean = []
    for link in page["links"]:
        if link != url and link not in seen:
            seen.add(link)
            clean.append(link)
    page["links"] = clean

output = sorted(pages.values(), key=lambda p: p["url"])

Path("data").mkdir(exist_ok=True)
with open("data/pages.json", "w") as f:
    json.dump(output, f, indent=2)

print(f"Total pages: {len(output)}")
print(f"Total links: {sum(len(p['links']) for p in output)}")
print()

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
    cluster_urls = {p["url"] for p in cpages}
    intra = sum(1 for p in cpages for l in p["links"] if l in cluster_urls)
    max_edges = n * (n - 1) if n > 1 else 1
    density = intra / max_edges
    avg_deg = intra / n if n > 0 else 0
    print(f"{name:<20} {n:>6} {total_links:>6} {avg_deg:>8.1f} {density:>8.4f}")
