import os
import json
import uuid
import requests
from bs4 import BeautifulSoup

def get_page_data(url):
    try:
        res = requests.get(url)
        res.raise_for_status()
        soup = BeautifulSoup(res.content, "html.parser")
        # Extract title
        title = soup.title.string.strip() if soup.title and soup.title.string else ""
        # Remove unwanted elements
        for tag in soup(['script', 'style', 'img', 'button', 'nav', 'footer', 'header', 'aside', 'noscript']):
            tag.decompose()
        # Get visible text only
        content = soup.get_text(separator="\n")
        # Clean up excessive empty lines and strip
        content = "\n".join([line.strip() for line in content.splitlines() if line.strip()])
        return {
            "uid": str(uuid.uuid4()),
            "url": url,
            "title": title,
            "content": content
        }
    except Exception as e:
        print(f"Failed to retrieve data from {url}: {e}")
        raise

def save_as_json(data, path):
    filename = f"{data['uid']}.json"
    try:
        path = os.path.join(path, filename)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return data
    except Exception as e:
        print(f"Failed to save {filename}: {e}")
        raise

def add_article(url):
    data_dir = os.getenv("DATA_DIR")
    for filename in os.listdir(data_dir):
        if filename.endswith(".json"):
            filepath = os.path.join(data_dir, filename)
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    data = json.load(f)
                if data.get("url") == url:
                    return None
            except Exception:
                continue
    new_article = get_page_data(url)
    return new_article

def add_article_to_db(embedding, article):
    db_path = os.getenv("DB_PATH")
    data_dir = os.getenv("DATA_DIR")
    try:
        with open(db_path, "r", encoding="utf-8") as f:
            db = json.load(f)
    except Exception as e:
        print(f"Failed to read database: {e}")
    record = {
        "embedding": embedding,
        "article": article
    }
    db.append(record)
    try:
        with open(db_path, "w", encoding="utf-8") as f:
            json.dump(db, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"Failed to write to database: {e}")
        raise
    save_as_json(article, data_dir)

def list_articles():
    data_dir = os.getenv("DATA_DIR")
    print(data_dir)
    articles = []
    for filename in os.listdir(data_dir):
        if filename.endswith(".json"):
            filepath = os.path.join(data_dir, filename)
            with open(filepath, "r", encoding="utf-8") as f:
                try:
                    data = json.load(f)
                    title = data.get("title")
                    url = data.get("url")
                    if title and url:
                        articles.append({"title": title, "url": url})
                except Exception:
                    continue
    print(articles)
    return articles