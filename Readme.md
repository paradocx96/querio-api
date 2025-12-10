# Querio - RAG API

<div align="center">

![Python](https://img.shields.io/badge/python-3.10+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115.6-009688.svg)
![LangChain](https://img.shields.io/badge/LangChain-0.3.13-green.svg)
![License](https://img.shields.io/badge/license-MIT-blue.svg)

**A powerful PDF-based Retrieval Augmented Generation (RAG) API built with FastAPI, LangChain, and Google Gemini**

[Features](#features) •
[Quick Start](#quick-start) •
[API Documentation](#api-documentation) •
[Development](#development) •
[Deployment](#deployment)

</div>

---

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Architecture](#architecture)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [API Documentation](#api-documentation)
- [Configuration](#configuration)
- [Project Structure](#project-structure)
- [Usage Examples](#usage-examples)
- [Development](#development)
- [Testing](#testing)
- [Deployment](#deployment)
- [Contributing](#contributing)
- [Troubleshooting](#troubleshooting)
- [License](#license)
- [Acknowledgments](#acknowledgments)

---

## 🎯 Overview

Querio is a production-ready RESTful API that enables intelligent question-answering over PDF documents using Retrieval Augmented Generation (RAG). Built on modern AI technologies, it provides a robust backend for building knowledge-based applications with natural language interfaces.

### Why Querio?

- 🚀 **Fast & Efficient**: Optimized vector search with ChromaDB
- 🔒 **Production Ready**: Complete with error handling, validation, and comprehensive API docs
- 🎨 **Frontend Ready**: CORS-enabled REST API perfect for web/mobile frontends
- 📚 **Multi-Document**: Process and query across multiple PDF documents
- 💬 **Conversational**: Session-based chat with context retention
- 🔍 **Semantic Search**: Advanced vector similarity search
- 📊 **Scalable**: Built with async FastAPI for high performance

---

## ✨ Features

### Core Functionality

- **Document Management**
  - Upload single or multiple PDF files
  - Automatic text extraction and processing
  - Document metadata tracking
  - Delete and manage documents

- **Intelligent Querying**
  - RAG-based question answering
  - Context-aware responses using Google Gemini
  - Configurable retrieval parameters
  - Source attribution

- **Conversational AI**
  - Session-based chat conversations
  - Message history tracking
  - Multi-session support
  - Context retention across messages

- **Semantic Search**
  - Vector similarity search
  - Find similar content
  - Retrieve relevant document chunks
  - No LLM overhead for pure search

### Technical Features

- ⚡ **Async API**: Built with FastAPI for high concurrency
- 📖 **Auto Documentation**: Interactive Swagger UI and ReDoc
- 🔐 **Type Safety**: Pydantic models for request/response validation
- 🎯 **Error Handling**: Comprehensive exception handling and logging
- 🌐 **CORS Support**: Ready for browser-based frontends
- 📈 **Health Monitoring**: Health check and statistics endpoints
- 🔄 **Hot Reload**: Development server with auto-reload

---

## 🏗️ Architecture

```
┌─────────────┐      ┌──────────────┐      ┌─────────────┐
│   Client    │────▶ │  FastAPI     │────▶ │  Google     │
│ Application │      │  REST API    │      │  Gemini AI  │
└─────────────┘      └──────────────┘      └─────────────┘
                            │
                            ▼
                     ┌──────────────┐
                     │  Document    │
                     │  Service     │
                     └──────────────┘
                            │
                            ▼
                     ┌──────────────┐      ┌─────────────┐
                     │  Vector      │────▶ │  ChromaDB   │
                     │  Store       │      │  (Local)    │
                     └──────────────┘      └─────────────┘
                            │
                            ▼
                     ┌──────────────┐
                     │  HuggingFace │
                     │  Embeddings  │
                     └──────────────┘
```

### Technology Stack

- **Framework**: FastAPI 0.115.6
- **LLM**: Google Gemini Pro
- **Embeddings**: HuggingFace (sentence-transformers)
- **Vector DB**: ChromaDB 0.5.23
- **PDF Processing**: PyMuPDF (fitz)
- **Text Splitting**: LangChain Text Splitters
- **Orchestration**: LangChain 0.3.13

---

## 📦 Prerequisites

### System Requirements

- **Python**: 3.10 or higher (3.11+ recommended)
- **RAM**: Minimum 4GB (8GB+ recommended for large documents)
- **Storage**: ~2GB for dependencies + space for documents and vector DB

### API Keys

- **Google AI API Key**: Get from [Google AI Studio](https://makersuite.google.com/app/apikey)

---

## 🚀 Installation

### 1. Clone the Repository

```bash
git clone https://github.com/paradocx96/querio.git
cd querio
```

### 2. Create Virtual Environment

```bash
# Using venv
python -m venv querio-venv

# Activate on Windows
querio-venv\Scripts\activate

# Activate on macOS/Linux
source querio-venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Set Up Environment Variables

Create a `.env` file in the project root:

```bash
# .env
GENAI_API_KEY=your_google_api_key_here
```

### 5. Verify Installation

```bash
python --version  # Should be 3.10+
pip list | grep fastapi  # Verify FastAPI is installed
```

---

## ⚡ Quick Start

### Start the API Server

```bash
cd src
python app.py
```

The server will start on `http://localhost:8000`

### Access the Documentation

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/api/health

### Basic Workflow

1. **Upload a PDF Document**
   ```bash
   curl -X POST "http://localhost:8000/api/documents/upload" \
     -F "file=@your_document.pdf"
   ```

2. **Process Documents**
   ```bash
   curl -X POST "http://localhost:8000/api/documents/process"
   ```

3. **Ask a Question**
   ```bash
   curl -X POST "http://localhost:8000/api/query" \
     -H "Content-Type: application/json" \
     -d '{"query": "What is the main topic?", "k": 3}'
   ```

---

## 📚 API Documentation

### Base URL
```
http://localhost:8000
```

### Endpoints Overview

| Category | Endpoint | Method | Description |
|----------|----------|--------|-------------|
| **System** | `/api/health` | GET | Health check |
| **System** | `/api/stats` | GET | System statistics |
| **Documents** | `/api/documents/upload` | POST | Upload PDF |
| **Documents** | `/api/documents` | GET | List all documents |
| **Documents** | `/api/documents/{id}` | GET | Get document details |
| **Documents** | `/api/documents/{id}` | DELETE | Delete document |
| **Documents** | `/api/documents/process` | POST | Process documents |
| **Query** | `/api/query` | POST | Ask a question |
| **Chat** | `/api/chat` | POST | Send chat message |
| **Chat** | `/api/chat/sessions` | GET | List chat sessions |
| **Chat** | `/api/chat/sessions` | POST | Create session |
| **Chat** | `/api/chat/sessions/{id}` | GET | Get session |
| **Chat** | `/api/chat/sessions/{id}` | DELETE | Delete session |
| **Chat** | `/api/chat/sessions/{id}/history` | GET | Get chat history |
| **Search** | `/api/search` | POST | Semantic search |
| **Search** | `/api/search/similar` | POST | Find similar content |

### Interactive Documentation

Visit `http://localhost:8000/docs` for:
- Try out endpoints directly
- See request/response schemas
- Test authentication
- View example payloads

For detailed API documentation, see [API_DOCUMENTATION.md](docs/API_DOCUMENTATION.md)

---

## ⚙️ Configuration

### Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `GENAI_API_KEY` | Yes | - | Google AI API key |
| `PDF_FOLDER` | No | `data` | PDF storage directory |
| `CHROMA_DB` | No | `chroma_db` | Vector DB directory |

### Application Settings

Edit `src/config.py` to customize:

```python
class Settings:
    GENAI_API_KEY = os.getenv("GENAI_API_KEY")
    PDF_FOLDER = "data"
    CHROMA_DB = "chroma_db"
```

### Server Configuration

Modify `src/app.py` for:
- CORS origins
- Server host/port
- API metadata
- Middleware

---

## 📁 Project Structure

```
querio/
├── src/
│   ├── api/
│   │   ├── routes/
│   │   │   ├── __init__.py
│   │   │   ├── query.py           # Query endpoints
│   │   │   ├── chat.py            # Chat endpoints
│   │   │   ├── documents.py       # Document management
│   │   │   ├── search.py          # Search endpoints
│   │   │   └── system.py          # Health & stats
│   │   ├── __init__.py
│   │   ├── models.py              # Pydantic models
│   │   ├── services.py            # Business logic
│   │   └── dependencies.py        # Dependency injection
│   ├── app.py                     # FastAPI application
│   ├── config.py                  # Configuration
│   ├── pdf_handler.py             # PDF processing
│   ├── text_splitter.py           # Text chunking
│   ├── vector_store.py            # Vector DB operations
│   ├── rag_pipeline.py            # RAG logic
│   └── main.py                    # CLI interface (legacy)
├── data/                          # PDF storage
├── chroma_db/                     # Vector database
├── requirements.txt               # Dependencies
├── .env                           # Environment variables
└── README.md                      # This file
```

---

## 💡 Usage Examples

### Python Client

```python
import requests

BASE_URL = "http://localhost:8000"

# Upload document
with open("document.pdf", "rb") as f:
    files = {"file": f}
    response = requests.post(f"{BASE_URL}/api/documents/upload", files=files)
    print(f"Uploaded: {response.json()['filename']}")

# Process documents
response = requests.post(f"{BASE_URL}/api/documents/process")
print(f"Processed {response.json()['documents_processed']} documents")

# Query
data = {"query": "What is machine learning?", "k": 3}
response = requests.post(f"{BASE_URL}/api/query", json=data)
print(f"Answer: {response.json()['answer']}")

# Start a chat
data = {"message": "Hello, tell me about the documents"}
response = requests.post(f"{BASE_URL}/api/chat", json=data)
session_id = response.json()["session_id"]
print(f"Response: {response.json()['answer']}")

# Continue conversation
data = {"message": "Tell me more", "session_id": session_id}
response = requests.post(f"{BASE_URL}/api/chat", json=data)
print(f"Response: {response.json()['answer']}")
```

### JavaScript/Fetch

```javascript
// Upload document
const formData = new FormData();
formData.append('file', fileInput.files[0]);

const uploadResponse = await fetch('http://localhost:8000/api/documents/upload', {
  method: 'POST',
  body: formData
});
const uploadData = await uploadResponse.json();
console.log('Uploaded:', uploadData.filename);

// Process documents
await fetch('http://localhost:8000/api/documents/process', {
  method: 'POST'
});

// Query
const queryResponse = await fetch('http://localhost:8000/api/query', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    query: 'What is AI?',
    k: 3
  })
});
const queryData = await queryResponse.json();
console.log('Answer:', queryData.answer);
```

### cURL

```bash
# Upload document
curl -X POST "http://localhost:8000/api/documents/upload" \
  -F "file=@document.pdf"

# Process documents
curl -X POST "http://localhost:8000/api/documents/process"

# Query
curl -X POST "http://localhost:8000/api/query" \
  -H "Content-Type: application/json" \
  -d '{"query": "What is the main topic?", "k": 3}'

# Chat
curl -X POST "http://localhost:8000/api/chat" \
  -H "Content-Type: application/json" \
  -d '{"message": "Tell me about the documents"}'
```

---

## 🛠️ Development

### Development Setup

```bash
# Install in development mode
pip install -r requirements.txt

# Run with auto-reload
cd src
python app.py

# Or use uvicorn directly
uvicorn app:app --reload --host 0.0.0.0 --port 8000
```

### Code Style

```bash
# Format code with black
black src/

# Sort imports
isort src/

# Lint with flake8
flake8 src/
```

### Adding New Endpoints

1. Define Pydantic models in `src/api/models.py`
2. Add business logic to `src/api/services.py`
3. Create route file in `src/api/routes/`
4. Include router in `src/app.py`

Example:
```python
# src/api/routes/new_feature.py
from fastapi import APIRouter

router = APIRouter(prefix="/api/feature", tags=["Feature"])

@router.get("/")
async def get_feature():
    return {"message": "New feature"}

# src/app.py
from api.routes import new_feature
app.include_router(new_feature.router)
```

---

## 🧪 Testing

### Manual Testing

Use the interactive API documentation:
```
http://localhost:8000/docs
```

### API Testing

```bash
# Test health endpoint
curl http://localhost:8000/api/health

# Test stats
curl http://localhost:8000/api/stats

# Upload test document
curl -X POST http://localhost:8000/api/documents/upload \
  -F "file=@test.pdf"
```

### Load Testing

```bash
# Install Apache Bench
apt-get install apache2-utils

# Test with 100 requests, 10 concurrent
ab -n 100 -c 10 http://localhost:8000/api/health
```

---

## 🚢 Deployment

### Docker Deployment

Create `Dockerfile`:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY src/ ./src/
COPY .env .

# Create data directories
RUN mkdir -p data chroma_db

EXPOSE 8000

# Run application
CMD ["uvicorn", "src.app:app", "--host", "0.0.0.0", "--port", "8000"]
```

Build and run:
```bash
docker build -t querio-api .
docker run -p 8000:8000 -v $(pwd)/data:/app/data querio-api
```

### Docker Compose

Create `docker-compose.yml`:

```yaml
version: '3.8'

services:
  api:
    build: .
    ports:
      - "8000:8000"
    volumes:
      - ./data:/app/data
      - ./chroma_db:/app/chroma_db
    env_file:
      - .env
    restart: unless-stopped
```

Run with:
```bash
docker-compose up -d
```

### Production Deployment

#### Using Gunicorn + Uvicorn Workers

```bash
pip install gunicorn

gunicorn src.app:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000 \
  --timeout 120
```

#### Systemd Service

Create `/etc/systemd/system/querio.service`:

```ini
[Unit]
Description=Querio API Service
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/opt/querio
Environment="PATH=/opt/querio/venv/bin"
ExecStart=/opt/querio/venv/bin/uvicorn src.app:app --host 0.0.0.0 --port 8000
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl enable querio
sudo systemctl start querio
sudo systemctl status querio
```

#### Nginx Reverse Proxy

```nginx
server {
    listen 80;
    server_name api.yourdomain.com;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```

---

## 🤝 Contributing

Contributions are welcome! Please follow these guidelines:

### Getting Started

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Guidelines

- Follow PEP 8 style guide
- Add docstrings to all functions
- Update documentation for new features
- Write meaningful commit messages
- Test your changes before submitting

### Code of Conduct

- Be respectful and inclusive
- Provide constructive feedback
- Focus on what is best for the community
- Show empathy towards other contributors

---

## ❓ Troubleshooting

### Common Issues

#### Vector Store Not Initialized
```
Error: Vector store not initialized
```
**Solution**: Upload documents and run `/api/documents/process`

#### Import Errors
```
ModuleNotFoundError: No module named 'fastapi'
```
**Solution**: Ensure virtual environment is activated and dependencies are installed
```bash
pip install -r requirements.txt
```

#### Google API Key Error
```
Error: Failed to configure Google LLM
```
**Solution**: Check that `GENAI_API_KEY` is set in `.env` file

#### Port Already in Use
```
Error: Address already in use
```
**Solution**: Change port in `app.py` or kill process using port 8000
```bash
# Windows
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# Linux/Mac
lsof -i :8000
kill -9 <PID>
```

#### ChromaDB Errors
```
Failed to send telemetry event
```
**Solution**: These are harmless warnings. Update to latest version:
```bash
pip install -U langchain-chroma
```

### Getting Help

- 📖 Check the [API Documentation](docs/API_DOCUMENTATION.md)
- 💬 Open an [Issue](https://github.com/paradocx96/querio/issues)
- 📧 Contact: navindadev@gmail.com

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

```
MIT License

Copyright (c) 2025 Navinda Chandrasiri

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

---

## 🙏 Acknowledgments

### Built With

- [FastAPI](https://fastapi.tiangolo.com/) - Modern web framework
- [LangChain](https://www.langchain.com/) - LLM orchestration
- [Google Gemini](https://ai.google.dev/) - Large language model
- [ChromaDB](https://www.trychroma.com/) - Vector database
- [HuggingFace](https://huggingface.co/) - Embeddings models
- [PyMuPDF](https://pymupdf.readthedocs.io/) - PDF processing

### Inspiration

This project was inspired by the need for a production-ready RAG API that could be easily integrated into any application requiring intelligent document querying.

### Special Thanks

- The FastAPI community for excellent documentation
- LangChain team for RAG abstractions
- Google for providing Gemini API
- All contributors and users of this project

---

## 📞 Contact & Support

### Maintainer

**Your Name**
- GitHub: [@paradocx96](https://github.com/paradocx96)
- Email: navindadev@gmail.com
- LinkedIn: [Profile](https://www.linkedin.com/in/navinda-chandrasiri)

### Community

- 🐛 Report bugs via [GitHub Issues](https://github.com/paradocx96/querio/issues)
- 💡 Request features via [GitHub Discussions](https://github.com/paradocx96/querio/discussions)
- 📧 General inquiries: navindadev@gmail.com

### Star History

If you find this project helpful, please consider giving it a ⭐ on GitHub!

---

<div align="center">

**Made with ❤️ by developers, for developers**

[⬆ Back to Top](#querio---rag-api)

</div>
