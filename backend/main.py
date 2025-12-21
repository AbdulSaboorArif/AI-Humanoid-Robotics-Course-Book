# #!/usr/bin/env python3
# """
# RAG Website Ingestion Pipeline

# This script ingests content from a Docusaurus website by:
# 1. Parsing the sitemap.xml to discover all content URLs
# 2. Extracting clean educational text from each page
# 3. Chunking text semantically with configurable size and overlap
# 4. Generating embeddings using Cohere's embed-english-v3.0 model
# 5. Storing vectors and metadata in Qdrant Cloud collection

# Author: Claude Code
# Date: 2025-12-21
# """

# import os
# import random
# import time
# import logging
# import xml.etree.ElementTree as ET
# from typing import List, Dict, Optional, Tuple
# from urllib.parse import urljoin, urlparse
# import requests
# from bs4 import BeautifulSoup
# import cohere
# from qdrant_client import QdrantClient
# from qdrant_client.http.models import (
#     PointStruct,
#     VectorParams,
#     Distance,
#     HnswConfigDiff,
#     PayloadSchemaType
# )
# from dotenv import find_dotenv, load_dotenv
# from tqdm import tqdm
# import re
# import json
# from datetime import datetime
# from dotenv import load_dotenv
# load_dotenv(find_dotenv())


# # Configure logging
# logging.basicConfig(
#     level=logging.INFO,
#     format='%(asctime)s - %(levelname)s - %(message)s',
#     handlers=[
#         logging.FileHandler('ingestion.log'),
#         logging.StreamHandler()
#     ]
# )

# logger = logging.getLogger(__name__)

# class RAGWebsiteIngestor:
#     def __init__(self):
#         # Load configuration from environment
#         self.cohere_client = cohere.Client(api_key=os.getenv('COHERE_API_KEY'))
#         self.qdrant_client = QdrantClient(
#             url=os.getenv('QDRANT_URL'),
#             api_key=os.getenv('QDRANT_API_KEY')
#         )

#         # Configuration
#         self.target_site = "https://ai-humanoid-robotics-course-book.vercel.app/"
#         self.sitemap_url = f"{self.target_site}/sitemap.xml"
#         self.collection_name = os.getenv('COLLECTION_NAME', 'physical_ai_humanoid_textbook')
#         self.vector_size = 1024  # Cohere embed-english-v3.0 dimension
#         self.chunk_size = 1000
#         self.chunk_overlap = 100
#         self.delay_range = (1, 2)  # seconds between requests

#         logger.info(f"Initialized ingestor for {self.target_site}")

#     def get_sitemap_urls(self, sitemap_url: str) -> List[str]:
#         """
#         Parse sitemap.xml to extract all content URLs.

#         Args:
#             sitemap_url: URL of the sitemap to parse

#         Returns:
#             List of content URLs
#         """
#         logger.info(f"Fetching sitemap from {sitemap_url}")

#         try:
#             response = requests.get(sitemap_url, timeout=30)
#             response.raise_for_status()

#             root = ET.fromstring(response.content)

#             # Handle both standard sitemap and sitemap index formats
#             urls = [
#                     "https://ai-humanoid-robotics-course-book.vercel.app/docs/intro",
#                     "hhttps://ai-humanoid-robotics-course-book.vercel.app/docs/intro/week1-2",
#                     "https://ai-humanoid-robotics-course-book.vercel.app/docs/intro/week3-4",
#                     "https://ai-humanoid-robotics-course-book.vercel.app/docs/intro/week5-6",
#                     "https://ai-humanoid-robotics-course-book.vercel.app/docs/intro/week7-8",
#                     "https://ai-humanoid-robotics-course-book.vercel.app/docs/intro/week9-10",
#                     "https://ai-humanoid-robotics-course-book.vercel.app/docs/intro/week11-12",
#                     "https://ai-humanoid-robotics-course-book.vercel.app/docs/intro/week13-14",
#                     "https://ai-humanoid-robotics-course-book.vercel.app/docs/intro/week15-16",
#                     "https://ai-humanoid-robotics-course-book.vercel.app/docs/intro/week17-18",
                    
#                     ]

#             namespace = {'ns': 'http://www.sitemaps.org/schemas/sitemap/0.9'}

#             # Look for <url><loc> elements (standard sitemap)
#             for url_elem in root.findall('.//ns:url/ns:loc', namespace):
#                 urls.append(url_elem.text.strip())

#             # If no URLs found, try without namespace
#             if not urls:
#                 for url_elem in root.findall('.//url/loc'):
#                     urls.append(url_elem.text.strip())

#             # Also look for sitemap references (sitemap index)
#             sitemap_namespace = {'ns': 'http://www.sitemaps.org/schemas/sitemap/0.9'}
#             for sitemap_elem in root.findall('.//ns:sitemap/ns:loc', sitemap_namespace):
#                 sitemap_ref = sitemap_elem.text.strip()
#                 logger.info(f"Found nested sitemap: {sitemap_ref}")
#                 # Recursively get URLs from nested sitemap
#                 nested_urls = self.get_sitemap_urls(sitemap_ref)
#                 urls.extend(nested_urls)

#             # Filter URLs to only include those from the target site
#             filtered_urls = [
#                 url for url in urls
#                 if url.startswith(self.target_site) and not url.endswith(('.xml', '.jpg', '.png', '.pdf'))
#             ]

#             logger.info(f"Found {len(filtered_urls)} URLs in sitemap")
#             return filtered_urls

#         except Exception as e:
#             logger.error(f"Error parsing sitemap: {str(e)}")
#             return []

#     def extract_text_from_url(self, url: str) -> Tuple[Optional[str], Dict[str, str]]:
#         """
#         Extract clean educational text from a Docusaurus page.

#         Args:
#             url: URL of the page to extract text from

#         Returns:
#             Tuple of (clean text, metadata dictionary)
#         """
#         try:
#             logger.debug(f"Extracting text from {url}")
#             response = requests.get(url, timeout=30)
#             response.raise_for_status()

#             soup = BeautifulSoup(response.content, 'html.parser')

#             # Remove unwanted elements (navigation, headers, footers, sidebars)
#             for element in soup(['nav', 'header', 'footer', 'aside']):
#                 element.decompose()

#             # Remove script and style elements
#             for element in soup(['script', 'style', 'noscript']):
#                 element.decompose()

#             # Try to find main content containers typical in Docusaurus
#             content_selectors = [
#                 'main div[class*="container"]',  # Docusaurus container
#                 'article',  # Main article content
#                 'div.main-wrapper',  # Docusaurus main wrapper
#                 'div.docPage_node_modules-\@docusaurus-theme-classic-lib-next-theme-DocPage-styles-module',  # Specific Docusaurus class
#                 'div[class*="docItemContainer"]',  # Documentation container
#                 'div[class*="theme-doc-markdown"]',  # Markdown content
#                 '[role="main"]',  # Main role
#                 'main'  # Fallback to main tag
#             ]

#             content_element = None
#             for selector in content_selectors:
#                 content_element = soup.select_one(selector)
#                 if content_element:
#                     break

#             # If no content element found, use body
#             if not content_element:
#                 content_element = soup.find('body')

#             if not content_element:
#                 logger.warning(f"No content element found for {url}")
#                 return None, {}

#             # Extract text and clean it
#             text = content_element.get_text(separator='\n', strip=True)

#             # Clean up excessive whitespace
#             text = re.sub(r'\n+', '\n', text)
#             text = re.sub(r'[ \t]+', ' ', text)
#             text = text.strip()

#             # Extract metadata
#             metadata = {
#                 'url': url,
#                 'title': self._extract_title(soup),
#                 'module': self._extract_module_from_url(url),
#                 'section': self._extract_section_from_url(url),
#                 'created_at': datetime.utcnow().isoformat(),
#                 'word_count': len(text.split()),
#                 'char_count': len(text)
#             }

#             logger.debug(f"Extracted {len(text)} characters from {url}")
#             return text, metadata

#         except Exception as e:
#             logger.error(f"Error extracting text from {url}: {str(e)}")
#             return None, {}

#     def _extract_title(self, soup: BeautifulSoup) -> str:
#         """Extract title from the page."""
#         title_tag = soup.find('title')
#         if title_tag:
#             return title_tag.get_text().strip()

#         h1_tag = soup.find('h1')
#         if h1_tag:
#             return h1_tag.get_text().strip()

#         return ""

#     def _extract_module_from_url(self, url: str) -> str:
#         """Extract module information from URL path."""
#         parsed = urlparse(url)
#         path_parts = parsed.path.strip('/').split('/')

#         # Look for common documentation patterns
#         for i, part in enumerate(path_parts):
#             if part in ['docs', 'modules', 'chapters']:
#                 if i + 1 < len(path_parts):
#                     return path_parts[i + 1]

#         # Return the first meaningful path segment after domain
#         for part in path_parts:
#             if part and part != 'index':
#                 return part

#         return "unknown"

#     def _extract_section_from_url(self, url: str) -> str:
#         """Extract section information from URL path."""
#         parsed = urlparse(url)
#         path_parts = parsed.path.strip('/').split('/')

#         # Look for the last meaningful path segment
#         for part in reversed(path_parts):
#             if part and part != 'index':
#                 return part

#         return "overview"

#     def chunk_text(self, text: str, metadata: Dict[str, str]) -> List[Dict[str, str]]:
#         """
#         Chunk text semantically with configurable size and overlap.

#         Args:
#             text: Text to chunk
#             metadata: Metadata to include with each chunk

#         Returns:
#             List of chunk dictionaries with text and metadata
#         """
#         if not text:
#             return []

#         chunks = []
#         start_idx = 0
#         position = 0

#         while start_idx < len(text):
#             # Determine chunk end position
#             end_idx = start_idx + self.chunk_size

#             # If we're near the end, take the rest
#             if end_idx >= len(text):
#                 end_idx = len(text)
#             else:
#                 # Try to break at sentence boundary
#                 temp_end = min(end_idx, len(text))
#                 while temp_end < len(text) and text[temp_end] not in '.!?':
#                     temp_end += 1
#                 if temp_end < len(text):
#                     end_idx = temp_end + 1  # Include the punctuation
#                 else:
#                     end_idx = temp_end

#             chunk_text = text[start_idx:end_idx].strip()

#             if chunk_text:  # Only add non-empty chunks
#                 chunk_metadata = metadata.copy()
#                 chunk_metadata.update({
#                     'chunk_text': chunk_text,
#                     'position': position,
#                     'start_idx': start_idx,
#                     'end_idx': end_idx,
#                     'chunk_length': len(chunk_text)
#                 })

#                 chunks.append(chunk_metadata)
#                 position += 1

#             # Move to next chunk position with overlap
#             start_idx = end_idx - self.chunk_overlap
#             if start_idx >= len(text):
#                 break
#             elif start_idx <= start_idx:  # Prevent infinite loop
#                 start_idx = end_idx  # Move past the chunk without overlap

#         logger.debug(f"Created {len(chunks)} chunks from {metadata['url']}")
#         return chunks

#     def embed_chunks(self, chunks: List[Dict[str, str]]) -> List[Tuple[List[float], Dict[str, str]]]:
#         """
#         Generate embeddings for text chunks using Cohere.

#         Args:
#             chunks: List of chunk dictionaries

#         Returns:
#             List of tuples (embedding_vector, metadata_dict)
#         """
#         if not chunks:
#             return []

#         # Prepare texts for embedding
#         texts = [chunk['chunk_text'] for chunk in chunks]

#         try:
#             logger.info(f"Generating embeddings for {len(texts)} chunks")
#             response = self.cohere_client.embed(
#                 texts=texts,
#                 model='embed-english-v3.0',
#                 input_type='search_document'
#             )

#             embeddings = response.embeddings
#             result = []

#             for i, chunk in enumerate(chunks):
#                 if i < len(embeddings):
#                     result.append((embeddings[i], chunk))
#                 else:
#                     logger.error(f"No embedding returned for chunk {i}")

#             logger.info(f"Generated {len(result)} embeddings successfully")
#             return result

#         except Exception as e:
#             logger.error(f"Error generating embeddings: {str(e)}")
#             return []

#     def create_collection(self) -> bool:
#         """
#         Create Qdrant collection with appropriate configuration.

#         Returns:
#             True if collection exists or was created successfully
#         """
#         try:
#             collections = self.qdrant_client.get_collections()

#             # Check if collection already exists
#             collection_exists = any(col.name == self.collection_name for col in collections.collections)

#             if collection_exists:
#                 logger.info(f"Collection '{self.collection_name}' already exists")
#                 # Update collection configuration if needed
#                 self.qdrant_client.update_collection(
#                     collection_name=self.collection_name,
#                     hnsw_config=HnswConfigDiff(m_ef_construct=128, m=16),
#                 )
#             else:
#                 logger.info(f"Creating collection '{self.collection_name}'")
#                 self.qdrant_client.create_collection(
#                     collection_name=self.collection_name,
#                     vectors_config=VectorParams(
#                         size=self.vector_size,
#                         distance=Distance.COSINE
#                     ),
#                     hnsw_config=HnswConfigDiff(m=16, ef_construct=128),
#                     optimizers_config={
#                         "memmap_threshold": 20000,
#                         "indexing_threshold": 20000,
#                     }
#                 )

#                 # Set payload schema for metadata
#                 self.qdrant_client.create_payload_index(
#                     collection_name=self.collection_name,
#                     field_name="url",
#                     field_schema=PayloadSchemaType.KEYWORD
#                 )

#                 self.qdrant_client.create_payload_index(
#                     collection_name=self.collection_name,
#                     field_name="module",
#                     field_schema=PayloadSchemaType.KEYWORD
#                 )

#                 self.qdrant_client.create_payload_index(
#                     collection_name=self.collection_name,
#                     field_name="section",
#                     field_schema=PayloadSchemaType.KEYWORD
#                 )

#             return True

#         except Exception as e:
#             logger.error(f"Error creating collection: {str(e)}")
#             return False

#     def save_chunks_to_qdrant(self, embeddings_data: List[Tuple[List[float], Dict[str, str]]]) -> int:
#         """
#         Save chunk embeddings to Qdrant collection.

#         Args:
#             embeddings_data: List of tuples (embedding_vector, metadata_dict)

#         Returns:
#             Number of points saved successfully
#         """
#         if not embeddings_data:
#             return 0

#         try:
#             points = []
#             for i, (embedding, metadata) in enumerate(embeddings_data):
#                 point = PointStruct(
#                     id=i,
#                     vector=embedding,
#                     payload=metadata
#                 )
#                 points.append(point)

#             logger.info(f"Uploading {len(points)} points to Qdrant")

#             # Upload in batches
#             batch_size = 100
#             successful_uploads = 0

#             for i in tqdm(range(0, len(points), batch_size), desc="Uploading to Qdrant"):
#                 batch = points[i:i + batch_size]
#                 self.qdrant_client.upsert(
#                     collection_name=self.collection_name,
#                     points=batch,
#                     wait=True
#                 )
#                 successful_uploads += len(batch)

#             logger.info(f"Successfully uploaded {successful_uploads} points to Qdrant")
#             return successful_uploads

#         except Exception as e:
#             logger.error(f"Error saving chunks to Qdrant: {str(e)}")
#             return 0

#     def search_test(self, query: str = "sensorimotor intelligence", top_k: int = 3) -> List[Dict]:
#         """
#         Test search functionality to verify ingestion worked.

#         Args:
#             query: Query text to search for
#             top_k: Number of top results to return

#         Returns:
#             List of search results
#         """
#         try:
#             # Generate embedding for query
#             response = self.cohere_client.embed(
#                 texts=[query],
#                 model='embed-english-v3.0',
#                 input_type='search_query'
#             )
#             query_embedding = response.embeddings[0]

#             # Search in Qdrant
#             search_results = self.qdrant_client.search(
#                 collection_name=self.collection_name,
#                 query_vector=query_embedding,
#                 limit=top_k,
#                 with_payload=True
#             )

#             results = []
#             for result in search_results:
#                 results.append({
#                     'score': result.score,
#                     'payload': result.payload,
#                     'text_preview': result.payload.get('chunk_text', '')[:200] + '...'
#                 })

#             logger.info(f"Test search completed for query: '{query}'")
#             return results

#         except Exception as e:
#             logger.error(f"Error during test search: {str(e)}")
#             return []

#     def ingest_pipeline(self) -> Dict[str, int]:
#         """
#         Execute the complete ingestion pipeline.

#         Returns:
#             Dictionary with statistics about the ingestion process
#         """
#         stats = {
#             'urls_found': 0,
#             'pages_processed': 0,
#             'chunks_created': 0,
#             'embeddings_generated': 0,
#             'points_saved': 0
#         }

#         logger.info("Starting RAG website ingestion pipeline")

#         # Step 1: Get URLs from sitemap
#         urls = self.get_sitemap_urls(self.sitemap_url)
#         stats['urls_found'] = len(urls)

#         if not urls:
#             logger.error("No URLs found in sitemap")
#             return stats

#         # Step 2: Create Qdrant collection
#         if not self.create_collection():
#             logger.error("Failed to create Qdrant collection")
#             return stats

#         # Step 3: Process each URL
#         all_chunks = []
#         for i, url in enumerate(tqdm(urls, desc="Processing pages")):
#             logger.debug(f"Processing {i+1}/{len(urls)}: {url}")

#             # Extract text and metadata
#             text, metadata = self.extract_text_from_url(url)

#             if text:
#                 # Chunk the text
#                 chunks = self.chunk_text(text, metadata)
#                 all_chunks.extend(chunks)
#                 stats['pages_processed'] += 1

#             # Respectful delay between requests
#             time.sleep(random.uniform(*self.delay_range))

#         stats['chunks_created'] = len(all_chunks)
#         logger.info(f"Created {stats['chunks_created']} chunks from {stats['pages_processed']} pages")

#         if not all_chunks:
#             logger.warning("No chunks were created, stopping pipeline")
#             return stats

#         # Step 4: Generate embeddings
#         embeddings_data = self.embed_chunks(all_chunks)
#         stats['embeddings_generated'] = len(embeddings_data)

#         if not embeddings_data:
#             logger.error("No embeddings were generated, stopping pipeline")
#             return stats

#         # Step 5: Save to Qdrant
#         stats['points_saved'] = self.save_chunks_to_qdrant(embeddings_data)

#         logger.info("Ingestion pipeline completed")
#         return stats

#     def run_test_search(self):
#         """Run a test search to verify the ingestion worked."""
#         logger.info("Running test search to verify ingestion...")

#         test_queries = [
#             "sensorimotor intelligence",
#             "AI robotics",
#             "humanoid",
#             "machine learning"
#         ]

#         for query in test_queries:
#             results = self.search_test(query, top_k=2)
#             logger.info(f"\nTop results for query '{query}':")
#             for i, result in enumerate(results, 1):
#                 logger.info(f"  {i}. Score: {result['score']:.3f}")
#                 logger.info(f"     URL: {result['payload'].get('url', 'N/A')}")
#                 logger.info(f"     Module: {result['payload'].get('module', 'N/A')}")
#                 logger.info(f"     Section: {result['payload'].get('section', 'N/A')}")
#                 logger.info(f"     Preview: {result['text_preview']}")
#                 logger.info("")


# def main():
#     """Main entry point for the RAG ingestion pipeline."""
#     logger.info("Starting RAG Website Ingestion Pipeline")

#     try:
#         ingestor = RAGWebsiteIngestor()
#         stats = ingestor.ingest_pipeline()

#         logger.info("Pipeline Statistics:")
#         logger.info(f"  URLs found: {stats['urls_found']}")
#         logger.info(f"  Pages processed: {stats['pages_processed']}")
#         logger.info(f"  Chunks created: {stats['chunks_created']}")
#         logger.info(f"  Embeddings generated: {stats['embeddings_generated']}")
#         logger.info(f"  Points saved: {stats['points_saved']}")

#         if stats['points_saved'] > 0:
#             logger.info("Running test search...")
#             ingestor.run_test_search()

#     except Exception as e:
#         logger.error(f"Pipeline failed: {str(e)}")
#         return 1

#     return 0


# if __name__ == "__main__":
#     exit(main())
import os
import requests
from bs4 import BeautifulSoup
import xml.etree.ElementTree as ET
from typing import List, Dict, Any
import cohere
from qdrant_client import QdrantClient
from qdrant_client.http import models
from qdrant_client.models import PointStruct
import logging
from urllib.parse import urljoin, urlparse
import time
import uuid
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DocusaurusEmbeddingPipeline:
    def __init__(self):
        # Initialize Cohere client
        self.cohere_client = cohere.Client(api_key=os.getenv("DUwA29gOutJC6TGjwSB4xo6w07jwemeqYjPrJnl1"))

        # Initialize Qdrant client
        qdrant_url = os.getenv("QDRANT_URL", "https://d1f4e4fd-25a0-449b-9f5c-4c042d2c4be1.europe-west3-0.gcp.cloud.qdrant.io")
        qdrant_api_key = os.getenv("QDRANT_API_KEY")

        if qdrant_api_key:
            self.qdrant_client = QdrantClient(url=qdrant_url, api_key=qdrant_api_key)
        else:
            self.qdrant_client = QdrantClient(url=qdrant_url)

        # Target URL for the Docusaurus site
        self.target_url = "https://ai-humanoid-robotics-course-book.vercel.app/"

    def get_all_urls(self, base_url: str) -> List[str]:
        """
        Extract all URLs from a deployed Docusaurus site using sitemap
        """
        urls = []

        try:
            # Try to get URLs from sitemap first
            sitemap_url = urljoin(base_url, "sitemap.xml")
            response = requests.get(sitemap_url)

            if response.status_code == 200:
                root = ET.fromstring(response.content)

                # Handle both sitemap index and regular sitemap
                if root.tag.endswith('sitemapindex'):
                    # If it's a sitemap index, get individual sitemaps
                    for sitemap in root.findall('.//{http://www.sitemaps.org/schemas/sitemap/0.9}loc'):
                        sitemap_response = requests.get(sitemap.text)
                        if sitemap_response.status_code == 200:
                            sitemap_root = ET.fromstring(sitemap_response.content)
                            for url_elem in sitemap_root.findall('.//{http://www.sitemaps.org/schemas/sitemap/0.9}loc'):
                                urls.append(url_elem.text)
                else:
                    # Regular sitemap
                    for url_elem in root.findall('.//{http://www.sitemaps.org/schemas/sitemap/0.9}loc'):
                        urls.append(url_elem.text)
            else:
                # Fallback: try to crawl the site by looking for links
                logger.info(f"Sitemap not found at {sitemap_url}, attempting to crawl...")

                # Get the main page and extract links
                response = requests.get(base_url)
                soup = BeautifulSoup(response.content, 'html.parser')

                # Find all links within the page
                for link in soup.find_all('a', href=True):
                    href = link['href']
                    full_url = urljoin(base_url, href)

                    # Only add URLs from the same domain
                    if urlparse(full_url).netloc == urlparse(base_url).netloc:
                        if full_url not in urls and full_url.startswith(base_url):
                            urls.append(full_url)

        except Exception as e:
            logger.error(f"Error getting URLs from {base_url}: {e}")

        return urls

    def extract_text_from_url(self, url: str) -> str:
        """
        Extract and clean text from a single URL
        """
        try:
            response = requests.get(url)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, 'html.parser')

            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.decompose()

            # Look for main content containers typically used in Docusaurus
            # Try multiple selectors to find the main content
            content_selectors = [
                'article',  # Main article content
                '.markdown',  # Docusaurus markdown content
                '.theme-doc-markdown',  # Docusaurus theme markdown
                '.main-wrapper',  # Main content wrapper
                'main',  # Main content area
                '.container',  # Container with content
                '[role="main"]'  # Main role
            ]

            content = ""
            for selector in content_selectors:
                elements = soup.select(selector)
                if elements:
                    for element in elements:
                        # Get text but try to preserve some structure
                        text = element.get_text(separator=' ', strip=True)
                        if len(text) > len(content):
                            content = text
                    break

            # If no specific content found, get all body text
            if not content:
                body = soup.find('body')
                if body:
                    content = body.get_text(separator=' ', strip=True)

            # Clean up the text
            lines = (line.strip() for line in content.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            content = ' '.join(chunk for chunk in chunks if chunk)

            return content

        except Exception as e:
            logger.error(f"Error extracting text from {url}: {e}")
            return ""

    def chunk_text(self, text: str, chunk_size: int = 1000, overlap: int = 100) -> List[str]:
        """
        Split text into chunks with overlap to preserve context
        """
        if len(text) <= chunk_size:
            return [text]

        chunks = []
        start = 0

        while start < len(text):
            end = start + chunk_size
            chunk = text[start:end]
            chunks.append(chunk)

            # Move start position by chunk_size - overlap
            start = end - overlap

            # If remaining text is less than chunk_size, add it as final chunk
            if len(text) - start < chunk_size:
                if start < len(text):
                    final_chunk = text[start:]
                    if final_chunk not in chunks:  # Avoid duplicate chunks
                        chunks.append(final_chunk)
                break

        return chunks

    def embed(self, text: str) -> List[float]:
        """
        Generate embedding for text using Cohere
        """
        try:
            response = self.cohere_client.embed(
                texts=[text],
                model="embed-multilingual-v3.0",  # Using multilingual model
                input_type="search_document"  # Optimize for search
            )
            return response.embeddings[0]  # Return the first (and only) embedding
        except Exception as e:
            logger.error(f"Error generating embedding for text: {e}")
            return []

    def create_collection(self, collection_name: str = "rag_embedding"):
        """
        Create a Qdrant collection for storing embeddings
        """
        try:
            # Check if collection already exists
            collections = self.qdrant_client.get_collections()
            collection_names = [col.name for col in collections.collections]

            if collection_name in collection_names:
                logger.info(f"Collection {collection_name} already exists")
                return

            # Create collection with appropriate vector size (1024 for Cohere embeddings)
            self.qdrant_client.create_collection(
                collection_name=collection_name,
                vectors_config=models.VectorParams(size=1024, distance=models.Distance.COSINE)
            )

            logger.info(f"Created collection {collection_name} with 1024-dimension vectors")

        except Exception as e:
            logger.error(f"Error creating collection {collection_name}: {e}")
            raise

    def save_chunk_to_qdrant(self, content: str, url: str, embedding: List[float], position: int, collection_name: str = "rag_embedding"):
        """
        Save a text chunk with its embedding to Qdrant
        """
        try:
            # Generate a unique ID for the point
            point_id = str(uuid.uuid4())

            # Prepare the payload with metadata
            payload = {
                "content": content,
                "url": url,
                "position": position,
                "created_at": time.time()
            }

            # Create and upload the point to Qdrant
            points = [PointStruct(
                id=point_id,
                vector=embedding,
                payload=payload
            )]

            self.qdrant_client.upsert(
                collection_name=collection_name,
                points=points
            )

            logger.info(f"Saved chunk to Qdrant: {url} (position {position})")
            return True

        except Exception as e:
            logger.error(f"Error saving chunk to Qdrant: {e}")
            return False

def main():
    """
    Main function to execute the complete pipeline
    """
    logger.info("Starting Docusaurus Embedding Pipeline...")

    # Initialize the pipeline
    pipeline = DocusaurusEmbeddingPipeline()

    try:
        # Step 1: Create the Qdrant collection
        logger.info("Creating Qdrant collection...")
        pipeline.create_collection("rag_embedding")

        # Step 2: Get all URLs from the target Docusaurus site
        logger.info(f"Extracting URLs from {pipeline.target_url}...")
        urls = pipeline.get_all_urls(pipeline.target_url)

        if not urls:
            logger.warning(f"No URLs found at {pipeline.target_url}")
            return

        logger.info(f"Found {len(urls)} URLs to process")

        # Step 3: Process each URL
        total_chunks = 0
        for i, url in enumerate(urls):
            logger.info(f"Processing URL {i+1}/{len(urls)}: {url}")

            # Extract text from the URL
            text_content = pipeline.extract_text_from_url(url)

            if not text_content:
                logger.warning(f"No content extracted from {url}")
                continue

            logger.info(f"Extracted {len(text_content)} characters from {url}")

            # Chunk the text
            chunks = pipeline.chunk_text(text_content)
            logger.info(f"Created {len(chunks)} chunks from {url}")

            # Process each chunk
            for j, chunk in enumerate(chunks):
                if not chunk.strip():
                    continue

                # Generate embedding
                embedding = pipeline.embed(chunk)

                if not embedding:
                    logger.error(f"Failed to generate embedding for chunk {j} of {url}")
                    continue

                # Save to Qdrant
                success = pipeline.save_chunk_to_qdrant(
                    content=chunk,
                    url=url,
                    embedding=embedding,
                    position=j
                )

                if success:
                    total_chunks += 1
                    logger.info(f"Successfully saved chunk {j} of {url} to Qdrant")
                else:
                    logger.error(f"Failed to save chunk {j} of {url} to Qdrant")

        logger.info(f"Pipeline completed successfully! Total chunks saved: {total_chunks}")

    except Exception as e:
        logger.error(f"Pipeline failed with error: {e}")
        raise

if __name__ == "__main__":
    main()