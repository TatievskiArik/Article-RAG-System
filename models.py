from pydantic import BaseModel
from typing import Optional

class ArticleAddRequest(BaseModel):
    url: str

class PromptToLLM(BaseModel):
    query: str

class Article(BaseModel):
    uid: str
    url: str
    title: Optional[str] = None
    content: Optional[str] = None