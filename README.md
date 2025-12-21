# Physical AI & Humanoid Robotics Course Book with RAG Chatbot

A comprehensive educational platform featuring a Docusaurus-based textbook on Physical AI & Humanoid Robotics, powered by a Retrieval-Augmented Generation (RAG) chatbot for interactive learning.

## 🎯 Project Overview

This unified project delivers:

1. **📚 Interactive Textbook**: Complete 13-week course on Physical AI & Humanoid Robotics built with Docusaurus
2. **🤖 RAG Chatbot**: AI assistant that answers questions about course content using vector search and OpenAI
3. **🔄 Content Pipeline**: Automated ingestion system that extracts and vectorizes textbook content
4. **🌐 Web Integration**: Embedded chatbot component accessible on all textbook pages

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    Physical AI & Robotics Platform               │
├─────────────────────────────────────────────────────────────────┤
│  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────┐  │
│  │   Docusaurus    │    │   FastAPI       │    │   Qdrant    │  │
│  │   Textbook      │◄──►│   Chatbot API   │◄──►│   Vector DB  │  │
│  │                 │    │                 │    │             │  │
│  └─────────────────┘    └─────────────────┘    └─────────────┘  │
│         │                        │                    │         │
│         ▼                        ▼                    ▼         │
│  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────┐  │
│  │   React Chat    │    │   OpenAI GPT    │    │   Cohere    │  │
│  │   Component     │    │   Responses     │    │   Embeddings │  │
│  │                 │    │                 │    │             │  │
│  └─────────────────┘    └─────────────────┘    └─────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

## 🚀 Quick Start

### Prerequisites

- **Python 3.11+** with pip
- **Node.js 20+** with npm
- **Git** for version control
- API Keys:
  - [Cohere API Key](https://dashboard.cohere.ai/api-keys)
  - [Qdrant Cloud Account](https://cloud.qdrant.io/)
  - [OpenAI API Key](https://platform.openai.com/api-keys)

### 1. Clone and Setup

```bash
git clone <repository-url>
cd AI-Humanoid-Robotics-Course-Book
```

### 2. Backend Setup (RAG Pipeline & API)

```bash
cd backend

# Install Python dependencies
pip install -r requirements.txt

# Configure environment variables
cp .env.example .env
# Edit .env with your API keys
```

### 3. Content Ingestion

```bash
# Run the ingestion pipeline to populate the vector database
python main.py
```

### 4. Start Chatbot API

```bash
# Start the FastAPI server
python chatbot_api.py
```

The API will be available at `http://localhost:8000`

### 5. Frontend Setup (Docusaurus)

```bash
cd ../docs

# Install Node.js dependencies
npm install

# Start development server
npm start
```

The textbook will be available at `http://localhost:3000`

## 📖 Usage

### For Students

1. **Browse the Textbook**: Navigate through the 13-week course content
2. **Ask Questions**: Click the "💬 Ask AI" button in the bottom-right corner
3. **Select Text**: Highlight any text on the page to ask specific questions about it
4. **Get Answers**: Receive AI-powered responses with source citations

### For Educators

1. **Content Management**: Update course content in the `docs/` directory
2. **Re-ingest Content**: Run the ingestion pipeline to update the knowledge base
3. **Monitor Usage**: Check API logs and conversation history

## 🔧 Configuration

### Environment Variables

Create a `.env` file in the `backend/` directory:

```env
# Cohere API for embeddings
COHERE_API_KEY=your_cohere_key

# Qdrant Cloud for vector storage
QDRANT_URL=https://your-cluster.qdrant.io
QDRANT_API_KEY=your_qdrant_key

# OpenAI for chatbot responses
OPENAI_API_KEY=your_openai_key

# Collection settings
COLLECTION_NAME=physical_ai_humanoid_textbook
```

### Customization

- **Chunk Size**: Modify `chunk_size` in `main.py` (default: 1000 characters)
- **Embedding Model**: Change model in `chatbot_api.py` (default: embed-english-v3.0)
- **Chatbot Personality**: Update system prompt in `RAGChatbot.generate_response()`

## 🛠️ Development

### Project Structure

```
AI-Humanoid-Robotics-Course-Book/
├── backend/                 # Python RAG pipeline and API
│   ├── main.py             # Content ingestion pipeline
│   ├── chatbot_api.py      # FastAPI chatbot server
│   ├── requirements.txt    # Python dependencies
│   └── .env               # Environment configuration
├── docs/                   # Docusaurus textbook
│   ├── src/
│   │   ├── components/
│   │   │   └── Chatbot/    # React chatbot component
│   │   └── theme/
│   │       └── Root.tsx    # Chatbot integration
│   ├── docusaurus.config.ts
│   └── package.json
└── specs/                  # Project specifications
```

### API Endpoints

- `POST /chat` - Send messages to chatbot
- `GET /health` - Service health check
- `GET /conversations/{id}` - Get conversation history
- `DELETE /conversations/{id}` - Delete conversation

### Adding New Content

1. Add content to `docs/docs/` directory
2. Update `docs/sidebars.ts` if needed
3. Re-run the ingestion pipeline: `python backend/main.py`

## 📊 Features

### 🤖 Intelligent Chatbot
- **Context-Aware**: Uses selected text as additional context
- **Source Citations**: Provides references to textbook sections
- **Conversation Memory**: Maintains context across messages
- **Module Filtering**: Can focus on specific course modules

### 📚 Rich Textbook Content
- **13-Week Structure**: Comprehensive learning progression
- **Interactive Elements**: Code examples, diagrams, and exercises
- **Modern UI**: Docusaurus-powered responsive design
- **Search Integration**: Built-in search with Algolia (optional)

### 🔄 Automated Pipeline
- **Smart Extraction**: Docusaurus-aware content parsing
- **Semantic Chunking**: Maintains educational context
- **Vector Embeddings**: High-quality semantic representations
- **Cloud Storage**: Scalable vector database in Qdrant Cloud

## 🚀 Deployment

### Backend Deployment

```bash
# Build and deploy FastAPI app
# (Use your preferred hosting: Railway, Render, Heroku, etc.)
```

### Frontend Deployment

```bash
cd docs
npm run build
npm run deploy  # Deploys to GitHub Pages
```

### Production Considerations

- Set up proper CORS configuration
- Implement rate limiting
- Add authentication if needed
- Monitor API usage and costs
- Set up database backups

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- Built with [Docusaurus](https://docusaurus.io/)
- Powered by [Cohere](https://cohere.ai/) embeddings
- Chat functionality via [OpenAI](https://openai.com/)
- Vector storage with [Qdrant](https://qdrant.tech/)

## 📞 Support

For questions or issues:
- Check the [Issues](../../issues) page
- Review the documentation in `specs/`
- Contact the maintainers

---

**Happy Learning! 🚀🤖**