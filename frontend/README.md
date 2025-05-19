# LangGraph Agent Frontend

This is a **Streamlit-based frontend** for interacting with the LangGraph agent backend via a chat interface. It supports uploading custom documents, triggering ingestion into a vector store, and asking questions that invoke an LLM-powered tool-using agent.

---

## Features

- Conversational UI powered by Streamlit
- Upload and index local files (PDF, TXT, DOCX, SQLite DB)
- Ingest content from websites
- Choose between OpenAI or Groq LLMs
- View tools used, intermediate steps, and retrieved data chunks
- Persistent chat session with memory
- Dockerized for easy deployment

---

## Project Structure

```plaintext
frontend/
├── app.py 
├── Dockerfile 
├── requirements.txt # for frontend
└── README.md
```

---

## Requirements

- Python 3.10+
- A running LangGraph backend API (FastAPI, port 8000 by default)

---

## 🔧 Setup (Local)

1. **Install dependencies**:

```bash
pip install -r requirements.txt
```

2. **Run the app**:

```bash
streamlit run app.py
```
Open `http://localhost:8501` in browser.

---

## Run with Docker

```bash
# Build the image
docker build -t langgraph-frontend .

# Run the container
docker run -p 8501:8501 --env-file .env langgraph-frontend
```

The server will:
- Set up Qdrant collection if needed
- Ingest documents if configured
- Preload conversational agent

---

##  How It Works

- Communicates with backend at API_BASE_URL (default: http://localhost:8000)
- Sends prompts to /agent/invoke
- Uploads documents to /vectordb/upload or /vectordb/create
- Displays tools used, intermediate reasoning steps, and final outputs

---