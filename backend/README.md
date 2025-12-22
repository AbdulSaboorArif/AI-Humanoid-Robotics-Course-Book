# RAG Website Ingestion and Retrieval Backend

This backend provides a complete RAG (Retrieval-Augmented Generation) system for the Physical AI & Humanoid Robotics Course. It includes both an ingestion pipeline to crawl and store course content in a vector database, and a retrieval API to query that content for RAG chatbot integration.

## Features

- **Website Ingestion**: Crawls the Physical AI & Humanoid Robotics Course website (https://ai-humanoid-robotics-course-book.vercel.app/)
- **Content Extraction**: Extracts clean educational content while filtering out navigation and layout elements
- **Embedding Generation**: Creates high-quality embeddings using Cohere's embed-english-v3.0 model
- **Vector Storage**: Stores embeddings with rich metadata in Qdrant vector database
- **Retrieval API**: FastAPI endpoint for querying relevant content based on user queries
- **Module Hierarchy**: Preserves the 13-week course structure and module/section relationships

## Prerequisites

- Python 3.11+
- pip package manager
- Git (optional, for cloning)

## Setup

### 1. Clone and Navigate to Backend Directory

```bash
cd backend
```

### 2. Create a Virtual Environment (Recommended)

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

### 3. Install Dependencies

```bash
# Using uv (recommended)
uv pip install -r requirements.txt

# Alternative using pip
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Create an `.env` file by copying the example:

```bash
cp .env.example .env
```

Edit the `.env` file with your API keys:

```bash
# Edit .env file with your favorite editor
nano .env
```

Required environment variables:
- `COHERE_API_KEY`: Your Cohere API key (get from https://dashboard.cohere.com/api-keys)
- `QDRANT_URL`: Your Qdrant cluster URL (or leave empty for local instance)
- `QDRANT_API_KEY`: Your Qdrant API key (or leave empty for local instance)

### 5. Verify Setup

Run the ingestion pipeline to fetch and process the course content:

```bash
python main.py
```

## Usage

### 1. Run the Ingestion Pipeline

The ingestion pipeline will:
- Crawl the Physical AI & Humanoid Robotics Course website
- Extract clean content from all pages
- Generate embeddings using Cohere
- Store content with metadata in Qdrant

```bash
python main.py
```

### 2. Start the Retrieval API Server

Start the FastAPI server to enable querying of the stored content:

```bash
uvicorn retrieval:app --host 0.0.0.0 --port 8000 --reload
```

Or run the retrieval server directly:

```bash
python retrieval.py
```

### 3. Query the Retrieval API

Once the server is running, you can query it using:

```
GET http://localhost:8000/retrieve?query=your_search_query&k=5
```

Example with curl:

```bash
curl "http://localhost:8000/retrieve?query=What%20is%20Physical%20AI?&k=5"
```

The API supports the following parameters:
- `query`: The search query (required)
- `k`: Number of results to return (default: 5, max: 20)
- `module_filter`: Filter results by specific module
- `section_filter`: Filter results by specific section

### 4. Check API Health

Check the health of the retrieval service:

```
GET http://localhost:8000/health
```

Get available modules:

```
GET http://localhost:8000/modules
```

## API Endpoints

### `/retrieve`
- **Method**: GET
- **Description**: Retrieve relevant content chunks based on the query
- **Parameters**:
  - `query` (required): Search query
  - `k` (optional): Number of results (default: 5, max: 20)
  - `module_filter` (optional): Filter by module
  - `section_filter` (optional): Filter by section
- **Response**: JSON with query, results, and metadata

### `/health`
- **Method**: GET
- **Description**: Check service health and collection status

### `/modules`
- **Method**: GET
- **Description**: Get list of all available modules in the collection

### `/`
- **Method**: GET
- **Description**: Health check endpoint

## Architecture

The system consists of two main components:

### Ingestion Pipeline (main.py)
1. **URL Discovery**: Gets all URLs from sitemap.xml or uses fallback URLs
2. **Content Extraction**: Extracts clean text content from each URL, preserving module/section hierarchy
3. **Content Chunking**: Splits content into meaningful chunks while maintaining context
4. **Embedding Generation**: Creates embeddings using Cohere embed-english-v3.0 (1024 dimensions)
5. **Storage**: Saves embeddings with rich metadata to Qdrant vector database

### Retrieval API (retrieval.py)
1. **Query Processing**: Accepts search queries and generates embeddings
2. **Vector Search**: Finds relevant content in Qdrant using cosine similarity
3. **Response Formatting**: Returns top-k results with metadata for RAG chatbot integration

## Data Model

The system stores content with the following metadata:
- `id`: Unique identifier for the chunk
- `text`: The actual content text
- `url`: Source URL
- `title`: Page title
- `module`: Course module (e.g., "Week 1-2: Introduction to Physical AI")
- `section`: Specific section within the module
- `hierarchy_path`: Full path in content hierarchy
- `word_count`: Number of words in the chunk
- `embedding`: 1024-dimensional vector representation
- `created_at`: Timestamp when chunk was created

## Configuration

### Environment Variables

- `COHERE_API_KEY`: Cohere API key for embedding generation
- `QDRANT_URL`: Qdrant cluster URL (leave empty for local instance)
- `QDRANT_API_KEY`: Qdrant API key
- `TARGET_WEBSITE_URL`: URL of the course website (default: https://ai-humanoid-robotics-course-book.vercel.app/)
- `COLLECTION_NAME`: Qdrant collection name (default: rag_embedding)
- `PORT`: API server port (default: 8000)

### Collection Configuration

The Qdrant collection is configured with:
- 1024-dimensional vectors (for Cohere embed-english-v3.0)
- Cosine distance metric
- HNSW indexing (m=16, ef_construct=128)
- Payload indexes for metadata fields (url, module, section, hierarchy_path)

## Dependencies

- `requests`: HTTP requests
- `beautifulsoup4`: HTML parsing
- `cohere`: Embedding generation
- `qdrant-client`: Vector database interaction
- `python-dotenv`: Environment variable management
- `fastapi`: Web framework for retrieval API
- `uvicorn`: ASGI server
- `tqdm`: Progress bars
- `lxml`: XML parsing for sitemaps
- `markdownify`: HTML to markdown conversion
- `urllib3`: HTTP client
- `pydantic`: Data validation

## Troubleshooting

### Common Issues

1. **Rate Limiting**: The system includes 1-second delays between requests to respect the target website. If you encounter rate limits, consider increasing the delay.

2. **API Keys**: Ensure your Cohere and Qdrant API keys are valid and have sufficient quota.

3. **Network Issues**: The ingestion pipeline includes retry mechanisms for network errors.

4. **Large Content**: Very large pages are automatically chunked to maintain optimal search performance.

### Logging

The ingestion pipeline logs progress to both console and `ingestion.log` file. Check these logs for detailed information about the processing status.

## Testing

The ingestion pipeline includes a test search function that runs after processing to verify the system is working correctly. You can also manually test the retrieval API by making requests to the endpoints.

## Performance

- The ingestion pipeline processes approximately 20 pages of the course website
- Embeddings are generated using Cohere's efficient embed-english-v3.0 model
- Qdrant provides fast vector search with HNSW indexing
- The system handles the full 13-week Physical AI & Humanoid Robotics course structure