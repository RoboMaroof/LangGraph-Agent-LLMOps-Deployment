from llama_index.readers.web import SimpleWebPageReader
from llama_index.core import SimpleDirectoryReader, Document
import sqlite3

def get_documents(source_type, source_path):
    if source_type == "website":
        return SimpleWebPageReader().load_data(urls=[source_path])
    
    elif source_type == "docs":
        return SimpleDirectoryReader(source_path).load_data()
    
    elif source_type == "sql":
        conn = sqlite3.connect(source_path)
        cursor = conn.cursor()

        cursor.execute("SELECT question, answer FROM faq")
        rows = cursor.fetchall()
        conn.close()

        return [
            Document(text=f"Q: {q.strip()}\nA: {a.strip()}")
            for q, a in rows if q and a
        ]

    else:
        raise ValueError("Unsupported source type")
