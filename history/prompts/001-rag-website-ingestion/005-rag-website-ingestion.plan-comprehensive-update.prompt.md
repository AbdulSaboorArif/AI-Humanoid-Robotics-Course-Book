---
id: 005
title: "Comprehensive Plan Update for Textbook RAG Pipeline"
stage: plan
date_iso: "2025-12-20"
surface: "agent"
model: "Claude Sonnet 4.5"
feature: "001-rag-website-ingestion"
branch: "001-rag-website-ingestion"
user: "user"
command: "/sp.plan"
labels:
  - "rag"
  - "ingestion"
  - "pipeline"
  - "planning"
  - "architecture"
  - "ai"
  - "education"
  - "textbook"
  - "docusaurus"
files_yaml:
  - "specs/001-rag-website-ingestion/plan.md"
  - "specs/001-rag-website-ingestion/research.md"
  - "specs/001-rag-website-ingestion/data-model.md"
  - "specs/001-rag-website-ingestion/quickstart.md"
  - "history/prompts/001-rag-website-ingestion/005-rag-website-ingestion.plan-comprehensive-update.prompt.md"
tests_yaml:
  - "Plan updated with new website structure"
  - "Research refined for sitemap usage"
  - "Data model updated for module hierarchy"
  - "Quickstart updated for new URL and model"
  - "All files consistent with textbook structure"
---

## Outcome
Comprehensive update of all planning artifacts to reflect the new target website (https://hackathon-physical-ai-humanoid-text-sigma.vercel.app/) with 7-module textbook structure, using Cohere embed-english-v3.0 model, and implementing sitemap-based crawling.

## Evaluation
All planning files (plan.md, research.md, data-model.md, quickstart.md) have been updated to reflect the correct target website structure with 7 modules (~20 pages), using the specified Cohere embed-english-v3.0 model with 1024 dimensions, and implementing sitemap-based URL discovery with module/section hierarchy preservation.

## Prompt Text
```
now update all file that you create during plan like data model quick start research and plan based on this prompt i want actually this plan.md Refine and complete the implementation plan.md for the Docusaurus RAG embedding pipeline

**Target Audience:** AI engineers building RAG ingestion pipelines for Docusaurus-based educational textbooks on Physical AI and Humanoid Robotics

**Focus:** Merge and enhance the provided plan with the structure and details from previous /sp.plan outputs (e.g., detailed architecture diagrams, function breakdowns, data flow, constitution check, project structure). Update specifics to match the actual target site: https://hackathon-physical-ai-humanoid-text-sigma.vercel.app/ (Physical AI & Humanoid Robotics Textbook, module-based structure with ~20 pages). Prioritize using the sitemap.xml for URL discovery. Specify Cohere embed-english-v3.0 (1024 dimensions). Preserve module/section hierarchy in metadata during chunking. Keep single-file main.py implementation. Add practical details from research (sitemap parsing, Docusaurus content extraction best practices, rate limiting).

**Success Criteria:**
- Updated plan reflects accurate site URL, sitemap usage, and cohere, qdrant-client, python-dotenv
- Python version: 3.11+
- Single-file implementation: main.py
- Output: Full revised plan.md in complete Markdown format (replace the old one)
- Timeline: Complete within 2 days
- Respect public content only, add polite delay in crawling

**Not Changing:**
- Core single main.py structure and listed listed functions
- Overall phase breakdown (0 Research, 1 Design, 2 Implementation)
- No addition of new major features (e.g., incremental updates, UI)

**Additional Instructions:** Ensure the plan is comprehensive, actionable, consistent in formatting, and ready to replace the current plan.md file directly.
```

## Response Text
Updated all planning artifacts as requested:

**plan.md**: Complete revision with 7-module textbook structure (ROS2, Simulation, Hardware, VLA, Advanced AI, Humanoid Design, Appendix), sitemap-based crawling, Cohere embed-english-v3.0 details, and module/section hierarchy preservation.

**research.md**: Updated with sitemap.xml crawling approach, Docusaurus content extraction best practices, embed-english-v3.0 rationale, and rate limiting strategies.

**data-model.md**: Revised entities to reflect module-based structure instead of weekly structure, with 1024-dimensional embeddings and module hierarchy preservation in metadata.

**quickstart.md**: Updated with correct target URL, installation instructions including urllib3, environment variables, and execution instructions specific to the textbook structure.

All files are now consistent with the new target website and requirements.