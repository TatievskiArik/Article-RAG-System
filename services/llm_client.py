import os
from openai import AzureOpenAI
import logging

# AZURE_OPENAI_API_VERSION = "2024-02-01"
api_key = os.getenv("AZURE_OPENAI_API_KEY")
api_version = os.getenv("AZURE_OPENAI_API_VERSION")
azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
deployment_name_embedding = os.getenv("AZURE_OPENAI_EMBEDDING_DEPLOYMENT_NAME")
deployment_name_llm = os.getenv("AZURE_OPENAI_CHAT_DEPLOYMENT_NAME")

client = AzureOpenAI(
    api_key=api_key,
    azure_endpoint=azure_endpoint,
    api_version=api_version,
)

async def get_embedding(text: str):
    # Embedding the text using Azure OpenAI
    response = client.embeddings.create(
        input=[text],
        model=deployment_name_embedding
    )
    return response.data[0].embedding, response.usage.total_tokens

async def get_llm_response(prompt: str, articles: list[str]):
    # Create context from articles
    context =""
    for idx, art in enumerate(articles):
        context += (
            f"Article {idx+1}:\n"
            f"Title: {art['title']}\n"
            f"Content:\n{art['content']}\n\n"
        )
    # Generate system message for the LLM
    system_msg = f"""
            You are an AI assistant for articles and research analysis, operating as part of a Retrieval-Augmented Generation (RAG) system.
            You are provided with one or more articles, each with a title, URL, and content.
            Your job is to answer the user's question using ONLY the information from the provided articles below.

            Guidelines:
            - Clearly reference the article(s) (by title) that support your answer.
            - Do not use any external knowledge or make up facts not found in the articles.
            - Ignore navigation, repeated menu items, or language switchers.
            - When summarizing, extracting key topics, or analyzing sentiment, make your reasoning transparent and cite the relevant articles.
            - You MUST return your response in MD format with clear headings and bullet points where appropriate.
            - If the question is not answerable with the provided articles, respond with a response relavent to the question but state that the information is not available in the provided articles or tell him your job if the question is irrlevant to your job.
            - Your only exception is if the question is a greeting or a simple "hello" - in that case, respond with a friendly greeting.

            Articles:
            {context}
        """
    messages = [{"role": "system", "content": system_msg},
                {"role": "user", "content": prompt}]
    try:
        # Sending the query to the LLM
        response = client.chat.completions.create(
            model=deployment_name_llm,
            messages=messages,
            max_tokens=1000
        )
        return response.choices[0].message.content.strip(), response.usage.total_tokens
    except Exception as e:
        logging.error(f"Error in LLM response: {str(e)}")
        raise