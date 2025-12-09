# Querio API Documentation

A FastAPI-based PDF RAG (Retrieval Augmented Generation) system for querying PDF documents using AI.

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Set Up Environment

Create a `.env` file in the project root:

```env
GENAI_API_KEY=your_google_api_key_here
```

### 3. Run the API Server

```bash
cd src
python app.py
```

Or use uvicorn directly:

```bash
uvicorn app:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at:
- **API**: http://localhost:8000
- **Interactive Docs (Swagger)**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## API Endpoints

### Health & System

#### `GET /api/health`
Health check endpoint.

**Response:**
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "timestamp": "2024-01-10T12:00:00"
}
```

#### `GET /api/stats`
Get system statistics.

**Response:**
```json
{
  "total_documents": 5,
  "total_chunks": 150,
  "vector_db_size": "25.3 MB",
  "last_updated": "2024-01-10T11:30:00"
}
```

---

### Documents

#### `POST /api/documents/upload`
Upload a single PDF document.

**Request:**
- **Content-Type**: `multipart/form-data`
- **Body**: `file` (PDF file)

**Response:**
```json
{
  "id": "uuid-here",
  "filename": "document.pdf",
  "file_size": 1024000,
  "page_count": 10,
  "uploaded_at": "2024-01-10T12:00:00",
  "processed": false
}
```

**Example (cURL):**
```bash
curl -X POST "http://localhost:8000/api/documents/upload" \
  -H "accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@document.pdf"
```

#### `POST /api/documents/bulk-upload`
Upload multiple PDF documents.

**Request:**
- **Content-Type**: `multipart/form-data`
- **Body**: `files` (multiple PDF files)

**Response:** Array of document metadata

#### `GET /api/documents`
List all uploaded documents.

**Response:**
```json
{
  "documents": [...],
  "total": 5
}
```

#### `GET /api/documents/{document_id}`
Get specific document metadata.

**Response:** Single document metadata object

#### `DELETE /api/documents/{document_id}`
Delete a document.

**Response:**
```json
{
  "success": true,
  "message": "Document deleted successfully",
  "document_id": "uuid-here"
}
```

#### `POST /api/documents/process`
Process all documents and rebuild vector database.

**Request:**
```json
{
  "force": false
}
```

**Response:**
```json
{
  "success": true,
  "message": "Documents processed successfully",
  "documents_processed": 5,
  "chunks_created": 150
}
```

---

### Query

#### `POST /api/query`
Ask a question about your documents.

**Request:**
```json
{
  "query": "What is the main topic of the documents?",
  "k": 3
}
```

**Response:**
```json
{
  "query": "What is the main topic?",
  "answer": "The main topic is...",
  "sources": [
    {
      "content": "relevant text chunk",
      "metadata": {}
    }
  ],
  "processing_time": 1.23
}
```

**Example (cURL):**
```bash
curl -X POST "http://localhost:8000/api/query" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What is machine learning?",
    "k": 3
  }'
```

---

### Chat

#### `POST /api/chat`
Have a conversation with context.

**Request:**
```json
{
  "message": "Tell me more about that",
  "session_id": "optional-session-id",
  "k": 3
}
```

**Response:**
```json
{
  "session_id": "uuid-here",
  "message": "Tell me more",
  "answer": "Based on the documents...",
  "sources": [...],
  "processing_time": 1.45
}
```

#### `GET /api/chat/sessions`
List all chat sessions.

**Response:**
```json
[
  {
    "session_id": "uuid",
    "created_at": "2024-01-10T12:00:00",
    "updated_at": "2024-01-10T12:05:00",
    "message_count": 5
  }
]
```

#### `POST /api/chat/sessions`
Create a new chat session.

**Response:** Session metadata

#### `GET /api/chat/sessions/{session_id}`
Get specific session details.

#### `DELETE /api/chat/sessions/{session_id}`
Delete a chat session.

#### `GET /api/chat/sessions/{session_id}/history`
Get conversation history.

**Response:**
```json
{
  "session_id": "uuid",
  "messages": [
    {
      "role": "user",
      "content": "Hello",
      "timestamp": "2024-01-10T12:00:00"
    },
    {
      "role": "assistant",
      "content": "Hi there!",
      "timestamp": "2024-01-10T12:00:01"
    }
  ],
  "created_at": "2024-01-10T12:00:00",
  "updated_at": "2024-01-10T12:05:00"
}
```

---

### Search

#### `POST /api/search`
Semantic search without generating an answer.

**Request:**
```json
{
  "query": "machine learning",
  "k": 5
}
```

**Response:**
```json
{
  "query": "machine learning",
  "results": [
    {
      "content": "text chunk about ML",
      "metadata": {},
      "score": null
    }
  ],
  "total": 5
}
```

#### `POST /api/search/similar`
Find similar content.

Same request/response format as `/api/search`

---

## Usage Examples

### Python Client

```python
import requests

BASE_URL = "http://localhost:8000"

# Upload a document
with open("document.pdf", "rb") as f:
    files = {"file": f}
    response = requests.post(f"{BASE_URL}/api/documents/upload", files=files)
    print(response.json())

# Process documents
response = requests.post(f"{BASE_URL}/api/documents/process")
print(response.json())

# Query
data = {"query": "What is the main topic?", "k": 3}
response = requests.post(f"{BASE_URL}/api/query", json=data)
print(response.json()["answer"])

# Chat
data = {"message": "Hello, tell me about the documents"}
response = requests.post(f"{BASE_URL}/api/chat", json=data)
session_id = response.json()["session_id"]
print(response.json()["answer"])

# Continue conversation
data = {"message": "Tell me more", "session_id": session_id}
response = requests.post(f"{BASE_URL}/api/chat", json=data)
print(response.json()["answer"])
```

### JavaScript/Fetch

```javascript
// Upload document
const formData = new FormData();
formData.append('file', fileInput.files[0]);

fetch('http://localhost:8000/api/documents/upload', {
  method: 'POST',
  body: formData
})
  .then(res => res.json())
  .then(data => console.log(data));

// Query
fetch('http://localhost:8000/api/query', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    query: 'What is AI?',
    k: 3
  })
})
  .then(res => res.json())
  .then(data => console.log(data.answer));
```

## Error Handling

All endpoints return appropriate HTTP status codes:

- **200**: Success
- **400**: Bad Request (validation error)
- **404**: Not Found
- **500**: Internal Server Error

Error response format:
```json
{
  "error": "Error message",
  "detail": "Detailed error information",
  "timestamp": "2024-01-10T12:00:00"
}
```

## CORS

CORS is enabled for all origins by default. In production, configure specific origins in `app.py`:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://yourdomain.com"],
    ...
)
```

## Rate Limiting

Currently no rate limiting is implemented. Consider adding rate limiting middleware for production use.

## Authentication

No authentication is currently implemented. For production:

1. Add JWT or API key authentication
2. Implement user management
3. Add role-based access control

## Performance Tips

1. **Batch uploads**: Use `/api/documents/bulk-upload` for multiple files
2. **Adjust k parameter**: Lower k = faster responses, higher k = more context
3. **Vector store caching**: Vector store is loaded on startup and cached
4. **Session management**: Reuse chat sessions to maintain conversation context

## Troubleshooting

### Vector store not initialized
Run `/api/documents/process` after uploading documents.

### Slow responses
- Reduce the `k` parameter
- Check network latency to Google AI API
- Ensure sufficient system resources

### Upload failures
- Check file is valid PDF
- Ensure file size is reasonable
- Verify write permissions to data folder

## Development

### Project Structure
```
src/
├── api/
│   ├── routes/        # API endpoints
│   ├── models.py      # Pydantic models
│   ├── services.py    # Business logic
│   └── dependencies.py
├── app.py            # FastAPI application
├── config.py         # Configuration
├── pdf_handler.py    # PDF processing
├── text_splitter.py  # Text chunking
├── vector_store.py   # Vector database
└── rag_pipeline.py   # RAG logic
```

### Adding New Endpoints

1. Define models in `api/models.py`
2. Add business logic to `api/services.py`
3. Create route in `api/routes/`
4. Include router in `app.py`

## Production Deployment

### Using Docker (recommended)

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY ../requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY ../src ./src/
COPY ../.env .

EXPOSE 8000
CMD ["uvicorn", "src.app:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Using systemd

```ini
[Unit]
Description=Querio API
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/path/to/querio
ExecStart=/path/to/venv/bin/uvicorn src.app:app --host 0.0.0.0 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
```

## License

MIT License
