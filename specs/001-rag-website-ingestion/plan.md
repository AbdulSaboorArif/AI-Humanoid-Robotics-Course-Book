# Implementation Plan: RAG Website Ingestion and Vectorization Pipeline

**Branch**: `001-rag-website-ingestion` | **Date**: 2025-12-20 | **Spec**: [link to spec.md](spec.md)
**Input**: Feature specification from `/specs/001-rag-website-ingestion/spec.md`

**Note**: This template is filled in by the `/sp.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Implementation of a RAG (Retrieval-Augmented Generation) ingestion pipeline to crawl, extract, clean, chunk, embed, and store content from the Docusaurus-based Physical AI & Humanoid Robotics Textbook website (https://hackathon-physical-ai-humanoid-text-sigma.vercel.app/) into a Qdrant vector database using Cohere embeddings. The system is implemented as a single Python file (main.py) with functions for crawling, content extraction, chunking by module/section hierarchy, embedding generation, and vector storage. The website contains 7 modules (ROS2 Foundations, Simulation, Hardware Basics, VLA Foundations, Advanced AI Control, Humanoid Design, and Appendix) with approximately 19-20 pages organized in a hierarchical structure.

## Technical Context

**Language/Version**: Python 3.11+
**Primary Dependencies**: requests, beautifulsoup4, cohere, qdrant-client, python-dotenv, markdownify, lxml, urllib3
**Storage**: Qdrant Cloud vector database
**Testing**: pytest
**Target Platform**: Linux server (backend service)
**Project Type**: single backend service
**Performance Goals**: Process ~20 pages within 24 hours, <200ms embedding generation per chunk, handle rate limits appropriately
**Constraints**: <1GB memory usage during processing, resume from checkpoints, handle Docusaurus-specific structure, respect public content only with polite delays
**Scale/Scope**: 7-module textbook with ~20 pages, module/section hierarchy preservation
**Target Site**: https://ai-humanoid-robotics-course-book.vercel.app/
**Sitemap.xml**: https://ai-humanoid-robotics-course-book.vercel.app/sitemap.xml

## Architecture Overview

### System Architecture
```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    RAG Website Ingestion Pipeline                           │
├─────────────────────────────────────────────────────────────────────────────┤
│  ┌─────────────┐    ┌──────────────────┐    ┌──────────────────┐            │
│  │   Website   │───▶│ Content Pipeline │───▶│ Vector Database  │            │
│  │   Crawler   │    │                  │    │                  │            │
│  └─────────────┘    └──────────────────┘    └──────────────────┘            │
│         │                      │                       │                    │
│         ▼                      ▼                       ▼                    │
│  ┌─────────────┐    ┌──────────────────┐    ┌──────────────────┐            │
│  │   Target    │    │   Processing     │    │  Qdrant Cloud    │            │
│  │   Website   │    │   Functions      │    │   Vector DB      │            │
│  │(Docusaurus) │    │                  │    │                  │            │
│  └─────────────┘    └──────────────────┘    └──────────────────┘            │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Component Architecture
```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        main.py Implementation                               │
├─────────────────────────────────────────────────────────────────────────────┤
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐              │
│  │ get_all_urls()  │  │ chunk_text()    │  │ create_collection() │          │
│  │ - Discover all  │  │ - Split content │  │ - Initialize      │            │
│  │   website URLs  │  │   by hierarchy  │  │   Qdrant collection│           │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘              │
│         │                       │                       │                   │
│         ▼                       ▼                       ▼                   │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐              │
│  │extract_text_from│  │   embed()       │  │save_chunk_to_   │              │
│  │ _url()          │  │ - Generate      │  │ qdrant()        │              │
│  │ - Extract clean │  │   Cohere        │  │ - Store with    │              │
│  │   content       │  │   embeddings    │  │   metadata      │              │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘              │
│         │                       │                       │                   │
│         └───────────────────────┼───────────────────────┘                   │
│                                 ▼                                           │
│  ┌─────────────────────────────────────────────────────────────────────────┐ │
│  │                     ingest_book()                                       │ │
│  │              Main orchestration function                                │ │
│  └─────────────────────────────────────────────────────────────────────────┘ │
│                                 │                                           │
│                                 ▼                                           │
│  ┌─────────────────────────────────────────────────────────────────────────┐ │
│  │                         main()                                          │ │
│  │                   Entry point function                                  │ │
│  └─────────────────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Data Flow Architecture
```
1. Website Crawling → 2. Content Extraction → 3. Content Chunking → 4. Embedding → 5. Storage
   get_all_urls()      extract_text_from_url()  chunk_text()         embed()       save_chunk_to_qdrant()
   ↓                   ↓                        ↓                    ↓             ↓
   URL List            Clean Text               Structured Chunks    Vector        Qdrant DB
   (Docusaurus)        (HTML → Text)            (by Module/Section)  (Cohere)      (with Metadata)
```

## Website Structure Analysis

### Target Website: https://hackathon-physical-ai-humanoid-text-sigma.vercel.app/

**Textbook Overview:**
- Module-based structure with 7 core modules covering Physical AI & Humanoid Robotics
- ~19-20 total pages with consistent Docusaurus documentation layout
- Sequential learning progression from ROS2 basics to humanoid design
- Public content with GitHub integration

**Module Structure:**
1. **Module 1**: ROS2 Foundations (docs/ros2/module-1-ros2-foundations)
2. **Module 2**: Simulation (docs/simulation/module-2-simulation)
3. **Module 3**: Hardware Basics (docs/hardware/module-3-hardware-basics)
4. **Module 4**: VLA Foundations (docs/vla/module-4-vla-foundations)
5. **Module 5**: Advanced AI Control (docs/advanced/module-5-advanced-ai-control)
6. **Module 6**: Humanoid Design (docs/humanoid/module-6-humanoid-design)
7. **Appendix**: Glossary and references

**Content Organization:**
- Home/introduction page with overview
- Module index pages with theoretical foundations
- Hands-on/practical components within each module
- Reference materials and glossary in appendix
- GitHub links and social profiles

**Content Types:**
- Theoretical concepts and principles
- Practical hands-on components
- Code examples and implementation guides
- Technical documentation and specifications
- Reference materials and glossary

**Docusaurus-Specific Elements:**
- Sidebar navigation with complete module outline
- Breadcrumb navigation showing current location
- "Next" buttons for sequential progression
- Section anchors for direct linking to topics
- Standard Docusaurus documentation layout

## Function Breakdown

### Core Functions in main.py:

1. **get_all_urls()**: Discovers all accessible URLs from the target Docusaurus website by parsing sitemap.xml and following navigation links. Specifically targets the 7-module structure with modules for ROS2, Simulation, Hardware, VLA, Advanced AI, and Humanoid Design.

2. **extract_text_from_url()**: Extracts clean educational content from each URL, specifically filtering out navigation, headers, footers, and other non-content elements while preserving theoretical concepts, code examples, and technical specifications from the Physical AI textbook.

3. **chunk_text()**: Splits content into meaningful chunks preserving the module/section hierarchy (by module, section, topic). Respects the educational boundaries between modules (Module 1-6) and maintains content relationships within each module while preserving the sequential learning progression.

4. **embed()**: Generates high-quality embeddings using Cohere's embed-english-v3.0 model (1024 dimensions), optimized for technical content related to robotics, AI, ROS 2, simulation, and humanoid systems.

5. **create_collection()**: Sets up the Qdrant vector database collection with appropriate schema and configuration to store the 7-module textbook content with proper metadata for educational content.

6. **save_chunk_to_qdrant()**: Stores content chunks with embeddings and rich metadata in Qdrant database, including module/section information, content type (theoretical/practical/code), and educational context while preserving the hierarchical structure.

7. **ingest_book()**: Main orchestration function that coordinates the entire pipeline, processing the 7-module textbook in order while maintaining the educational progression and content relationships.

8. **main()**: Entry point that executes the complete ingestion process, starting from the introduction and progressing through all 6 modules and appendix.

## Data Model Architecture

The system handles four primary data entities:

- **ContentChunk**: Educational content segments with semantic boundaries preserved, including module/section information from the 7-module textbook structure
- **SourceMetadata**: Information about original location and context (URL, title, hierarchy, content type - theoretical/practical/code, module/section path)
- **EmbeddingVector**: Numerical representations (1024 dimensions) for semantic similarity matching, optimized for robotics/AI technical content using Cohere embed-english-v3.0
- **ProcessingPipeline**: Records of pipeline execution status and checkpoints for the multi-module textbook processing

## Technical Implementation Details

### Content Extraction Strategy:
- Uses BeautifulSoup with Docusaurus-specific CSS selectors
- Targets the specific 7-module textbook structure and module organization
- Preserves code blocks, technical specifications, and educational content
- Filters out navigation, headers, footers, and other non-educational elements
- Maintains content hierarchy and structure (Module → Section → Topic)

### Website Crawling Strategy:
- Discovers URLs through sitemap.xml parsing as primary method
- Follows the 7-module structure: ros2, simulation, hardware, vla, advanced, humanoid, appendix
- Respects the module breakdown (Module 1 through Module 6 plus appendix)
- Handles Docusaurus-specific navigation patterns and page relationships
- Implements polite delays between requests to respect public content

### Chunking Strategy:
- Semantic chunking using document structure (headings, sections) within the educational context
- Respects educational boundaries (modules, sections, and sequential progression)
- Ensures chunks are neither too large (lose specificity) nor too small (break context)
- Maintains 500-1000 words per chunk as optimal for RAG applications
- Preserves the module-based learning progression and content relationships
- Maintains module/section hierarchy in metadata during chunking

### Embedding Strategy:
- Uses Cohere's embed-english-v3.0 model with 1024 dimensions optimized for technical content
- Processes robotics, AI, and engineering content from the Physical AI textbook
- Includes educational metadata in embedding process for better retrieval
- Handles specialized terminology in ROS 2, simulation, hardware, and humanoid robotics
- Preserves module/section context in embedding metadata

### Storage Strategy:
- Qdrant Cloud for scalable vector storage of the comprehensive 7-module textbook
- Rich metadata storage including module/section information, content type, and educational context
- Proper indexing for fast similarity search across the structured textbook content
- Maintains relationships between textbook modules and sequential progression
- Preserves module/section hierarchy in Qdrant metadata

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

The implementation aligns with the Physical AI & Humanoid Robotics Course constitution by:
- Supporting the module-based learning program structure (7 core modules)
- Providing educational content access through RAG system for enhanced learning
- Following academic rigor with proper citations and structured content
- Enabling conversational robotics education through accessible knowledge base
- Using validated technical approaches (Python, web scraping, vector databases)

## Project Structure

### Documentation (this feature)

```text
specs/001-rag-website-ingestion/
├── plan.md              # This file (/sp.plan command output)
├── research.md          # Phase 0 output (/sp.plan command)
├── data-model.md        # Phase 1 output (/sp.plan command)
├── quickstart.md        # Phase 1 output (/sp.plan command)
├── contracts/           # Phase 1 output (/sp.plan command)
└── tasks.md             # Phase 2 output (/sp.tasks command - NOT created by /sp.plan)
```

### Source Code (repository root)

```text
backend/
├── main.py              # Single-file implementation with all required functions
├── requirements.txt     # Project dependencies
├── .env                 # Environment variables
└── .gitignore           # Git ignore rules
```

**Structure Decision**: Single-file Python implementation (main.py) with minimal dependencies to maintain simplicity and focus on the core RAG ingestion functionality as specified.

## Phase 1 Artifacts

- **research.md**: Technical decisions for sitemap parsing, Docusaurus content extraction, rate limiting, and embedding strategies
- **data-model.md**: Entity definitions for ContentChunk, SourceMetadata, EmbeddingVector, and ProcessingPipeline
- **quickstart.md**: Setup and execution instructions for the RAG ingestion pipeline
- **contracts/**: (Not applicable for this single-file backend implementation)

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| [e.g., 4th project] | [current need] | [why 3 projects insufficient] |
| [e.g., Repository pattern] | [specific problem] | [why direct DB access insufficient] |
