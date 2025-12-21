# Data Model: RAG Website Ingestion and Vectorization Pipeline

## ContentChunk Entity

**Definition**: A segment of educational content extracted from the Physical AI & Humanoid Robotics Textbook website that maintains semantic coherence and context

**Fields**:
- `id` (string): Unique identifier for the chunk
- `text` (string): The actual text content of the chunk
- `url` (string): Source URL where the content was extracted from
- `title` (string): Page title from the source
- `module` (string): Module name in the 7-module learning program (e.g., "ROS2 Foundations", "Simulation", etc.)
- `section` (string): Section name within the module
- `topic` (string): Specific topic covered in the chunk
- `hierarchy_path` (string): Full path in the content hierarchy (e.g., "Module 1/ROS2 Foundations/Basic Concepts")
- `word_count` (integer): Number of words in the chunk
- `created_at` (datetime): Timestamp when chunk was created
- `embedding` (vector): Vector representation of the text content

**Validation Rules**:
- `text` must not be empty
- `url` must be a valid URL
- `module` must be one of: "ROS2 Foundations", "Simulation", "Hardware Basics", "VLA Foundations", "Advanced AI Control", "Humanoid Design", "Appendix"
- `word_count` must be > 0 and < 10000 (practical limits)

## SourceMetadata Entity

**Definition**: Information about the original location and context of content chunks

**Fields**:
- `source_url` (string): Original URL of the page
- `page_title` (string): Title of the source page
- `content_type` (string): Type of content (text, code, math, diagram)
- `docusaurus_sidebar_category` (string): Category from Docusaurus sidebar
- `docusaurus_tags` (array): Tags associated with the content in Docusaurus
- `module_path` (string): Module/section path (e.g., "docs/ros2/module-1-ros2-foundations")
- `last_modified` (datetime): Last modification date of source content
- `language` (string): Language of the content (default: "en")

**Validation Rules**:
- `source_url` must be a valid URL
- `content_type` must be one of: "text", "code", "math", "diagram", "mixed"
- `module_path` must follow the textbook structure pattern

## EmbeddingVector Entity

**Definition**: Numerical representation (1024 dimensions) of content chunk text that captures semantic meaning for similarity matching using Cohere embed-english-v3.0

**Fields**:
- `chunk_id` (string): Reference to the ContentChunk this embedding represents
- `vector` (array of floats): The actual embedding vector (1024 dimensions)
- `model_name` (string): Name of the model used to generate the embedding ("embed-english-v3.0")
- `model_version` (string): Version of the model used
- `embedding_created_at` (datetime): Timestamp when embedding was generated
- `module_info` (string): Module information preserved from chunk for retrieval context

**Validation Rules**:
- `vector` must have exactly 1024 dimensions (for embed-english-v3.0 model)
- `chunk_id` must reference an existing ContentChunk
- `model_name` must be "embed-english-v3.0"

## ProcessingPipeline Entity

**Definition**: Record of a complete run of the ingestion pipeline

**Fields**:
- `pipeline_id` (string): Unique identifier for this pipeline run
- `start_time` (datetime): When the pipeline started
- `end_time` (datetime): When the pipeline completed
- `status` (string): Current status (running, completed, failed, paused)
- `processed_pages_count` (integer): Number of pages processed
- `successful_chunks_count` (integer): Number of chunks successfully created
- `failed_pages_count` (integer): Number of pages that failed to process
- `total_words_processed` (integer): Total words processed in this run
- `checkpoint_urls` (array): List of URLs processed so far (for resume capability)
- `module_progress` (object): Tracking progress by module (e.g., {"ROS2 Foundations": "completed", "Simulation": "in_progress"})

**Validation Rules**:
- `status` must be one of: "running", "completed", "failed", "paused"
- `processed_pages_count` >= 0
- `successful_chunks_count` >= 0
- `module_progress` keys must be valid textbook modules