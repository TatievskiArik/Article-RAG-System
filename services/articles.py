import os
import json
import uuid
import httpx
import aiofiles
import logging
from bs4 import BeautifulSoup
from filelock import FileLock

LOCK_PATH = os.getenv("DB_PATH") + ".lock"

async def get_page_data(url):
    try:
        async with httpx.AsyncClient() as client:
            res = await client.get(url)
            res.raise_for_status()
            soup = BeautifulSoup(res.content, "html.parser")

        title = soup.title.string.strip() if soup.title and soup.title.string else ""
        for tag in soup(['script', 'style', 'img', 'button', 'nav', 'footer', 'header', 'aside', 'noscript']):
            tag.decompose()

        content = soup.get_text(separator="\n")
        content = "\n".join([line.strip() for line in content.splitlines() if line.strip()])

        return {
            "uid": str(uuid.uuid4()),
            "url": url,
            "title": title,
            "content": content
        }
    except Exception as e:
        logging.error(f"Error fetching data from {url}: {e}")
        raise

async def save_as_json(data, path):
    filename = f"{data['uid']}.json"
    try:
        path = os.path.join(path, filename)
        async with aiofiles.open(path, "w", encoding="utf-8") as f:
            await f.write(json.dumps(data, ensure_ascii=False, indent=2))
        return data
    except Exception as e:
        logging.error(f"Failed to save {filename} locally: {e}")
        raise

async def add_article(url):
    data_dir = os.getenv("DATA_DIR")
    for filename in os.listdir(data_dir):
        if filename.endswith(".json"):
            filepath = os.path.join(data_dir, filename)
            try:
                async with aiofiles.open(filepath, "r", encoding="utf-8") as f:
                    content = await f.read()
                    data = json.loads(content)
                if data.get("url") == url:
                    return None
            except Exception:
                continue
    return await get_page_data(url)

async def add_article_to_db(embedding, article):
    db_path = os.getenv("DB_PATH")
    data_dir = os.getenv("DATA_DIR")
    lock = FileLock(LOCK_PATH)

    try:
        with lock:
            try:
                async with aiofiles.open(db_path, "r", encoding="utf-8") as f:
                    db_content = await f.read()
                    db = json.loads(db_content)
            except Exception as e:
                logging.error(f"Failed to read database: {e}")
                db = []

            record = {
                "embedding": embedding,
                "article": article
            }
            db.append(record)

            try:
                async with aiofiles.open(db_path, "w", encoding="utf-8") as f:
                    await f.write(json.dumps(db, ensure_ascii=False, indent=2))
            except Exception as e:
                logging.error(f"Failed to write to database: {e}")
                raise

    except Exception as e:
        logging.error(f"Error during locked access to vector DB: {e}")
        raise

    await save_as_json(article, data_dir)

async def list_articles():
    data_dir = os.getenv("DATA_DIR")
    articles = []

    for filename in os.listdir(data_dir):
        if filename.endswith(".json"):
            filepath = os.path.join(data_dir, filename)
            try:
                async with aiofiles.open(filepath, "r", encoding="utf-8") as f:
                    content = await f.read()
                    data = json.loads(content)

                title = data.get("title")
                url = data.get("url")
                if title and url:
                    articles.append({"title": title, "url": url})
            except Exception:
                continue

    return articles
