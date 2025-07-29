# Article RAG Chatbot

A Retrieval-Augmented Generation (RAG) API for interactive analysis and conversation with a dynamic collection of news articles. Users can ingest new articles by URL and ask questions, request summaries, extract topics, analyze sentiment, and compare content across sources—all in natural language.

## Features

- **Article Ingestion:** Add articles by URL and store their content and embeddings.
- **Article Listing:** Retrieve a list of all ingested articles.
- **AI Query:** Ask questions about the articles, get summaries, extract topics, analyze sentiment, and compare content using LLM-powered responses.

## Endpoints

| Method | Endpoint            | Description                                 |
|--------|---------------------|---------------------------------------------|
| GET    | `/`                 | Healthcheck/status of the API               |
| GET    | `/articles/list`    | List all ingested articles                  |
| POST   | `/articles/add`     | Add a new article by URL                    |
| POST   | `/ai/query`         | Query the AI about the articles             |

## Getting Started

### Prerequisites

- Python 3.8+
- pip

### Installation

1. **Clone the repository:**
   ```sh
   git clone https://github.com/TatievskiArik/Article-RAG-System
   cd rag-article-chatbot