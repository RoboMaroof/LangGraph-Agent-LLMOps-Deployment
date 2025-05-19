# LangGraph Agent LLMOps Deployment

This repository contains a complete **LangGraph-based LLMOps platform** for document ingestion, retrieval-augmented generation (RAG), and conversational agent execution — with a modular backend and frontend.

> Built using FastAPI, LangChain, LangGraph, Qdrant, and OpenAI.

---

## Tech Stack

| Category                     | Technologies                                                                 |
|-----------------------------|------------------------------------------------------------------------------|
| **Backend**                 | FastAPI, LangGraph, LangChain, LlamaIndex, Qdrant, OpenAI API, Groq API, SQLite, Boto3 |
| **Frontend**                | Streamlit                                                                    |
| **Tooling & Utilities**     | Poetry, Python-dotenv, Logging                                               |
| **Vector Indexing & Embeddings** | SentenceSplitter, OpenAIEmbedding, LLMRerank, QdrantVectorStore               |
| **Testing & CI/CD**         | Pytest, GitHub Actions, Docker, SSH, SCP, Appleboy Actions                   |
| **Cloud & Deployment**      | AWS EC2, Amazon S3, Qdrant Cloud, Environment Variables                      |

---

## Project Structure

```plaintext
├── backend/
│ ├── app/
│ │ ├── main.py             
│ ├── agents/
│ │ ├── routes.py         
│ │ ├── agent_loader.py  
│ │ ├── graph_builder.py          
│ │ └── tools.py  
│ ├── ingestion/
│ │ ├── routes.py         
│ │ ├── upload_handler.py  
│ │ ├── index_builder.py       
│ │ └── sources.py   
│ ├── utils/
│ │ ├── config.py 
│ │ ├── logging_config.py # TODO 
│ │ ├── qdrant_utils.py 
│ │ └── logger.py         
│ ├── Dockerfile          
│ ├── pyproject.toml      
│ ├── poetry.lock         
│ └── .env                # Local 
│
├── frontend/ # (Optional) React, Next.js, etc.
│ ├── app.py
│ ├── Dockerfile
│ └── requirements.txt
│
├── .github/workflows/ 
├── .env.example 
├── docker-compose.yml
└── README.md 
```

---

## Features

- **Document Indexing** from local folders, SQLite DB, or S3
- **LLM Agent Execution** via LangGraph with memory + tools
- **Qdrant Cloud Vector Store** integration
- **CI/CD** via GitHub Actions with Docker & AWS EC2
- Secure `.env` configuration and GitHub Secrets

---

## Quickstart (Dev)

> See `/backend/README.md` and `/frontend/README.md` for detailed setup.

```bash
# 1. Clone the repo
git clone https://github.com/RoboMaroof/LangGraph-Agent-LLMOps-Deployment
cd langgraph-llmops

# 2. Create .env file
cp .env.example .env
# Fill in OpenAI, Qdrant, AWS keys etc.

# 3. Run backend with Docker
cd backend
docker build -t langgraph-app .
docker run --env-file .env -p 8000:8000 langgraph-app

# 4. Run frontend
cd ../frontend
streamlit run app.py
```

---

## CI/CD Workflow

| Step          | Description                         |
|---------------|-------------------------------------|
| Push to `main`| Triggers GitHub Actions             |
| Run Tests     | Executes `pytest` via Poetry        |
| Deploy to EC2 | SCP + SSH + Docker deploy           |
Details in `.github/workflows/ci-cd.yml`

---

## Required Environment Variables
Use `.env.example` as a template:
```env
OPENAI_API_KEY=your-openai-key-here
GROQ_API_KEY=your-groq-key-here
CO_API_KEY=your-coherent-key-here
TAVILY_API_KEY=your-tavily-key-here

# AWS 
AWS_REGION="us-east-1"
S3_BUCKET_NAME="langgraph-docs"
AWS_ACCESS_KEY_ID=your-aws-key-id-here
AWS_SECRET_ACCESS_KEY=your-aws-secret-access-key-here

# Qdrant 
QDRANT_HOST=your-qdrant-host-here
QDRANT_API_KEY=your-qdrant-key-here
QDRANT_COLLECTION="langgraph-rag-vectordb"
```

---

## Testing
Tests live in the `backend/tests/` folder. Run with:
```bash
cd backend
poetry run pytest
```
