from typing import List, Optional, Any
from pydantic import BaseModel

class ArticleAddRequest(BaseModel):
    url: str

class PromptToLLM(BaseModel):
    query: str

class Article(BaseModel):
    uid: str
    url: str
    title: Optional[str] = None
    content: Optional[str] = None

class RootResponse(BaseModel):
    status: str
    app_name: str
    version: str
    description: str

class ArticlesListResponse(BaseModel):
    articles: List[Article]

class ArticleAddResponse(BaseModel):
    article: Article

class MessageResponse(BaseModel):
    message: str

class ErrorResponse(BaseModel):
    error: str

class ContextArticleScore(BaseModel):
    article: Article
    score: float

class AIQueryResponse(BaseModel):
    response: str
    context: List[ContextArticleScore]
    llm_usage: int
