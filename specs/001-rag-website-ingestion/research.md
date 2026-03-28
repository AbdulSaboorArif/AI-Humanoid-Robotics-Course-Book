# Research: RAG Website Ingestion and Vectorization Pipeline

## Decision: Web Crawling Approach Using Sitemap.xml
**Rationale**: For the Physical AI & Humanoid Robotics Textbook website (https://hackathon-physical-ai-humanoid-text-sigma.vercel.app/), using sitemap.xml as the primary URL discovery method is most effective. The sitemap reveals 19 total pages organized in 7 modules, providing a complete and reliable list of URLs without requiring complex crawling logic. This approach respects rate limits and avoids overloading the public site.
**Alternatives considered**:
- Manual URL following: Less reliable and could miss pages
- Scrapy: More complex for simple use case
- Playwright/Selenium: Unnecessary for static Docusaurus content

## Decision: Docusaurus Content Extraction Best Practices
**Rationale**: Docusaurus sites have predictable structure with content in specific CSS classes (typically `.markdown`, `.theme-doc-markdown`). Using BeautifulSoup with Docusaurus-specific selectors (main content area, sidebar navigation exclusion) will extract clean educational content while filtering out navigation, headers, and footers. Adding polite delays (1-2 seconds) between requests respects public content hosting.
**Alternatives considered**:
- Direct MDX parsing: More complex than needed
- Pandoc: External dependency not needed
- Custom regex: Less reliable than CSS selectors

## Decision: Module/Section Hierarchy Preservation in Chunking
**Rationale**: For educational content with 7 sequential modules, preserving the module/section hierarchy in metadata is crucial for maintaining learning context. Using semantic chunking with document structure (H1, H2, H3 headings) while maintaining module boundaries ensures chunks retain their educational context for RAG applications.
**Alternatives considered**:
- Fixed token length: Breaks educational context
- Sentence-based: Doesn't respect module boundaries
- Paragraph-based: May miss important hierarchical structure

## Decision: Cohere embed-english-v3.0 Model (1024 dimensions)
**Rationale**: Cohere's embed-english-v3.0 model with 1024 dimensions is specifically optimized for technical content and provides excellent performance for robotics/AI educational material. The 1024-dimensional vectors provide good balance of performance and storage efficiency for the ~20-page textbook.
**Alternatives considered**:
- OpenAI embeddings: Different pricing model and dimensions
- Sentence Transformers: Self-hosted option but requires more maintenance
- embed-multilingual-v3.0: English model is sufficient for this content

## Decision: Qdrant Vector Database with Rich Metadata
**Rationale**: Qdrant offers cloud-hosted solution with excellent Python client, proper metadata filtering capabilities, and efficient similarity search needed for educational content retrieval. The ability to store module/section hierarchy in metadata is essential for the textbook structure.
**Alternatives considered**:
- Pinecone: Good alternative but Qdrant has better metadata handling
- Weaviate: Good option but Qdrant simpler for this use case
- Chroma: Self-hosted only, more complex setup

## Decision: Rate Limiting and Polite Crawling
**Rationale**: Since this is a public educational website, implementing rate limiting with 1-2 second delays between requests and respecting robots.txt is essential for responsible crawling. This ensures we don't overload the hosting infrastructure while accessing public content.
**Alternatives considered**:
- No rate limiting: Could overload the server
- Complex adaptive rate limiting: Unnecessary for this scale
- Parallel requests: Could be too aggressive for public site

## Decision: Single File Architecture (main.py) with Complete Function Set
**Rationale**: As specified in requirements, implementing as a single file with all functions (get_all_urls, extract_text_from_url, chunk_text, embed, create_collection, save_chunk_to_qdrant, ingest_book, main) maintains simplicity for the ~20-page textbook while meeting the specified implementation requirements.
**Alternatives considered**:
- Multi-file modular: Against requirements
- Package structure: More complex than needed for single-file implementation