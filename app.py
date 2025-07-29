# Load environment variables from .env file
from dotenv import load_dotenv
load_dotenv()
# Server imports
from fastapi import FastAPI, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from models import *
# Backend imports
import time
from services.llm_client import get_embedding, get_llm_response
from services.vectors import ai_search
from services.articles import add_article, add_article_to_db, list_articles

############################################################
##### This is the main app file for the FastAPI server #####
############################################################

app = FastAPI(
    title="Article RAG Chatbot",
    description=(
        "A Retrieval-Augmented Generation (RAG) API for interactive analysis and conversation with a dynamic collection of news articles. "
        "Users can ingest new articles by URL and ask questions, request summaries, extract topics, analyze sentiment, and compare content across sources—all in natural language. "    ),
    version="1.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

### Endpoint for healthcheck ###

@app.get("/")
def root():
    return JSONResponse(
        content={"status": "API is running", "app_name": "Article RAG Chatbot",
                 "version": "1.0", "description": "A Retrieval-Augmented Generation (RAG) API for interactive analysis and conversation with a dynamic collection of news articles."},
        status_code=status.HTTP_200_OK
    )

### Endpoints for article management ###

@app.get("/articles/list")
def get_articles():
    try:
        articles = list_articles()
        return JSONResponse(
            content={"articles": articles},
            status_code=status.HTTP_200_OK
        )
    except Exception as e:
        return JSONResponse(
            content={"error": f"Failed to list articles: {str(e)}"},
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@app.post("/articles/add")
def post_article(article: ArticleAddRequest):
    try:
        new_article = add_article(article.url)
        if not new_article:
            return JSONResponse(
                content={"message": "Article already exists."},
                status_code=status.HTTP_200_OK
            )
        start_time = time.time()
        text_embedding = get_embedding(new_article['content'])
        end_time = time.time()
        print(f"Time taken for embedding: {end_time - start_time} seconds")
        print(f"Embedding for article {new_article['title']} Completed. Usage: {text_embedding[1]} tokens")
        add_article_to_db(text_embedding[0], new_article)
        return JSONResponse(
            content={"article": new_article},
            status_code=status.HTTP_201_CREATED
        )
    except Exception as e:
        return JSONResponse(
            content={"error": f"Failed to add article: {str(e)}"},
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

### Endpoints for AI services ###

@app.post("/ai/query")
def query_ai(text: PromptToLLM):
    try:
        # Embedding the query & Context retrieval
        embedding = get_embedding(text.query)
        context = ai_search(embedding[0])
        articles_context = [r["article"] for r in context]
        start_time = time.time()
        # Sending the query to the LLM
        llm_response = get_llm_response(text.query, articles_context)
        end_time = time.time()
        print(f"Time taken for LLM response: {end_time - start_time} seconds")
        print(f"LLM response usage: {llm_response[1]} tokens")
        return JSONResponse(
            content={
                "response": llm_response[0],
                "context": context,
                "llm_usage": llm_response[1]
            },
            status_code=status.HTTP_200_OK
        )
    except Exception as e:
        return JSONResponse(
            content={"error": f"Failed to query: {str(e)}"},
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
        