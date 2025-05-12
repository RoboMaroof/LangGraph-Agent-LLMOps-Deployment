import requests
import streamlit as st
import os
from dotenv import load_dotenv
import uuid

load_dotenv()
BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")

if 'chat_session_id' not in st.session_state:
    st.session_state.chat_session_id = str(uuid.uuid4())
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'vector_store_ready' not in st.session_state:
    st.session_state.vector_store_ready = False

st.set_page_config(page_title="Langchain RAG Agent", layout="centered")
st.title('🧠 LangGraph Agent Chat App')

with st.expander("📥 Ingest Custom Data into Vector Store (if required)", expanded=False):
    st.markdown("##### Select a Data Source")
    source_type = st.selectbox("Select data source type:", ["website", "docs", "sql"])

    if source_type == "website":
        source_path = st.text_input("Enter URL path:")
        if st.button("Ingest and Update Vector Store"):
            if source_path:
                with st.spinner("Ingesting and updating vector store..."):
                    response = requests.post(f"{BASE_URL}/vectordb/create", json={
                        "source_type": source_type,
                        "source_path": source_path
                    })
                    if response.ok and "message" in response.json():
                        st.success("✅ Vector store updated successfully!")
                        st.session_state.vector_store_ready = True
                    else:
                        st.error(f"❌ Failed to update vector store. {response.json().get('error', '')}")
            else:
                st.warning("⚠️ Please enter a valid source path.")
    else:
        uploaded_file = st.file_uploader("Upload a file (PDF, TXT, DOCX, DB, etc.):", type=["pdf", "txt", "docx", "db"])
        if st.button("Upload and Ingest File"):
            if uploaded_file:
                with st.spinner("Uploading and indexing file..."):
                    files = {"file": (uploaded_file.name, uploaded_file.getvalue())}
                    response = requests.post(f"{BASE_URL}/vectordb/upload", files=files)
                    if response.ok and "message" in response.json():
                        st.success(f"✅ {response.json()['message']}")
                        st.session_state.vector_store_ready = True
                    else:
                        st.error(f"❌ Upload failed. {response.json().get('error', '')}")
            else:
                st.warning("⚠️ Please upload a valid file.")

st.markdown("---")
st.markdown("## 🤖 Chat with Your Documents")

if st.button("🧹 Clear Chat"):
    st.session_state.chat_history = []
    st.session_state.chat_session_id = str(uuid.uuid4())
    st.success("Chat cleared!")

model_label_map = {
    "OpenAI (gpt-4o-mini)": "openai:gpt-4o-mini",
    "Groq (qwen-qwq-32b)": "groq:qwen-qwq-32b"
}
model_choice_label = st.selectbox("Choose a model:", list(model_label_map.keys()))
model_choice = model_label_map[model_choice_label]

def render_response(response_data):
    if "final_output" in response_data:
        st.chat_message("assistant").markdown(response_data["final_output"])

        with st.expander("🛠 Tools Used", expanded=False):
            if response_data.get("tools_used"):
                for tool in response_data["tools_used"]:
                    st.markdown(f"- {tool}")
            else:
                st.markdown("_None_")

        with st.expander("📄 Retrieved Data", expanded=False):
            if response_data.get("retrieved_chunks"):
                for chunk in response_data["retrieved_chunks"]:
                    st.markdown(f"**Tool**: `{chunk.get('tool')}` | **Type**: `{chunk.get('type')}`")
                    st.code(chunk.get("data", ""))
            else:
                st.markdown("_None_")

        with st.expander("🔎 Intermediate Steps", expanded=False):
            if response_data.get("intermediate_steps"):
                for idx, step in enumerate(response_data["intermediate_steps"], 1):
                    st.markdown(f"**Step {idx}**: `{step.get('type', 'unknown')}`")
                    if step["type"] == "ai_tool_call":
                        st.markdown(f"- Tool: `{step.get('tool')}`")
                        st.markdown(f"- Arguments: `{step.get('args')}`")
                    elif step["type"] == "tool_response":
                        st.markdown(f"- Tool: `{step.get('tool')}`")
                        st.code(step.get("content", ""))
                    elif step["type"] == "ai_final_response":
                        st.markdown(f"- Final Response: {step.get('content')}")
                    else:
                        st.markdown(f"- Content: `{step.get('content', '')}`")
            else:
                st.markdown("_None_")

for chat in st.session_state.chat_history:
    st.chat_message("user").markdown(chat["user"])
    render_response(chat["response"])

prompt = st.chat_input("Enter your question...")
if prompt:
    st.chat_message("user").markdown(prompt)

    with st.spinner("Thinking..."):
        try:
            response = requests.post(
                f"{BASE_URL}/agent/invoke",
                json={
                    "input": {"input": prompt},
                    "model": model_choice,
                    "session_id": st.session_state.chat_session_id
                }
            )
            response.raise_for_status()
            data = response.json()

            st.session_state.chat_history.append({
                "user": prompt,
                "response": data
            })
            render_response(data)

        except Exception as e:
            st.error(f"❌ Error occurred: {e}")
