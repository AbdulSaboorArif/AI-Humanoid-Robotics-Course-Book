#!/usr/bin/env python3
"""
RAG Website Ingestion Pipeline for Physical AI & Humanoid Robotics Course

This script crawls the Docusaurus-based Physical AI & Humanoid Robotics Course website,
extracts clean educational content, chunks it by module/section hierarchy, generates
embeddings using Cohere, and stores them in Qdrant vector database with rich metadata.
"""

import os
import time
import uuid
import requests
import logging
import xml.etree.ElementTree as ET
from typing import List, Dict, Optional, Tuple
from urllib.parse import urljoin, urlparse
import re
from datetime import datetime

from bs4 import BeautifulSoup
import cohere
from qdrant_client import QdrantClient
from qdrant_client.http import models
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())
from tqdm import tqdm
import urllib3

# Disable SSL warnings if needed
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('ingestion.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class RAGWebsiteIngestor:
    """Main class for handling the RAG website ingestion pipeline."""

    def __init__(self):
        """Initialize the RAG Website Ingestor with configuration."""
        self.target_url = os.getenv('TARGET_WEBSITE_URL', 'https://ai-humanoid-robotics-course-book.vercel.app/')
        self.cohere_api_key = os.getenv('COHERE_API_KEY')
        self.qdrant_url = os.getenv('QDRANT_URL')
        self.qdrant_api_key = os.getenv('QDRANT_API_KEY')
        self.collection_name = os.getenv('COLLECTION_NAME', 'rag_embedding')

        # Validate required environment variables
        if not self.cohere_api_key:
            raise ValueError('COHERE_API_KEY')

        # Initialize clients
        self.cohere_client = cohere.Client(self.cohere_api_key)

        if self.qdrant_url:
            self.qdrant_client = QdrantClient(
                url=self.qdrant_url,
                api_key=self.qdrant_api_key,
                timeout=30
            )
        else:
            # Use local Qdrant instance if no URL provided
            self.qdrant_client = QdrantClient(host='localhost', port=6333)

        # Fallback URLs for the 13-week Physical AI Humanoid Robotics course
        self.fallback_urls = [
            "/",
            "/docs/intro",
            "/docs/intro/week1-2",
            "/docs/ros2/week3-5",
            "/docs/simulation/week6-7",
            "/docs/isaac/week8-10",
            "/docs/humanoid/week11-12",
            "/docs/vla/week13",
            "/docs/vla/capstone_overview",
            "/docs/references"
        ]

        # Module mapping based on URL structure
        self.module_mapping = {
            'intro': 'Introduction',
            'week1-2': 'Week 1-2: Introduction to Physical AI',
            'week3-5': 'Week 3-5: ROS2 and Navigation',
            'week6-7': 'Week 6-7: Simulation Environments',
            'week8-10': 'Week 8-10: Isaac Gym and Control',
            'week11-12': 'Week 11-12: Humanoid Locomotion',
            'week13': 'Week 13: VLA and Advanced Topics',
            'capstone_overview': 'Capstone Project',
            'references': 'References'
        }

        if len(self.target_url) < 5:  # If less than expected
                    logger.warning("Sitemap returned few URLs - using fallback")
                    fallback = [
                        self.target_site,
                        self.target_site + 'docs/intro',
                        self.target_site + 'docs/intro/week1-2',
                        self.target_site + 'docs/ros2/week3-5',
                        self.target_site + 'docs/simulation/week6-7',
                        self.target_site + 'docs/isaac/week8-10',
                        self.target_site + 'docs/humanoid/week11-12',
                        self.target_site + 'docs/vla/week13',
                        self.target_site + 'docs/vla/capstone_overview',
                        self.target_site + 'docs/references'
              ]
                    valid_urls = list(set(valid_urls + fallback))

                    logger.info(f"Final {len(valid_urls)} URLs")
                    return sorted(valid_urls)

    def validate_environment(self) -> bool:
        """Validate that all required environment variables are set."""
        required_vars = ['COHERE_API_KEY']
        missing_vars = [var for var in required_vars if not os.getenv(var)]

        if missing_vars:
            logger.error(f"Missing required environment variables: {missing_vars}")
            return False

        return True

    def get_sitemap_urls(self) -> List[str]:
        """Get all URLs from the sitemap.xml file."""
        sitemap_url = urljoin(self.target_url, 'sitemap.xml')
        logger.info(f"Fetching sitemap from: {sitemap_url}")

        try:
            response = requests.get(sitemap_url, timeout=30)
            response.raise_for_status()

            root = ET.fromstring(response.content)
            urls = []

            # Handle different sitemap namespace formats
            for url_element in root.findall('.//{http://www.sitemaps.org/schemas/sitemap/0.9}url'):
                loc_element = url_element.find('{http://www.sitemaps.org/schemas/sitemap/0.9}loc')
                if loc_element is not None:
                    url = loc_element.text
                    if url:
                        # Normalize both URLs for comparison
                        normalized_url = url.lower().rstrip('/')
                        normalized_target = self.target_url.lower().rstrip('/')

                        # Check if URL contains target domain (for placeholder sitemaps)
                        if normalized_target.replace('https://', '').replace('http://', '') in normalized_url:
                            # Replace placeholder domain with actual target domain
                            actual_url = url.replace(
                                url.split('/')[2],  # Extract domain from URL
                                self.target_url.replace('https://', '').replace('http://', '').rstrip('/')
                            ) if 'your-docusaurus-site.example.com' in url else url

                            urls.append(actual_url)
                        elif url.startswith(self.target_url):
                            urls.append(url)

            # If no URLs found with namespace, try without namespace
            if not urls:
                for url_element in root.findall('.//url'):
                    loc_element = url_element.find('loc')
                    if loc_element is not None:
                        url = loc_element.text
                        if url:
                            # Normalize both URLs for comparison
                            normalized_url = url.lower().rstrip('/')
                            normalized_target = self.target_url.lower().rstrip('/')

                            # Check if URL contains target domain (for placeholder sitemaps)
                            if normalized_target.replace('https://', '').replace('http://', '') in normalized_url:
                                # Replace placeholder domain with actual target domain
                                actual_url = url.replace(
                                    url.split('/')[2],  # Extract domain from URL
                                    self.target_url.replace('https://', '').replace('http://', '').rstrip('/')
                                ) if 'your-docusaurus-site.example.com' in url else url

                                urls.append(actual_url)
                            elif url.startswith(self.target_url):
                                urls.append(url)

            logger.info(f"Found {len(urls)} URLs in sitemap")
            if len(urls) == 0:
                logger.info("No matching URLs found in sitemap, using fallback URLs")
                return [urljoin(self.target_url, path) for path in self.fallback_urls]

            return urls

        except requests.RequestException as e:
            logger.warning(f"Could not fetch sitemap: {e}")
            logger.info("Using fallback URLs instead")
            return [urljoin(self.target_url, path) for path in self.fallback_urls]
        except ET.ParseError:
            logger.warning("Could not parse sitemap XML")
            logger.info("Using fallback URLs instead")
            return [urljoin(self.target_url, path) for path in self.fallback_urls]

    def extract_text_from_url(self, url: str) -> Optional[Dict]:
        """Extract clean text content from a URL with Docusaurus-specific selectors."""
        try:
            logger.info(f"Extracting content from: {url}")
            response = requests.get(url, timeout=30)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, 'html.parser')

            # Remove navigation, headers, footers, and other non-content elements
            for element in soup(['nav', 'header', 'footer', 'aside']):
                element.decompose()

            # Remove specific Docusaurus elements that are not content
            for element in soup.find_all(class_=re.compile(r'navbar|menu|toc|pagination|footer')):
                element.decompose()

            # Look for main content areas in Docusaurus sites
            content_selectors = [
                'article',  # Common for articles
                '[role="main"]',  # ARIA main role
                '.main-wrapper',  # Common wrapper
                '.container',  # Container classes
                '.theme-doc-markdown',  # Docusaurus-specific
                '.markdown',  # Markdown content
                '.doc-content',  # Documentation content
                '.docs-content',  # Alternative documentation class
                '.content',  # Generic content class
                '.docItemContainer',  # Docusaurus doc item container
                '.theme-doc-content',  # Docusaurus theme content
                '.theme-edit-this-page',  # Page editing links
                '.theme-last-updated',  # Last updated info
                '.theme-admonition',  # Admonition blocks
                '.codeBlockContainer',  # Code blocks
            ]

            content_element = None
            for selector in content_selectors:
                content_element = soup.select_one(selector)
                if content_element:
                    break

            # If no content found with selectors, try common article selectors
            if not content_element:
                content_element = soup.find('main') or soup.find('div', class_=re.compile(r'content|main|doc'))

            # If still no content found, use body
            if not content_element:
                content_element = soup.find('body')

            if content_element:
                # Extract text content
                text = content_element.get_text(separator=' ', strip=True)

                # Clean up excessive whitespace
                text = re.sub(r'\s+', ' ', text)

                # Get page title
                title_element = soup.find('title')
                title = title_element.get_text().strip() if title_element else 'No Title'

                # Extract module and section information from URL
                parsed_url = urlparse(url)
                path_parts = [part for part in parsed_url.path.split('/') if part]

                module = "General"
                section = "Overview"
                hierarchy_path = "General/Overview"

                # Try to extract module information from URL
                for part in path_parts:
                    if part in self.module_mapping:
                        module = self.module_mapping[part]
                        section = "Overview"
                        hierarchy_path = f"{module}/{section}"
                        break

                # More specific module extraction
                if 'intro' in url:
                    module = 'Introduction'
                    hierarchy_path = 'Introduction/Overview'
                elif 'week1-2' in url:
                    module = 'Week 1-2: Introduction to Physical AI'
                    hierarchy_path = 'Week 1-2/Overview'
                elif 'week3-5' in url:
                    module = 'Week 3-5: ROS2 and Navigation'
                    hierarchy_path = 'Week 3-5/Overview'
                elif 'week6-7' in url:
                    module = 'Week 6-7: Simulation Environments'
                    hierarchy_path = 'Week 6-7/Overview'
                elif 'week8-10' in url:
                    module = 'Week 8-10: Isaac Gym and Control'
                    hierarchy_path = 'Week 8-10/Overview'
                elif 'week11-12' in url:
                    module = 'Week 11-12: Humanoid Locomotion'
                    hierarchy_path = 'Week 11-12/Overview'
                elif 'week13' in url:
                    module = 'Week 13: VLA and Advanced Topics'
                    hierarchy_path = 'Week 13/Overview'
                elif 'capstone' in url:
                    module = 'Capstone Project'
                    hierarchy_path = 'Capstone/Overview'
                elif 'references' in url:
                    module = 'References'
                    hierarchy_path = 'References/Overview'

                # Extract section from headings if available
                heading = soup.find(['h1', 'h2', 'h3'])
                if heading:
                    section = heading.get_text().strip()
                    hierarchy_path = f"{module}/{section}"

                return {
                    'url': url,
                    'title': title,
                    'text': text,
                    'module': module,
                    'section': section,
                    'hierarchy_path': hierarchy_path,
                    'word_count': len(text.split())
                }
            else:
                logger.warning(f"No content found for URL: {url}")
                return None

        except requests.RequestException as e:
            logger.error(f"Failed to fetch URL {url}: {e}")
            return None
        except Exception as e:
            logger.error(f"Error extracting content from {url}: {e}")
            return None

    def chunk_text(self, content: Dict) -> List[Dict]:
        """Split content into meaningful chunks preserving module/section hierarchy."""
        text = content['text']
        max_chunk_size = 1000  # characters
        overlap = 100  # characters

        if len(text) <= max_chunk_size:
            # If content is small enough, return as single chunk
            return [{
                'id': str(uuid.uuid4()),
                'text': text,
                'url': content['url'],
                'title': content['title'],
                'module': content['module'],
                'section': content['section'],
                'hierarchy_path': content['hierarchy_path'],
                'word_count': len(text.split()),
                'created_at': datetime.utcnow().isoformat()
            }]

        # Split content into chunks
        chunks = []
        start = 0

        while start < len(text):
            end = start + max_chunk_size

            # Try to break at sentence boundary
            if end < len(text):
                # Look for sentence endings near the boundary
                sentence_end = text.rfind('.', start, end)
                if sentence_end > start + max_chunk_size // 2:  # Only if it's reasonably close
                    end = sentence_end + 1
                else:
                    # Look for paragraph breaks
                    paragraph_end = text.rfind('\n\n', start, end)
                    if paragraph_end > start + max_chunk_size // 2:
                        end = paragraph_end
                    else:
                        # Just break at the character limit
                        pass

            chunk_text = text[start:end].strip()
            if chunk_text and len(chunk_text) > 50:  # Only add substantial chunks
                chunks.append({
                    'id': str(uuid.uuid4()),
                    'text': chunk_text,
                    'url': content['url'],
                    'title': content['title'],
                    'module': content['module'],
                    'section': content['section'],
                    'hierarchy_path': content['hierarchy_path'],
                    'word_count': len(chunk_text.split()),
                    'created_at': datetime.utcnow().isoformat()
                })

            start = end - overlap if end < len(text) else end

        return chunks

    def embed(self, chunks: List[Dict]) -> List[Dict]:
        """Generate embeddings for content chunks using Cohere."""
        if not chunks:
            return []

        # Extract text for embedding
        texts = [chunk['text'] for chunk in chunks]

        try:
            # Generate embeddings using Cohere
            response = self.cohere_client.embed(
                texts=texts,
                model='embed-english-v3.0',
                input_type='search_document'
            )

            embeddings = response.embeddings

            # Add embeddings to chunks
            for i, chunk in enumerate(chunks):
                chunk['embedding'] = embeddings[i]
                chunk['model_name'] = 'embed-english-v3.0'
                chunk['model_version'] = '3.0'
                chunk['embedding_created_at'] = datetime.utcnow().isoformat()

            logger.info(f"Generated embeddings for {len(chunks)} chunks")
            return chunks

        except Exception as e:
            logger.error(f"Error generating embeddings: {e}")
            # Return chunks without embeddings if embedding fails
            for chunk in chunks:
                chunk['embedding'] = None
                chunk['model_name'] = 'embed-english-v3.0'
                chunk['model_version'] = '3.0'
                chunk['embedding_created_at'] = datetime.utcnow().isoformat()
            return chunks

    def create_collection(self):
        """Create Qdrant collection with appropriate schema."""
        try:
            # Check if collection already exists
            collections = self.qdrant_client.get_collections()
            collection_exists = any(col.name == self.collection_name for col in collections.collections)

            if collection_exists:
                logger.info(f"Collection '{self.collection_name}' already exists")
                return

            # Create collection with 1024-dimensional vectors (Cohere embed-english-v3.0)
            self.qdrant_client.create_collection(
                collection_name=self.collection_name,
                vectors_config=models.VectorParams(
                    size=1024,  # Cohere embed-english-v3.0 dimension
                    distance=models.Distance.COSINE
                ),
                hnsw_config=models.HnswConfigDiff(
                    m=16,
                    ef_construct=128
                )
            )

            # Create payload indexes for metadata fields
            self.qdrant_client.create_payload_index(
                collection_name=self.collection_name,
                field_name="url",
                field_schema=models.PayloadSchemaType.KEYWORD
            )

            self.qdrant_client.create_payload_index(
                collection_name=self.collection_name,
                field_name="module",
                field_schema=models.PayloadSchemaType.KEYWORD
            )

            self.qdrant_client.create_payload_index(
                collection_name=self.collection_name,
                field_name="section",
                field_schema=models.PayloadSchemaType.KEYWORD
            )

            self.qdrant_client.create_payload_index(
                collection_name=self.collection_name,
                field_name="hierarchy_path",
                field_schema=models.PayloadSchemaType.KEYWORD
            )

            logger.info(f"Created collection '{self.collection_name}' with 1024-dimensional vectors")

        except Exception as e:
            logger.error(f"Error creating collection: {e}")
            raise

    def save_chunks_to_qdrant(self, chunks: List[Dict]):
        """Save content chunks with embeddings to Qdrant."""
        if not chunks:
            return

        # Prepare points for Qdrant
        points = []
        for chunk in chunks:
            if chunk.get('embedding') is not None:
                point = models.PointStruct(
                    id=chunk['id'],
                    vector=chunk['embedding'],
                    payload={
                        'text': chunk['text'],
                        'url': chunk['url'],
                        'title': chunk['title'],
                        'module': chunk['module'],
                        'section': chunk['section'],
                        'hierarchy_path': chunk['hierarchy_path'],
                        'word_count': chunk['word_count'],
                        'created_at': chunk['created_at'],
                        'model_name': chunk['model_name'],
                        'model_version': chunk['model_version'],
                        'embedding_created_at': chunk['embedding_created_at']
                    }
                )
                points.append(point)

        if points:
            try:
                # Batch upload to Qdrant (max 100 points per batch)
                batch_size = 100
                for i in range(0, len(points), batch_size):
                    batch = points[i:i + batch_size]
                    self.qdrant_client.upsert(
                        collection_name=self.collection_name,
                        points=batch
                    )
                    logger.info(f"Uploaded batch of {len(batch)} points to Qdrant")

                logger.info(f"Successfully saved {len(points)} chunks to Qdrant collection '{self.collection_name}'")
            except Exception as e:
                logger.error(f"Error saving chunks to Qdrant: {e}")
                raise
        else:
            logger.warning("No chunks with valid embeddings to save to Qdrant")

    def ingest_book(self):
        """Main orchestration function to process the entire book."""
        logger.info("Starting book ingestion process...")

        # Get all URLs
        urls = self.get_sitemap_urls()
        logger.info(f"Processing {len(urls)} URLs")

        processed_count = 0
        successful_chunks_count = 0
        failed_pages_count = 0
        total_words_processed = 0

        # Process each URL
        for url in tqdm(urls, desc="Processing URLs"):
            try:
                # Respect rate limits - add delay between requests
                time.sleep(1)  # 1 second delay to be respectful

                # Extract content from URL
                content = self.extract_text_from_url(url)
                if content is None:
                    failed_pages_count += 1
                    continue

                # Chunk the content
                chunks = self.chunk_text(content)

                # Generate embeddings
                embedded_chunks = self.embed(chunks)

                # Save to Qdrant
                self.save_chunks_to_qdrant(embedded_chunks)

                processed_count += 1
                successful_chunks_count += len(embedded_chunks)
                total_words_processed += content['word_count']

                logger.info(f"Processed URL: {url} - {len(embedded_chunks)} chunks")

            except Exception as e:
                logger.error(f"Error processing URL {url}: {e}")
                failed_pages_count += 1
                continue

        # Log summary
        logger.info("="*50)
        logger.info("INGESTION SUMMARY")
        logger.info("="*50)
        logger.info(f"Pages processed successfully: {processed_count}")
        logger.info(f"Pages failed: {failed_pages_count}")
        logger.info(f"Total chunks created: {successful_chunks_count}")
        logger.info(f"Total words processed: {total_words_processed}")
        logger.info("="*50)

        return {
            'processed_pages_count': processed_count,
            'successful_chunks_count': successful_chunks_count,
            'failed_pages_count': failed_pages_count,
            'total_words_processed': total_words_processed
        }

    def run_test_search(self, query: str = "What is Physical AI?"):
        """Run a test search to verify the ingestion worked."""
        try:
            # Generate embedding for the query
            response = self.cohere_client.embed(
                texts=[query],
                model='embed-english-v3.0',
                input_type='search_query'
            )

            query_embedding = response.embeddings[0]

            # Search in Qdrant
            search_results = self.qdrant_client.search(
                collection_name=self.collection_name,
                query_vector=query_embedding,
                limit=3,
                with_payload=True
            )

            logger.info(f"Test search results for query: '{query}'")
            for i, result in enumerate(search_results):
                logger.info(f"Result {i+1}:")
                logger.info(f"  Score: {result.score}")
                logger.info(f"  Module: {result.payload.get('module', 'N/A')}")
                logger.info(f"  Section: {result.payload.get('section', 'N/A')}")
                logger.info(f"  URL: {result.payload.get('url', 'N/A')}")
                logger.info(f"  Text preview: {result.payload.get('text', '')[:100]}...")
                logger.info("")

            return search_results

        except Exception as e:
            logger.error(f"Error running test search: {e}")
            return []


def main():
    """Main entry point for the ingestion pipeline."""
    logger.info("Starting RAG Website Ingestion Pipeline")

    try:
        # Initialize the ingestor
        ingestor = RAGWebsiteIngestor()

        # Validate environment
        if not ingestor.validate_environment():
            logger.error("Environment validation failed")
            return

        # Create Qdrant collection
        ingestor.create_collection()

        # Run the ingestion process
        summary = ingestor.ingest_book()

        # Run a test search to verify
        logger.info("\nRunning test search to verify ingestion...")
        test_results = ingestor.run_test_search("What is Physical AI?")

        logger.info("Ingestion pipeline completed successfully!")

    except Exception as e:
        logger.error(f"Error in main pipeline: {e}")
        raise


if __name__ == "__main__":
    main()