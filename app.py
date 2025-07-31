# Load environment variables from .env file
from dotenv import load_dotenv
load_dotenv()
# Server imports
from fastapi import FastAPI, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from models import *
# Backend imports
from services.llm_client import get_embedding, get_llm_response
from services.vectors import ai_search
from services.articles import add_article, add_article_to_db, list_articles
# Auditing and performance imports
import logging
import time

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

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logging.info("FastAPI server started with CORS enabled for all origins.")

### Endpoint for healthcheck ###
@app.get("/", response_model=RootResponse)
async def root():
    return JSONResponse(
        content={"status": "API is running", "app_name": "Article RAG Chatbot",
                 "version": "1.0", "description": "A Retrieval-Augmented Generation (RAG) API for interactive analysis and conversation with a dynamic collection of news articles."},
        status_code=status.HTTP_200_OK
    )

### Endpoints for article management ###
@app.get("/articles/list", response_model=ArticlesListResponse, responses={500: {"model": ErrorResponse}})
async def get_articles():
    try:
        articles = await list_articles()
        return JSONResponse(
            content={"articles": articles},
            status_code=status.HTTP_200_OK
        )
    except Exception as e:
        return JSONResponse(
            content={"error": f"Failed to list articles: {str(e)}"},
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@app.post("/articles/add", response_model=ArticleAddResponse, responses={200: {"model": MessageResponse}, 500: {"model": ErrorResponse}})
async def post_article(article: ArticleAddRequest):
    try:
        new_article = await add_article(article.url)
        if not new_article:
            return JSONResponse(
                content={"message": "Article already exists."},
                status_code=status.HTTP_208_ALREADY_REPORTED
            )
        start_time = time.time()
        text_embedding = await get_embedding(new_article['content'])
        end_time = time.time()
        logging.info(f"Time taken for embedding: {end_time - start_time} seconds")
        logging.info(f"Embedding for article {new_article['title']} completed. Usage: {text_embedding[1]} tokens")
        await add_article_to_db(text_embedding[0], new_article)
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
@app.post("/ai/query", response_model=AIQueryResponse, responses={500: {"model": ErrorResponse}})
async def query_ai(text: PromptToLLM):
    if (not text.query) or (text.query.strip() == ""):
        return JSONResponse(
            content={"error": "Query text cannot be empty."},
            status_code=status.HTTP_400_BAD_REQUEST
        )
    try:
        embedding = await get_embedding(text.query)
        context = await ai_search(embedding[0])
        articles_context = [r["article"] for r in context]
        start_time = time.time()
        llm_response = await get_llm_response(text.query, articles_context)
        end_time = time.time()
        logging.info(f"LLM response time: {end_time - start_time} seconds")
        logging.info(f"LLM response usage: {llm_response[1]} tokens")   
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
