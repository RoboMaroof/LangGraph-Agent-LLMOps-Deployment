# 🧠 LangGraph Agent API

A modular, production-ready backend for building intelligent agent workflows using LangGraph, FastAPI, Qdrant, and Poetry — all containerized via Docker. This system supports vector-based document retrieval, tool-augmented LLM responses, and seamless integration with local/S3 sources.

---

## 🚀 Features

- ✅ Conversational agents with LangGraph + LangChain
- ✅ Tool-augmented LLM responses (Wikipedia, Arxiv, Tavily, Vector DB)
- ✅ Qdrant vector database integration
- ✅ Upload or ingest documents from S3, SQLite, or websites
- ✅ Session-based memory & history
- ✅ FastAPI REST API
- ✅ Fully containerized (Docker + Poetry)
- ✅ Modular, extensible, and ready for production

---

## 📁 Project Structure

```plaintext
├── app.py           
├── agents/
│ ├── routes.py         
│ ├── agent_loader.py  
│ ├── graph_builder.py          
│ └── tools.py  
├── ingestion/
│ ├── routes.py         
│ ├── upload_handler.py  
│ ├── index_builder.py       
│ └── sources.py   
├── utils/
│ ├── config.py 
│ ├── logging_config.py # TODO 
│ ├── qdrant_utils.py 
│ └── logger.py         
├── Dockerfile          
├── pyproject.toml      
├── poetry.lock         
└── .env                # Local 
```

---

## ⚙️ Prerequisites

- [Docker](https://www.docker.com/)
- [Poetry](https://python-poetry.org/) (if running outside container)
- Qdrant Cloud or local instance
- OpenAI/Groq API key

---

## 📦 Quick Start (with Docker)

### 1. 🧪 Create `.env` File

```env
QDRANT_HOST=https://your-qdrant-instance
QDRANT_API_KEY=your-api-key
QDRANT_COLLECTION=langgraph-rag-vectordb

DEFAULT_DOCS_FOLDER=./docs
SQL_DB_PATH=./faq.sqlite3

LOG_LEVEL=DEBUG
```

---

### 2. 🐳 Build and Run the Docker Container

```bash
# Build the image
docker build -t langgraph-agent .

# Run the container
docker run --env-file .env -p 8000:8000 langgraph-agent
```

The server will:
- Set up Qdrant collection if needed
- Ingest documents if configured
- Preload your conversational agent

---

## 📡 API Endpoints

`🔗 /agent/invoke`
```http
POST /agent/invoke
```

***Body:***
```json
{
  "input": "Summarize LangGraph",
  "model": "openai:gpt-4o-mini",
  "session_id": "user-abc"
}
```

`📤 /vectordb/upload`
Upload and index a document:

```http
POST /vectordb/upload
```

`🛠️ /vectordb/create`
Manually ingest a source:

```json
{
  "source_type": "docs",
  "source_path": "s3://your-bucket/sample.pdf"
}
```

---

## 🧩 Supported Source Types

| Type     | Description                         |
|----------|-------------------------------------|
| `docs`   | Local folders or S3 document files  |
| `sql`    | SQLite FAQ table (Q/A pairs)        |
| `website`| Public URLs                         |

---

## 🔌 Tools Used

| Tool              | Description                             |
|-------------------|-----------------------------------------|
| WikipediaQueryRun | Wikipedia search                        |
| ArxivQueryRun     | Arxiv academic paper search             |
| TavilySearch      | Web search via Tavily                   |
| vector_retriever  | Custom document retrieval via Qdrant   |

---