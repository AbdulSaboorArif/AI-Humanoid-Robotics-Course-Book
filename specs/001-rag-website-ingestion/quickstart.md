# Quickstart: RAG Website Ingestion and Vectorization Pipeline

## Prerequisites

- Python 3.11+
- pip package manager
- Git (optional, for cloning)

## Setup

1. **Create the backend directory and navigate to it**:
   ```bash
   mkdir backend
   cd backend
   ```

2. **Create a virtual environment** (recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies using uv** (if available) or pip:
   ```bash
   # Using uv (as requested in the spec)
   uv pip install requests beautifulsoup4 cohere qdrant-client python-dotenv markdownify lxml urllib3

   # Alternative using pip
   pip install requests beautifulsoup4 cohere qdrant-client python-dotenv markdownify lxml urllib3
   ```

4. **Create environment file**:
   ```bash
   touch .env
   ```

5. **Add required environment variables to `.env`**:
   ```
   COHERE_API_KEY=your_cohere_api_key_here
   QDRANT_URL=your_qdrant_cluster_url
   QDRANT_API_KEY=your_qdrant_api_key
   TARGET_WEBSITE_URL=https://hackathon-physical-ai-humanoid-text-sigma.vercel.app/
   COLLECTION_NAME=physical_ai_humanoid_textbook
   ```

## Configuration

The main.py file contains all required functions as specified:

- `get_all_urls`: Discovers all URLs from the target website using sitemap.xml
- `extract_text_from_url`: Extracts clean text content from a URL with Docusaurus-specific selectors
- `chunk_text`: Splits content into meaningful chunks preserving module/section hierarchy
- `embed`: Generates embeddings using Cohere embed-english-v3.0 model (1024 dimensions)
- `create_collection`: Sets up the Qdrant collection with appropriate schema
- `save_chunk_to_qdrant`: Stores chunks with rich metadata in Qdrant
- `ingest_book`: Main orchestration function processing 7 modules in sequence
- `main`: Entry point function

## Running the Pipeline

1. **Execute the main script**:
   ```bash
   python main.py
   ```

2. **Monitor the output** for progress information

## Expected Output

- All ~20 pages from https://hackathon-physical-ai-humanoid-text-sigma.vercel.app/ will be crawled via sitemap.xml
- Content will be extracted, cleaned, and chunked by module/section hierarchy
- Embeddings will be generated using Cohere embed-english-v3.0 (1024 dimensions)
- Results will be stored in Qdrant with module/section metadata preserved
- Polite delays will be used to respect public content hosting

## Troubleshooting

- If you get rate-limited, the system implements 1-2 second delays between requests
- Check your API keys are valid and have sufficient quota
- Ensure the target website is accessible
- For the ~20-page textbook, the process should complete within 24 hours
- Verify sitemap.xml is accessible at the target website