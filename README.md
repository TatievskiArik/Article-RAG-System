# Article RAG Chatbot

A Retrieval-Augmented Generation (RAG) API for interactive analysis and conversation with a dynamic collection of news articles. Users can ingest new articles by URL and ask questions, request summaries, extract topics, analyze sentiment, and compare content across sources—all in natural language.

---

## About This Project

- **Modern Python API development** with FastAPI and async programming for high concurrency.
- **Robust data handling** with atomic file operations and concurrency-safe mechanisms.
- **Integration with Azure OpenAI** for embeddings and LLM-powered responses.
- **Vector search and chunking** for scalable retrieval-augmented generation.
- **Containerization** for easy deployment and reproducibility.

---

## Features

- **Article Ingestion:** Add articles by URL and store their content and embeddings.
- **Article Listing:** Retrieve a list of all ingested articles.
- **AI Query:** Ask questions about the articles, get summaries, extract topics, analyze sentiment, and compare content using LLM-powered responses.
- **Async Endpoints:** All endpoints are fully async for maximum performance.
- **Atomic & Safe Writes:** Vector DB writes are locked to prevent race conditions.
- **Dockerized:** Ready for deployment in any environment.

---

## Endpoints

| Method | Endpoint            | Description                                 |
|--------|---------------------|---------------------------------------------|
| GET    | `/`                 | Healthcheck/status of the API               |
| GET    | `/articles/list`    | List all ingested articles                  |
| POST   | `/articles/add`     | Add a new article by URL                    |
| POST   | `/ai/query`         | Query the AI about the articles             |

---

## Getting Started

### Prerequisites

- Python 3.8+
- pip

### Installation & Setup

1. **Clone the repository:**
    ```sh
    git clone https://github.com/TatievskiArik/Article-RAG-System.git
    cd rag-article-chatbot
    pip install -r requirements.txt
    ```

2. **Environment Variables:**
   - In the project root, create a `.env` file with the following variables (replace values as needed):

     ```
     DATA_DIR=./data
     DB_PATH=./vectorDB.json
     AZURE_OPENAI_API_KEY=your-azure-openai-api-key
     AZURE_OPENAI_ENDPOINT=your-azure-openai-endpoint
     AZURE_OPENAI_CHAT_DEPLOYMENT_NAME=your-chat-deployment-name
     AZURE_OPENAI_EMBEDDING_DEPLOYMENT_NAME=your-embedding-deployment-name
     AZURE_OPENAI_API_VERSION=2024-XX-XX
     ```

3. **Run the API:**
    ```sh
    uvicorn app:app --reload
    ```

---

## Docker Deployment

You can run the Article RAG Chatbot API in a container using Docker.

### Build the Docker image

```sh
docker build -t rag-article-chatbot .
```

### Run the container

```sh
docker run -p 8000:8000 --env-file .env rag-article-chatbot
```

This will start the API server at `http://localhost:8000`.

**Note:**  
- Make sure your `.env` file is present in the project root and contains all required environment variables.
- You can run tests inside the container by adding `pytest` to your requirements and running:
  ```sh
  docker run --env-file .env rag-article-chatbot pytest
  ```

---

## 🛠️ Improvements & Recommendations

**File I/O and Concurrency**
- **Thread Safety:** Consider using a database (SQLite, PostgreSQL) for concurrent access instead of JSON files.

**Performance**
- **Vector Search:** For larger datasets, use a vector database (e.g., FAISS, Pinecone) instead of iterating over JSON.
- **Batch Processing:** If you expect bulk article ingestion, process in batches.

**AI & Backend Engineering**
- **Extensible Design:** Easily add new endpoints, AI features, or swap out vector/LLM providers.
