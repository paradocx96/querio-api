# Storage Recommendations for Querio RAG System

**Version:** 1.0
**Last Updated:** December 2024
**Author:** Querio Development Team

---

## Table of Contents

- [Overview](#overview)
- [Storage Architecture](#storage-architecture)
- [Storage Layers](#storage-layers)
  - [1. Raw PDF Storage](#1-raw-pdf-storage)
  - [2. Text Chunks Storage](#2-text-chunks-storage)
  - [3. Vector Embeddings Storage](#3-vector-embeddings-storage)
  - [4. Metadata Storage](#4-metadata-storage)
  - [5. Caching Layer](#5-caching-layer)
- [Architecture by Scale](#architecture-by-scale)
- [Optimization Strategies](#optimization-strategies)
- [Migration Path](#migration-path)
- [Cost Analysis](#cost-analysis)
- [Implementation Examples](#implementation-examples)
- [Best Practices](#best-practices)
- [Performance Benchmarks](#performance-benchmarks)

---

## Overview

This document provides comprehensive storage recommendations for the Querio PDF RAG (Retrieval Augmented Generation) system. Proper storage architecture is crucial for:

- **Performance**: Fast retrieval and query response times
- **Scalability**: Ability to handle growing document volumes
- **Reliability**: Data durability and availability
- **Cost-effectiveness**: Optimized storage costs at scale
- **Maintainability**: Easy backup, recovery, and updates

### Current Architecture

```
querio/
├── data/              # Raw PDFs (file system)
├── chroma_db/         # Vector embeddings (ChromaDB)
└── In-memory          # Document metadata (Python dict)
```

**Limitations:**
- ❌ Not persistent (metadata lost on restart)
- ❌ Limited scalability
- ❌ No redundancy
- ❌ Difficult to backup
- ❌ No multi-instance support

---

## Storage Architecture

### Recommended Multi-Layer Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Application Layer                         │
│                     (FastAPI Backend)                        │
└────────────────┬────────────────────────────────────────────┘
                 │
    ┌────────────┼────────────┬────────────┬─────────────┐
    │            │            │            │             │
    ▼            ▼            ▼            ▼             ▼
┌────────┐  ┌────────┐  ┌──────────┐  ┌────────┐  ┌────────┐
│  S3    │  │ Postgres│  │ ChromaDB/│  │ Elastic│  │ Redis  │
│ Object │  │  (SQL)  │  │ Pinecone │  │ search │  │ Cache  │
│Storage │  │         │  │ (Vectors)│  │ (Text) │  │        │
└────────┘  └────────┘  └──────────┘  └────────┘  └────────┘
    │            │            │            │             │
    ▼            ▼            ▼            ▼             ▼
┌────────────────────────────────────────────────────────────┐
│              Storage Purpose                                │
├────────────────────────────────────────────────────────────┤
│ Raw PDFs  │ Metadata   │ Embeddings │ Full-text │ Hot Data│
│ Archives  │ Relations  │ Similarity │ Search    │ Session │
└────────────────────────────────────────────────────────────┘
```

---

## Storage Layers

### 1. Raw PDF Storage

Raw PDF files are the source of truth and need durable, cost-effective storage.

#### Option A: Cloud Object Storage (🏆 Recommended)

**Providers:**
- **AWS S3** (Most popular)
- **Google Cloud Storage**
- **Azure Blob Storage**
- **MinIO** (Self-hosted, S3-compatible)

**Advantages:**
- ✅ Unlimited scalability
- ✅ 99.999999999% durability (11 nines)
- ✅ Cost-effective: $0.023/GB/month (S3 Standard)
- ✅ Built-in versioning and lifecycle policies
- ✅ CDN integration (CloudFront, Fastly)
- ✅ Server-side encryption
- ✅ Event-driven processing (S3 triggers)

**Implementation Example:**

```python
import boto3
from botocore.exceptions import ClientError

class S3DocumentStorage:
    def __init__(self, bucket_name, region='us-east-1'):
        self.s3_client = boto3.client('s3', region_name=region)
        self.bucket_name = bucket_name

    def upload_pdf(self, file_path, s3_key):
        """Upload PDF to S3"""
        try:
            self.s3_client.upload_file(
                file_path,
                self.bucket_name,
                s3_key,
                ExtraArgs={
                    'ContentType': 'application/pdf',
                    'ServerSideEncryption': 'AES256'
                }
            )
            return f"s3://{self.bucket_name}/{s3_key}"
        except ClientError as e:
            raise Exception(f"S3 upload failed: {e}")

    def download_pdf(self, s3_key, local_path):
        """Download PDF from S3"""
        self.s3_client.download_file(
            self.bucket_name,
            s3_key,
            local_path
        )

    def get_presigned_url(self, s3_key, expiration=3600):
        """Generate temporary download URL"""
        url = self.s3_client.generate_presigned_url(
            'get_object',
            Params={'Bucket': self.bucket_name, 'Key': s3_key},
            ExpiresIn=expiration
        )
        return url

    def delete_pdf(self, s3_key):
        """Delete PDF from S3"""
        self.s3_client.delete_object(
            Bucket=self.bucket_name,
            Key=s3_key
        )
```

**S3 Lifecycle Configuration:**

```python
lifecycle_config = {
    'Rules': [
        {
            'Id': 'ArchiveOldDocuments',
            'Status': 'Enabled',
            'Transitions': [
                {
                    'Days': 90,
                    'StorageClass': 'STANDARD_IA'  # Infrequent Access
                },
                {
                    'Days': 365,
                    'StorageClass': 'GLACIER'  # Long-term archive
                }
            ]
        }
    ]
}
```

**Cost Breakdown (AWS S3):**
- Storage: $0.023/GB/month (Standard)
- Requests: $0.0004 per 1,000 GET requests
- Data Transfer: $0.09/GB out to internet
- Example: 1TB PDFs, 10K downloads/month = ~$35/month

---

#### Option B: Database BLOB Storage

**Technologies:**
- PostgreSQL with BYTEA
- MongoDB GridFS
- MySQL BLOB

**Advantages:**
- ✅ ACID transactions
- ✅ Integrated with metadata
- ✅ No external dependencies

**Disadvantages:**
- ❌ Expensive at scale (database storage is pricey)
- ❌ Slower than object storage
- ❌ Database size bloat
- ❌ Difficult backups

**PostgreSQL Implementation:**

```sql
CREATE TABLE document_files (
    id UUID PRIMARY KEY,
    document_id UUID REFERENCES documents(id),
    file_data BYTEA NOT NULL,
    file_size BIGINT NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Size limit: PostgreSQL BYTEA max is 1GB
```

**Use Case:** Small systems (<1000 documents), need transactional guarantees

---

#### Option C: File System Storage

**Advantages:**
- ✅ Simple, no external dependencies
- ✅ Fast local access
- ✅ Easy development/testing

**Disadvantages:**
- ❌ Not scalable horizontally
- ❌ No built-in redundancy
- ❌ Difficult to backup at scale
- ❌ No versioning
- ❌ Single point of failure

**Enhanced File System Implementation:**

```python
from pathlib import Path
import hashlib
import shutil

class FileSystemStorage:
    def __init__(self, base_path='./data'):
        self.base_path = Path(base_path)
        self.base_path.mkdir(exist_ok=True)

    def _get_hash_path(self, file_id):
        """Create hash-based directory structure"""
        # Distribute files across subdirectories
        # e.g., abc123 -> ab/c1/abc123.pdf
        hash_prefix = file_id[:2]
        hash_middle = file_id[2:4]
        return self.base_path / hash_prefix / hash_middle / f"{file_id}.pdf"

    def save_pdf(self, file_id, source_path):
        """Save PDF with hash-based organization"""
        dest_path = self._get_hash_path(file_id)
        dest_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source_path, dest_path)
        return str(dest_path)

    def verify_integrity(self, file_id, expected_hash):
        """Verify file integrity with checksum"""
        file_path = self._get_hash_path(file_id)
        with open(file_path, 'rb') as f:
            file_hash = hashlib.sha256(f.read()).hexdigest()
        return file_hash == expected_hash
```

**Use Case:** MVP, development, small deployments (<10K docs)

---

### 2. Text Chunks Storage

Extracted and processed text chunks need queryable storage.

#### Option A: Document Database (🏆 Recommended)

**MongoDB**

**Schema:**
```javascript
{
  "_id": ObjectId("..."),
  "chunk_id": "uuid-v4",
  "document_id": "doc-uuid",
  "content": "Extracted text content from PDF...",
  "chunk_index": 0,
  "page_number": 1,
  "character_count": 1024,
  "metadata": {
    "source": "document.pdf",
    "chapter": "Introduction",
    "section": "1.1",
    "language": "en"
  },
  "embedding_id": "chromadb-ref",
  "created_at": ISODate("2024-01-10T12:00:00Z"),
  "updated_at": ISODate("2024-01-10T12:00:00Z")
}
```

**Indexes:**
```javascript
db.chunks.createIndex({ "document_id": 1 })
db.chunks.createIndex({ "content": "text" })  // Full-text search
db.chunks.createIndex({ "chunk_index": 1 })
db.chunks.createIndex({ "created_at": -1 })
```

**Python Implementation:**

```python
from pymongo import MongoClient
from datetime import datetime
import uuid

class MongoChunkStore:
    def __init__(self, connection_string):
        self.client = MongoClient(connection_string)
        self.db = self.client.querio
        self.chunks = self.db.chunks

        # Create indexes
        self.chunks.create_index("document_id")
        self.chunks.create_index([("content", "text")])

    def store_chunks(self, document_id, chunks_data):
        """Store multiple chunks"""
        documents = []
        for idx, chunk in enumerate(chunks_data):
            doc = {
                "chunk_id": str(uuid.uuid4()),
                "document_id": document_id,
                "content": chunk["text"],
                "chunk_index": idx,
                "page_number": chunk.get("page", None),
                "character_count": len(chunk["text"]),
                "metadata": chunk.get("metadata", {}),
                "created_at": datetime.utcnow()
            }
            documents.append(doc)

        result = self.chunks.insert_many(documents)
        return result.inserted_ids

    def get_document_chunks(self, document_id):
        """Retrieve all chunks for a document"""
        return list(self.chunks.find(
            {"document_id": document_id}
        ).sort("chunk_index", 1))

    def full_text_search(self, query, limit=10):
        """Full-text search across chunks"""
        return list(self.chunks.find(
            {"$text": {"$search": query}},
            {"score": {"$meta": "textScore"}}
        ).sort([("score", {"$meta": "textScore"})]).limit(limit))
```

---

#### Option B: PostgreSQL with JSONB

**Schema:**
```sql
CREATE TABLE document_chunks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    document_id UUID NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    content TEXT NOT NULL,
    chunk_index INTEGER NOT NULL,
    page_number INTEGER,
    character_count INTEGER,
    metadata JSONB,
    embedding_id VARCHAR(100),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),

    CONSTRAINT unique_doc_chunk UNIQUE(document_id, chunk_index)
);

-- Indexes
CREATE INDEX idx_chunks_document_id ON document_chunks(document_id);
CREATE INDEX idx_chunks_metadata ON document_chunks USING GIN(metadata);
CREATE INDEX idx_chunks_content_fts ON document_chunks USING GIN(to_tsvector('english', content));

-- Full-text search function
CREATE INDEX idx_chunks_content_search ON document_chunks
USING GIN(to_tsvector('english', content));
```

**Python Implementation (SQLAlchemy):**

```python
from sqlalchemy import Column, String, Integer, Text, DateTime, func
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.ext.declarative import declarative_base
import uuid

Base = declarative_base()

class DocumentChunk(Base):
    __tablename__ = 'document_chunks'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    document_id = Column(UUID(as_uuid=True), nullable=False)
    content = Column(Text, nullable=False)
    chunk_index = Column(Integer, nullable=False)
    page_number = Column(Integer)
    character_count = Column(Integer)
    metadata = Column(JSONB)
    embedding_id = Column(String(100))
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    @classmethod
    def search_full_text(cls, session, query, limit=10):
        """Full-text search using PostgreSQL"""
        from sqlalchemy import func
        return session.query(cls).filter(
            func.to_tsvector('english', cls.content).match(query)
        ).limit(limit).all()
```

---

#### Option C: Elasticsearch (Best for Search-Heavy Applications)

**Schema:**
```json
{
  "mappings": {
    "properties": {
      "chunk_id": { "type": "keyword" },
      "document_id": { "type": "keyword" },
      "content": {
        "type": "text",
        "analyzer": "english",
        "fields": {
          "keyword": { "type": "keyword" }
        }
      },
      "chunk_index": { "type": "integer" },
      "page_number": { "type": "integer" },
      "metadata": { "type": "object" },
      "created_at": { "type": "date" }
    }
  }
}
```

**Python Implementation:**

```python
from elasticsearch import Elasticsearch

class ElasticsearchChunkStore:
    def __init__(self, hosts=['localhost:9200']):
        self.es = Elasticsearch(hosts)
        self.index_name = 'document_chunks'

    def index_chunks(self, chunks):
        """Bulk index chunks"""
        from elasticsearch.helpers import bulk

        actions = [
            {
                "_index": self.index_name,
                "_id": chunk["chunk_id"],
                "_source": chunk
            }
            for chunk in chunks
        ]
        bulk(self.es, actions)

    def search(self, query, size=10):
        """Search with relevance scoring"""
        result = self.es.search(
            index=self.index_name,
            body={
                "query": {
                    "multi_match": {
                        "query": query,
                        "fields": ["content^2", "metadata.title"],
                        "type": "best_fields"
                    }
                },
                "size": size,
                "highlight": {
                    "fields": {"content": {}}
                }
            }
        )
        return result['hits']['hits']
```

---

### 3. Vector Embeddings Storage

Vector databases store high-dimensional embeddings for semantic search.

#### Comparison Matrix

| Database | Scale | Latency | Cost | Managed | Open Source |
|----------|-------|---------|------|---------|-------------|
| **ChromaDB** | <10M | Fast | Free | No | ✅ Yes |
| **FAISS** | <100M | Fastest | Free | No | ✅ Yes |
| **Pinecone** | Unlimited | Fast | $70+/mo | ✅ Yes | ❌ No |
| **Weaviate** | <100M | Fast | Free/Paid | Optional | ✅ Yes |
| **Qdrant** | <100M | Fast | Free/Paid | Optional | ✅ Yes |
| **Milvus** | Unlimited | Fast | Free | No | ✅ Yes |
| **pgvector** | <50M | Medium | Free | No | ✅ Yes |

---

#### Option A: ChromaDB (🏆 Current - Good for Small-Medium)

**Advantages:**
- ✅ Easy setup, no infrastructure
- ✅ Good performance (<10M vectors)
- ✅ Built-in persistence
- ✅ Python-native

**Limitations:**
- ❌ Single-instance only
- ❌ Limited filtering capabilities
- ❌ Slower at large scale

**Current Implementation:**
```python
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings

embedding_model = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

vectordb = Chroma.from_documents(
    documents=documents,
    embedding=embedding_model,
    persist_directory="./chroma_db"
)
```

**When to Upgrade:** >1M vectors, need multi-tenancy, require distributed setup

---

#### Option B: Pinecone (🏆 Recommended for Production)

**Advantages:**
- ✅ Fully managed (no ops)
- ✅ Unlimited scale
- ✅ Fast (<100ms queries)
- ✅ Advanced filtering
- ✅ Multi-tenancy support

**Pricing:**
- Starter: $70/month (1M vectors, 1 pod)
- Standard: $0.096/hour per pod
- Enterprise: Custom pricing

**Implementation:**

```python
import pinecone
from langchain.vectorstores import Pinecone

# Initialize
pinecone.init(
    api_key="your-api-key",
    environment="us-west1-gcp"
)

# Create index
pinecone.create_index(
    name="querio-docs",
    dimension=384,  # all-MiniLM-L6-v2 dimension
    metric="cosine"
)

# Use with LangChain
vectordb = Pinecone.from_documents(
    documents,
    embedding_model,
    index_name="querio-docs"
)

# Query with metadata filtering
results = vectordb.similarity_search(
    query,
    k=5,
    filter={"document_id": "abc123", "page": {"$gte": 10}}
)
```

---

#### Option C: Weaviate (Open Source Alternative)

**Advantages:**
- ✅ Open source
- ✅ Self-hosted or cloud
- ✅ GraphQL API
- ✅ Hybrid search (vector + keyword)

**Implementation:**

```python
import weaviate

client = weaviate.Client("http://localhost:8080")

# Define schema
schema = {
    "class": "DocumentChunk",
    "vectorizer": "text2vec-transformers",
    "properties": [
        {"name": "content", "dataType": ["text"]},
        {"name": "document_id", "dataType": ["string"]},
        {"name": "chunk_index", "dataType": ["int"]}
    ]
}

client.schema.create_class(schema)

# Insert
client.data_object.create(
    class_name="DocumentChunk",
    data_object={
        "content": "Document text...",
        "document_id": "doc123"
    }
)

# Hybrid search (vector + keyword)
result = client.query.get(
    "DocumentChunk",
    ["content", "document_id"]
).with_hybrid(
    query="machine learning",
    alpha=0.5  # 0=keyword only, 1=vector only
).with_limit(10).do()
```

---

#### Option D: pgvector (PostgreSQL Extension)

**Advantages:**
- ✅ Use existing PostgreSQL
- ✅ No additional infrastructure
- ✅ ACID transactions
- ✅ Combine vector + relational queries

**Setup:**

```sql
-- Install extension
CREATE EXTENSION vector;

-- Add vector column
ALTER TABLE document_chunks
ADD COLUMN embedding vector(384);

-- Create index
CREATE INDEX ON document_chunks
USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 100);
```

**Python Implementation:**

```python
from pgvector.sqlalchemy import Vector
from sqlalchemy import Column

class DocumentChunk(Base):
    __tablename__ = 'document_chunks'
    # ... other columns
    embedding = Column(Vector(384))

# Query
from sqlalchemy import func

similar_chunks = session.query(DocumentChunk).order_by(
    DocumentChunk.embedding.cosine_distance(query_embedding)
).limit(10).all()
```

**Performance:** Good for <10M vectors, slower than specialized vector DBs

---

### 4. Metadata Storage

Relational database for structured metadata and relationships.

#### 🏆 PostgreSQL (Recommended)

**Complete Schema:**

```sql
-- Users table (if multi-tenancy needed)
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    username VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    is_active BOOLEAN DEFAULT TRUE
);

-- Documents table
CREATE TABLE documents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    filename VARCHAR(255) NOT NULL,
    original_filename VARCHAR(255) NOT NULL,
    file_size BIGINT NOT NULL,
    mime_type VARCHAR(50) DEFAULT 'application/pdf',

    -- Storage references
    storage_type VARCHAR(20) DEFAULT 'filesystem',  -- filesystem, s3, etc.
    storage_path VARCHAR(500),  -- Local path or S3 key
    s3_bucket VARCHAR(100),
    s3_key VARCHAR(500),

    -- Processing status
    processed BOOLEAN DEFAULT FALSE,
    processing_status VARCHAR(50),  -- pending, processing, completed, failed
    processing_started_at TIMESTAMP,
    processing_completed_at TIMESTAMP,
    error_message TEXT,

    -- Document metadata
    page_count INTEGER,
    word_count INTEGER,
    language VARCHAR(10),
    author VARCHAR(255),
    title VARCHAR(500),
    created_date DATE,

    -- System metadata
    uploaded_by UUID REFERENCES users(id),
    uploaded_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),

    -- Additional metadata (flexible)
    tags TEXT[],
    metadata JSONB,

    -- Soft delete
    deleted_at TIMESTAMP
);

-- Chunks table (if storing in PostgreSQL)
CREATE TABLE document_chunks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    document_id UUID NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    content TEXT NOT NULL,
    chunk_index INTEGER NOT NULL,
    page_number INTEGER,
    character_count INTEGER,
    token_count INTEGER,

    -- Vector DB reference
    embedding_id VARCHAR(100),  -- Reference to vector DB entry

    metadata JSONB,
    created_at TIMESTAMP DEFAULT NOW(),

    CONSTRAINT unique_doc_chunk UNIQUE(document_id, chunk_index)
);

-- Chat sessions
CREATE TABLE chat_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    title VARCHAR(255),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    message_count INTEGER DEFAULT 0,
    metadata JSONB
);

-- Chat messages
CREATE TABLE chat_messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID NOT NULL REFERENCES chat_sessions(id) ON DELETE CASCADE,
    role VARCHAR(20) NOT NULL,  -- user, assistant, system
    content TEXT NOT NULL,

    -- Source documents
    source_chunks UUID[],  -- Array of chunk IDs

    created_at TIMESTAMP DEFAULT NOW(),
    metadata JSONB
);

-- Query analytics
CREATE TABLE query_analytics (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    query TEXT NOT NULL,
    response_time_ms INTEGER,
    chunks_retrieved INTEGER,
    success BOOLEAN,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_documents_uploaded_by ON documents(uploaded_by);
CREATE INDEX idx_documents_uploaded_at ON documents(uploaded_at);
CREATE INDEX idx_documents_status ON documents(processing_status);
CREATE INDEX idx_documents_tags ON documents USING GIN(tags);
CREATE INDEX idx_documents_metadata ON documents USING GIN(metadata);

CREATE INDEX idx_chunks_document_id ON document_chunks(document_id);
CREATE INDEX idx_chunks_content_fts ON document_chunks USING GIN(to_tsvector('english', content));

CREATE INDEX idx_chat_session_user ON chat_sessions(user_id);
CREATE INDEX idx_chat_messages_session ON chat_messages(session_id);
CREATE INDEX idx_chat_messages_created ON chat_messages(created_at);

CREATE INDEX idx_analytics_user ON query_analytics(user_id);
CREATE INDEX idx_analytics_created ON query_analytics(created_at);
```

**SQLAlchemy Models:**

```python
from sqlalchemy import Column, String, Integer, BigInteger, Boolean, Text, TIMESTAMP, ARRAY, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
import uuid
from datetime import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False)
    username = Column(String(100), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.now())
    is_active = Column(Boolean, default=True)

    documents = relationship("Document", back_populates="user")

class Document(Base):
    __tablename__ = 'documents'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    filename = Column(String(255), nullable=False)
    original_filename = Column(String(255), nullable=False)
    file_size = Column(BigInteger, nullable=False)
    mime_type = Column(String(50), default='application/pdf')

    storage_type = Column(String(20), default='filesystem')
    storage_path = Column(String(500))
    s3_bucket = Column(String(100))
    s3_key = Column(String(500))

    processed = Column(Boolean, default=False)
    processing_status = Column(String(50))
    processing_started_at = Column(TIMESTAMP)
    processing_completed_at = Column(TIMESTAMP)
    error_message = Column(Text)

    page_count = Column(Integer)
    word_count = Column(Integer)
    language = Column(String(10))
    author = Column(String(255))
    title = Column(String(500))

    uploaded_by = Column(UUID(as_uuid=True), ForeignKey('users.id'))
    uploaded_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

    tags = Column(ARRAY(Text))
    metadata = Column(JSONB)
    deleted_at = Column(TIMESTAMP)

    user = relationship("User", back_populates="documents")
    chunks = relationship("DocumentChunk", back_populates="document", cascade="all, delete-orphan")

class DocumentChunk(Base):
    __tablename__ = 'document_chunks'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    document_id = Column(UUID(as_uuid=True), ForeignKey('documents.id'), nullable=False)
    content = Column(Text, nullable=False)
    chunk_index = Column(Integer, nullable=False)
    page_number = Column(Integer)
    character_count = Column(Integer)
    token_count = Column(Integer)
    embedding_id = Column(String(100))
    metadata = Column(JSONB)
    created_at = Column(TIMESTAMP, server_default=func.now())

    document = relationship("Document", back_populates="chunks")
```

---

### 5. Caching Layer

Redis for performance optimization and session management.

#### 🏆 Redis (Recommended)

**Use Cases:**
- Query result caching
- Embedding caching
- Rate limiting
- Session storage
- Real-time analytics

**Implementation:**

```python
import redis
import json
import hashlib
from functools import wraps

class RedisCache:
    def __init__(self, host='localhost', port=6379, db=0):
        self.client = redis.Redis(
            host=host,
            port=port,
            db=db,
            decode_responses=True
        )

    def cache_query_result(self, query, result, ttl=3600):
        """Cache query results"""
        key = f"query:{self._hash_query(query)}"
        self.client.setex(key, ttl, json.dumps(result))

    def get_cached_query(self, query):
        """Get cached query result"""
        key = f"query:{self._hash_query(query)}"
        result = self.client.get(key)
        return json.loads(result) if result else None

    def cache_embedding(self, text, embedding, ttl=86400):
        """Cache text embeddings"""
        key = f"embedding:{self._hash_text(text)}"
        self.client.setex(key, ttl, json.dumps(embedding.tolist()))

    def get_cached_embedding(self, text):
        """Get cached embedding"""
        key = f"embedding:{self._hash_text(text)}"
        result = self.client.get(key)
        if result:
            import numpy as np
            return np.array(json.loads(result))
        return None

    def rate_limit(self, user_id, max_requests=100, window=3600):
        """Implement rate limiting"""
        key = f"ratelimit:{user_id}"
        current = self.client.get(key)

        if current is None:
            self.client.setex(key, window, 1)
            return True
        elif int(current) < max_requests:
            self.client.incr(key)
            return True
        else:
            return False

    def store_session(self, session_id, data, ttl=3600):
        """Store session data"""
        key = f"session:{session_id}"
        self.client.setex(key, ttl, json.dumps(data))

    def _hash_query(self, query):
        return hashlib.md5(query.encode()).hexdigest()

    def _hash_text(self, text):
        return hashlib.md5(text.encode()).hexdigest()

# Decorator for caching
def cache_result(ttl=3600):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            cache = RedisCache()

            # Create cache key from function name and args
            cache_key = f"{func.__name__}:{str(args)}:{str(kwargs)}"

            # Try to get from cache
            cached = cache.client.get(cache_key)
            if cached:
                return json.loads(cached)

            # Execute function
            result = func(*args, **kwargs)

            # Store in cache
            cache.client.setex(cache_key, ttl, json.dumps(result))

            return result
        return wrapper
    return decorator

# Usage
@cache_result(ttl=1800)
def expensive_query(query_text):
    # Expensive operation
    return result
```

**Redis Data Structures for Analytics:**

```python
# Track popular queries
redis_client.zincrby("popular_queries", 1, query_text)

# Get top 10 queries
top_queries = redis_client.zrevrange("popular_queries", 0, 9, withscores=True)

# Track user activity
redis_client.pfadd(f"active_users:{date}", user_id)  # HyperLogLog for unique counts

# Count active users
active_count = redis_client.pfcount(f"active_users:{date}")
```

---

## Architecture by Scale

### Startup / MVP (0-10K documents)

**Stack:**
```
✅ File System (local PDFs)
✅ ChromaDB (vectors)
✅ In-memory or SQLite (metadata)
```

**Pros:** Simple, fast to develop, zero cost
**Cons:** Not scalable, no redundancy
**Cost:** $0/month
**Setup Time:** Hours

---

### Small Business (10K-100K documents)

**Stack:**
```
✅ AWS S3 (raw PDFs)
✅ PostgreSQL (metadata + chunks)
✅ ChromaDB (vectors)
✅ Redis (caching)
```

**Pros:** Scalable, reliable, affordable
**Cons:** Requires ops, single vector DB instance
**Cost:** $50-200/month
**Setup Time:** 1-2 days

**Architecture Diagram:**
```
Client → FastAPI → PostgreSQL (metadata)
                 ↓
                 → ChromaDB (vectors)
                 ↓
                 → S3 (PDFs)
                 ↓
                 → Redis (cache)
```

---

### Mid-Market (100K-1M documents)

**Stack:**
```
✅ AWS S3 + CloudFront CDN (PDFs)
✅ PostgreSQL RDS (metadata)
✅ MongoDB Atlas (chunks)
✅ Pinecone (vectors)
✅ Redis Cluster (caching)
```

**Pros:** High performance, managed services
**Cons:** Higher cost, vendor lock-in
**Cost:** $500-2000/month
**Setup Time:** 1 week

---

### Enterprise (1M+ documents)

**Stack:**
```
✅ Multi-region S3 + CloudFront (PDFs)
✅ PostgreSQL RDS Multi-AZ (metadata)
✅ Elasticsearch Cluster (full-text + chunks)
✅ Pinecone or Milvus (vectors)
✅ Redis Cluster (caching)
✅ SQS/Kafka (async processing)
✅ ECS/Kubernetes (container orchestration)
```

**Pros:** Unlimited scale, high availability
**Cons:** Complex, expensive
**Cost:** $5,000-50,000/month
**Setup Time:** 2-4 weeks

---

## Optimization Strategies

### 1. Chunk Size Optimization

```python
import matplotlib.pyplot as plt

# Test different chunk sizes
CHUNK_SIZES = [256, 512, 1000, 2000, 4000]
results = {}

for size in CHUNK_SIZES:
    chunks = split_text(document_text, chunk_size=size)

    # Metrics
    num_chunks = len(chunks)
    avg_retrieval_time = benchmark_retrieval(chunks, test_queries)
    retrieval_accuracy = measure_accuracy(chunks, ground_truth)

    results[size] = {
        'num_chunks': num_chunks,
        'retrieval_time': avg_retrieval_time,
        'accuracy': retrieval_accuracy
    }

# Visualize
plt.plot([r['accuracy'] for r in results.values()],
         [r['retrieval_time'] for r in results.values()])
plt.xlabel('Accuracy')
plt.ylabel('Retrieval Time (ms)')
plt.title('Chunk Size Trade-offs')
plt.show()
```

**Recommendations:**
- **256-512 tokens**: High precision, more chunks, slower indexing
- **1000-2000 tokens**: **Balanced (recommended)**
- **4000+ tokens**: More context, less precision, faster indexing

---

### 2. Hybrid Search (Vector + Keyword)

```python
def hybrid_search(query, k=10, alpha=0.5):
    """
    Combine vector and keyword search
    alpha: 0 = keyword only, 1 = vector only
    """
    # Vector search
    vector_results = vector_db.similarity_search(query, k=k*2)
    vector_scores = {doc.id: 1.0 - (i / len(vector_results))
                     for i, doc in enumerate(vector_results)}

    # Keyword search (BM25 or Elasticsearch)
    keyword_results = elasticsearch.search(query, size=k*2)
    keyword_scores = {doc['id']: doc['_score'] / max_score
                      for doc in keyword_results}

    # Combine with Reciprocal Rank Fusion (RRF)
    all_ids = set(vector_scores.keys()) | set(keyword_scores.keys())
    combined_scores = {}

    for doc_id in all_ids:
        vector_score = vector_scores.get(doc_id, 0)
        keyword_score = keyword_scores.get(doc_id, 0)

        # Weighted combination
        combined_scores[doc_id] = (
            alpha * vector_score +
            (1 - alpha) * keyword_score
        )

    # Sort and return top k
    ranked = sorted(combined_scores.items(),
                   key=lambda x: x[1], reverse=True)[:k]

    return [get_document(doc_id) for doc_id, score in ranked]
```

---

### 3. Embedding Caching

```python
class EmbeddingCache:
    def __init__(self):
        self.redis_client = redis.Redis()
        self.embedding_model = HuggingFaceEmbeddings(...)

    def get_embedding(self, text):
        """Get embedding with caching"""
        # Check cache
        cache_key = f"emb:{hash(text)}"
        cached = self.redis_client.get(cache_key)

        if cached:
            return pickle.loads(cached)

        # Generate embedding
        embedding = self.embedding_model.embed_query(text)

        # Cache for 24 hours
        self.redis_client.setex(
            cache_key,
            86400,
            pickle.dumps(embedding)
        )

        return embedding
```

**Performance Improvement:** 10-100x faster for repeated queries

---

### 4. Batch Processing

```python
async def batch_process_documents(document_ids, batch_size=10):
    """Process documents in batches for efficiency"""
    import asyncio

    async def process_batch(batch):
        tasks = [process_document(doc_id) for doc_id in batch]
        return await asyncio.gather(*tasks)

    results = []
    for i in range(0, len(document_ids), batch_size):
        batch = document_ids[i:i+batch_size]
        batch_results = await process_batch(batch)
        results.extend(batch_results)

    return results
```

---

### 5. Query Result Caching Strategy

```python
class QueryCache:
    def __init__(self):
        self.redis = redis.Redis()

    def cache_query(self, query, result, user_context=None):
        """Smart caching with context awareness"""
        # Create contextual cache key
        context_hash = hash(json.dumps(user_context)) if user_context else ""
        cache_key = f"query:{hash(query)}:{context_hash}"

        # Cache with TTL based on query type
        ttl = self._determine_ttl(query)

        self.redis.setex(
            cache_key,
            ttl,
            json.dumps(result)
        )

    def _determine_ttl(self, query):
        """Dynamic TTL based on query characteristics"""
        if "latest" in query.lower() or "recent" in query.lower():
            return 300  # 5 minutes for time-sensitive queries
        elif len(query.split()) < 3:
            return 1800  # 30 minutes for short queries
        else:
            return 3600  # 1 hour for complex queries
```

---

## Migration Path

### Phase 1: Add PostgreSQL (Week 1)

**Goal:** Replace in-memory metadata storage

**Steps:**
1. Install PostgreSQL and SQLAlchemy
```bash
pip install sqlalchemy psycopg2-binary alembic
```

2. Create database models (see Metadata Storage section)

3. Set up Alembic for migrations
```bash
alembic init alembic
alembic revision --autogenerate -m "Initial schema"
alembic upgrade head
```

4. Migrate existing data
```python
def migrate_to_postgres():
    # Load existing metadata
    old_metadata = load_from_memory()

    # Insert into PostgreSQL
    session = Session()
    for doc in old_metadata:
        db_doc = Document(**doc)
        session.add(db_doc)
    session.commit()
```

**Testing:** Verify all API endpoints work with PostgreSQL

---

### Phase 2: Add S3 Storage (Week 2)

**Goal:** Move PDFs to cloud storage

**Steps:**
1. Create S3 bucket
```bash
aws s3 mb s3://querio-documents-prod
```

2. Update upload logic
```python
def upload_to_s3(file_path, document_id):
    s3_key = f"documents/{document_id}.pdf"
    s3_client.upload_file(file_path, 'querio-documents-prod', s3_key)
    return s3_key
```

3. Migrate existing files
```python
def migrate_to_s3():
    for pdf_file in Path('data').glob('*.pdf'):
        s3_key = upload_to_s3(str(pdf_file), pdf_file.stem)
        # Update database with S3 reference
        update_document(pdf_file.stem, s3_key=s3_key)
```

**Testing:** Upload and retrieve documents via API

---

### Phase 3: Add Redis Caching (Week 3)

**Goal:** Improve response times

**Steps:**
1. Install Redis
```bash
# Docker
docker run -d -p 6379:6379 redis:alpine

# Or install locally
brew install redis  # Mac
sudo apt install redis  # Linux
```

2. Implement caching layer (see Caching section)

3. Add cache to query endpoints
```python
@router.post("/query")
async def query_documents(request: QueryRequest):
    # Check cache
    cached = redis_cache.get_cached_query(request.query)
    if cached:
        return cached

    # Execute query
    result = execute_query(request.query)

    # Cache result
    redis_cache.cache_query_result(request.query, result)

    return result
```

**Testing:** Measure response time improvement

---

### Phase 4: Upgrade Vector Database (Month 2)

**Goal:** Scale beyond ChromaDB limitations

**Steps:**
1. Choose target (Pinecone recommended for managed)

2. Create migration script
```python
def migrate_to_pinecone():
    # Initialize Pinecone
    pinecone.init(api_key="...", environment="...")
    pinecone.create_index("querio-vectors", dimension=384)

    # Read all vectors from ChromaDB
    old_vectors = chroma_db.get_all_vectors()

    # Batch upload to Pinecone
    index = pinecone.Index("querio-vectors")
    for batch in chunks(old_vectors, 100):
        index.upsert(batch)
```

3. Update query logic

4. A/B test both systems before complete cutover

**Testing:** Compare retrieval quality and performance

---

## Cost Analysis

### Monthly Cost Breakdown

#### Small Deployment (10K documents)
```
AWS S3 Storage (10 GB):         $0.23
S3 Requests (10K/month):        $0.04
PostgreSQL RDS (db.t3.micro):   $15.00
Redis (cache.t3.micro):         $12.00
ChromaDB (self-hosted):         $0.00
EC2 (t3.medium for API):        $30.00
Data Transfer:                  $5.00
----------------------------------------
Total:                          ~$62/month
```

#### Medium Deployment (100K documents)
```
AWS S3 Storage (100 GB):        $2.30
S3 Requests (100K/month):       $0.40
PostgreSQL RDS (db.t3.small):   $30.00
MongoDB Atlas (M10):            $60.00
Redis (cache.m5.large):         $100.00
Pinecone (Starter):             $70.00
EC2/ECS (multiple instances):   $200.00
Data Transfer:                  $30.00
----------------------------------------
Total:                          ~$492/month
```

#### Large Deployment (1M documents)
```
AWS S3 Storage (1 TB):          $23.00
S3 Requests (1M/month):         $4.00
PostgreSQL RDS (Multi-AZ):      $300.00
Elasticsearch (3-node):         $500.00
Redis Cluster:                  $200.00
Pinecone (Standard, 2 pods):    $350.00
ECS/Kubernetes:                 $800.00
Load Balancer:                  $25.00
Data Transfer:                  $200.00
CloudWatch/Monitoring:          $50.00
----------------------------------------
Total:                          ~$2,452/month
```

---

## Implementation Examples

### Complete PostgreSQL Setup

```python
# database.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.ext.declarative import declarative_base

DATABASE_URL = "postgresql://user:password@localhost/querio"

engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# models.py
# (See Metadata Storage section for complete models)

# crud.py
from sqlalchemy.orm import Session
from models import Document
import uuid

def create_document(db: Session, filename: str, file_size: int, **kwargs):
    document = Document(
        id=uuid.uuid4(),
        filename=filename,
        file_size=file_size,
        **kwargs
    )
    db.add(document)
    db.commit()
    db.refresh(document)
    return document

def get_document(db: Session, document_id: str):
    return db.query(Document).filter(Document.id == document_id).first()

def list_documents(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Document).offset(skip).limit(limit).all()

def update_document(db: Session, document_id: str, **kwargs):
    document = db.query(Document).filter(Document.id == document_id).first()
    for key, value in kwargs.items():
        setattr(document, key, value)
    db.commit()
    return document

def delete_document(db: Session, document_id: str):
    document = db.query(Document).filter(Document.id == document_id).first()
    if document:
        db.delete(document)
        db.commit()
        return True
    return False
```

### Using with FastAPI

```python
from fastapi import Depends
from database import get_db
from sqlalchemy.orm import Session

@router.post("/documents/upload")
async def upload_document(
    file: UploadFile,
    db: Session = Depends(get_db)
):
    # Save file
    content = await file.read()

    # Create database entry
    document = create_document(
        db,
        filename=file.filename,
        file_size=len(content),
        processed=False
    )

    return document
```

---

## Best Practices

### 1. Data Retention and Archival

```python
# Implement lifecycle policies
def archive_old_documents(days=365):
    """Archive documents older than specified days"""
    cutoff_date = datetime.now() - timedelta(days=days)

    old_docs = db.query(Document).filter(
        Document.uploaded_at < cutoff_date,
        Document.accessed_at < cutoff_date  # Not accessed recently
    ).all()

    for doc in old_docs:
        # Move to Glacier storage
        s3_client.copy_object(
            Bucket='querio-documents-archive',
            CopySource={'Bucket': 'querio-documents', 'Key': doc.s3_key},
            StorageClass='GLACIER'
        )

        # Update database
        doc.storage_class = 'GLACIER'
        doc.archived_at = datetime.now()

    db.commit()
```

### 2. Backup Strategy

```bash
# PostgreSQL backups
# Daily backup with pg_dump
pg_dump -h localhost -U postgres querio > backup_$(date +%Y%m%d).sql

# Continuous archiving (WAL)
archive_mode = on
archive_command = 'cp %p /path/to/archive/%f'

# S3 backup
aws s3 sync /local/backup s3://querio-backups/postgres/
```

### 3. Monitoring and Alerts

```python
import prometheus_client as prom

# Metrics
query_duration = prom.Histogram(
    'query_duration_seconds',
    'Time spent processing query'
)

documents_total = prom.Counter(
    'documents_total',
    'Total number of documents'
)

vector_db_size = prom.Gauge(
    'vector_db_size_mb',
    'Size of vector database in MB'
)

# Usage
@query_duration.time()
def process_query(query):
    # ... query logic
    pass

documents_total.inc()
```

### 4. Security

```python
# Encrypt sensitive data
from cryptography.fernet import Fernet

def encrypt_content(content: bytes, key: bytes) -> bytes:
    f = Fernet(key)
    return f.encrypt(content)

def decrypt_content(encrypted: bytes, key: bytes) -> bytes:
    f = Fernet(key)
    return f.decrypt(encrypted)

# S3 server-side encryption
s3_client.upload_file(
    file_path,
    bucket,
    key,
    ExtraArgs={'ServerSideEncryption': 'AES256'}
)

# Database encryption at rest
# Enable in PostgreSQL config
ssl = on
ssl_cert_file = 'server.crt'
ssl_key_file = 'server.key'
```

---

## Performance Benchmarks

### Query Performance by Storage Type

| Storage | 1K Docs | 10K Docs | 100K Docs | 1M Docs |
|---------|---------|----------|-----------|---------|
| **ChromaDB** | 50ms | 100ms | 500ms | 2000ms |
| **Pinecone** | 30ms | 40ms | 60ms | 80ms |
| **Weaviate** | 40ms | 60ms | 100ms | 150ms |
| **pgvector** | 80ms | 200ms | 800ms | 3000ms |

### Storage Costs per 100GB

| Storage Type | Monthly Cost | Retrieval Cost | Notes |
|--------------|--------------|----------------|-------|
| **S3 Standard** | $2.30 | $0.40/10K | Best for frequent access |
| **S3 IA** | $1.25 | $1.00/10K | 30-day minimum |
| **S3 Glacier** | $0.40 | $10.00/10K + delay | Long-term archive |
| **EBS SSD** | $10.00 | Free | Fast local storage |
| **PostgreSQL** | $15.00 | Free | Expensive for files |

---

## Conclusion

### Recommended Immediate Actions for Querio

1. **Week 1:** Add PostgreSQL for metadata
   - Persistent storage
   - Better querying
   - Production-ready

2. **Week 2:** Implement Redis caching
   - 10x faster repeated queries
   - Session management
   - Rate limiting

3. **Month 2:** Evaluate vector DB upgrade
   - If >1M vectors: migrate to Pinecone
   - If cost-sensitive: try Weaviate/Qdrant

4. **Month 3:** Move to S3
   - When >10K documents
   - Better scalability
   - Lower costs

### Decision Matrix

**Choose File System if:**
- ✅ MVP/Development
- ✅ <1K documents
- ✅ Single server

**Choose PostgreSQL + S3 + ChromaDB if:**
- ✅ 10K-100K documents
- ✅ Small team
- ✅ Budget-conscious
- ✅ **Current sweet spot for Querio**

**Choose Full Cloud Stack if:**
- ✅ >100K documents
- ✅ Multi-tenancy
- ✅ High availability requirements
- ✅ Enterprise customers

---

## Additional Resources

- [PostgreSQL Best Practices](https://wiki.postgresql.org/wiki/Performance_Optimization)
- [AWS S3 Best Practices](https://docs.aws.amazon.com/AmazonS3/latest/userguide/best-practices.html)
- [Vector Database Comparison](https://github.com/erikbern/ann-benchmarks)
- [LangChain Documentation](https://python.langchain.com/docs/)
- [Redis Best Practices](https://redis.io/docs/manual/patterns/)

---

**Document Version:** 1.0
**Last Updated:** December 2024
**Maintained By:** Querio Development Team
**Feedback:** [Open an issue](https://github.com/paradocx96/querio/issues)
