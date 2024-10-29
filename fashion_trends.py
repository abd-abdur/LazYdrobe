# fashion_trends.py

import requests
from bs4 import BeautifulSoup
import os
from dotenv import load_dotenv
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime
import time
from openai import OpenAI

# Load environment variables
load_dotenv()
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
DATABASE_URL = os.getenv('DATABASE_URL')

# Verify that the API key and DATABASE_URL are loaded
if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY is not set in the environment variables.")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL is not set in the environment variables.")

# Initialize OpenAI client
client = OpenAI(api_key=OPENAI_API_KEY)

# Setup headers for web scraping
headers = {'User-Agent': 'Mozilla/5.0'}

# SQLAlchemy setup
Base = declarative_base()

class FashionTrend(Base):
    __tablename__ = 'fashion_trends'
    trend_id = Column(Integer, primary_key=True, autoincrement=True)
    trend_name = Column(String(255), nullable=False)
    trend_description = Column(Text, nullable=False)
    date_added = Column(DateTime, default=datetime.utcnow)

# Create database engine and session
engine = create_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base.metadata.create_all(bind=engine)

def extract_text_from_url(url, retries=3, delay=2):
    for attempt in range(retries):
        try:
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, "html.parser")
                time.sleep(delay)
                return soup.get_text(separator=' ', strip=True)
            else:
                print(f"Failed to retrieve {url}, attempt {attempt + 1}, status code: {response.status_code}")
        except Exception as e:
            print(f"Error fetching {url}: {e}")
    print(f"Failed to fetch {url} after {retries} attempts.")
    return ""

def truncate_text(text, max_tokens=8000):
    words = text.split()
    return " ".join(words[:max_tokens // 4])

def get_embedding(text):
    truncated_text = truncate_text(text)
    try:
        response = client.embeddings.create(
            model="text-embedding-ada-002",
            input=truncated_text
        )
        embedding = response.data[0].embedding
        return np.array(embedding)
    except Exception as e:
        print(f"Error in embedding generation: {e}")
        return None

def extract_refined_trends(text, max_tokens=4000):
    chunks = [text[i:i+max_tokens] for i in range(0, len(text), max_tokens)]
    all_trends = []
    
    for chunk in chunks:
        try:
            response = client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a fashion trends analyst. Summarize key fashion trends for fall 2024 from the given text."},
                    {"role": "user", "content": f"Summarize key fashion trends for fall 2024 from this text: {chunk}"}
                ],
                max_tokens=1500
            )
            all_trends.append(response.choices[0].message.content)
        except Exception as e:
            print(f"Error in trend extraction: {e}")
    
    return "\n".join(all_trends)

def deduplicate_trends(trends_list):
    vectorizer = TfidfVectorizer(stop_words='english')
    X = vectorizer.fit_transform(trends_list)
    similarity_matrix = cosine_similarity(X)
    unique_trends = []
    threshold = 0.7
    added = set()
    
    for i in range(len(trends_list)):
        if i not in added:
            similar_indices = np.where(similarity_matrix[i] > threshold)[0]
            merged_trend = " ".join([trends_list[j] for j in similar_indices if j not in added])
            unique_trends.append(merged_trend)
            added.update(similar_indices)
    
    return unique_trends

def save_trends_to_db(trend_dict):
    session = SessionLocal()
    try:
        for trend_name, trend_description in trend_dict.items():
            # Truncate trend_name if it's too long
            if len(trend_name) > 1000:
                trend_name = trend_name[:997] + "..."
            trend = FashionTrend(trend_name=trend_name, trend_description=trend_description)
            session.add(trend)
        session.commit()
        print("Trends successfully inserted into the database.")
    except Exception as e:
        print(f"Failed to insert trends into the database: {e}")
        session.rollback()
    finally:
        session.close()

def preprocess_text(text, max_words=1000):
    words = text.split()
    return " ".join(words[:max_words])

def summarize_cluster(text):
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Summarize the key fashion trends from the given text in 100 words or less."},
                {"role": "user", "content": text}
            ],
            max_tokens=150
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"Error in cluster summarization: {e}")
        return ""

def main():
    urls = [
        "https://www.vogue.com/",
        "https://www.vogue.com/article/corduroy-pants#intcid=_vogue-verso-hp-trending_a5d8dd57-5bc8-447f-8eb9-98495b16e7f9_popular4-1",
        "https://www.glamour.com/story/2024-fashion-trends",
        "https://www.whowhatwear.com/fashion/trends/autumn-winter-2024-fashion-trends",
        "https://www.nordstrom.com/browse/content/fall-fashion-trends",
        "https://www.thewardrobeconsultant.com/blog/fall-fashion-trends-2024-style-guide",
        "https://www.whowhatwear.com/fall-winter-fashion-trends-2024",
        "https://www.travelandleisure.com/fall-fashion-trends-travel-clothes-september-2024-8707774"
    ]
    
    print("Fetching articles...")
    articles = [extract_text_from_url(url) for url in urls]
    
    print("Generating embeddings...")
    embeddings = [get_embedding(article) for article in articles if article]
    embeddings = np.array([e for e in embeddings if e is not None])
    
    if len(embeddings) == 0:
        print("No valid embeddings were generated. Check the embedding generation process.")
        return
    
    print("Clustering embeddings...")
    labels = KMeans(n_clusters=5, random_state=42).fit_predict(embeddings)
    
    print("Combining clustered articles...")
    clustered_text = [
        " ".join([articles[i] for i in range(len(labels)) if labels[i] == cluster]) 
        for cluster in set(labels)
    ]
    
    print("Summarizing clusters...")
    summarized_clusters = [summarize_cluster(preprocess_text(text)) for text in clustered_text]
    
    print("Extracting refined trends...")
    global_trends_text = extract_refined_trends(" ".join(summarized_clusters))
    
    if not global_trends_text:
        print("No refined trends extracted.")
        return
    
    trends_list = [trend.strip() for trend in global_trends_text.split('\n') if trend.strip()]
    
    if not trends_list:
        print("No trends found in the extracted text.")
        return
    
    print("Deduplicating trends...")
    unique_trends = deduplicate_trends(trends_list)
    
    if not unique_trends:
        print("No unique trends found after deduplication.")
        return
    
    trend_dict = {}
    for trend in unique_trends:
        if ":" in trend:
            parts = trend.split(":", 1)
            trend_name = parts[0].strip()
            trend_description = parts[1].strip()
            trend_dict[trend_name] = trend_description
        else:
            trend_dict[trend] = ""
    
    if trend_dict:
        save_trends_to_db(trend_dict)
    else:
        print("No trends to save to the database.")

if __name__ == "__main__":
    main()