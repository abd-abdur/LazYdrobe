# fashion_trends.py

import requests
from bs4 import BeautifulSoup
import os
from dotenv import load_dotenv
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity  # Added import
from sqlalchemy.orm import Session
from datetime import datetime
import time
import openai
import logging

from models import FashionTrend

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
DATABASE_URL = os.getenv('DATABASE_URL')  # Not directly used here, but kept for consistency

if not OPENAI_API_KEY:
    logger.error("OPENAI_API_KEY is not set in the environment variables.")
    raise ValueError("OPENAI_API_KEY is not set in the environment variables.")

# Initialize OpenAI client
openai.api_key = OPENAI_API_KEY

# Setup headers for web scraping
headers = {'User-Agent': 'Mozilla/5.0'}

def extract_text_from_url(url, retries=3, delay=2):
    """
    Fetches and extracts text content from a given URL.
    Retries on failure with specified delay between attempts.
    """
    for attempt in range(1, retries + 1):
        try:
            logger.info(f"Fetching URL: {url} (Attempt {attempt})")
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, "html.parser")
                time.sleep(delay)  # Polite delay
                text = soup.get_text(separator=' ', strip=True)
                logger.info(f"Successfully fetched and parsed URL: {url}")
                return text
            else:
                logger.warning(f"Failed to retrieve {url}, attempt {attempt}, status code: {response.status_code}")
        except Exception as e:
            logger.error(f"Error fetching {url} on attempt {attempt}: {e}")
    logger.error(f"Failed to fetch {url} after {retries} attempts.")
    return ""

def truncate_text(text, max_tokens=8000):
    """
    Truncates text to a maximum number of tokens.
    Assumes an average of 4 characters per token for simplicity.
    """
    words = text.split()
    truncated = " ".join(words[:max_tokens // 4])
    logger.debug(f"Truncated text to {len(truncated)} characters.")
    return truncated

def get_embedding(text):
    """
    Generates an embedding for the given text using OpenAI's API.
    """
    truncated_text = truncate_text(text)
    try:
        logger.info("Generating embedding for text.")
        response = openai.Embedding.create(
            model="text-embedding-ada-002",
            input=truncated_text
        )
        embedding = response['data'][0]['embedding']
        logger.info("Successfully generated embedding.")
        return np.array(embedding)
    except Exception as e:
        logger.error(f"Error in embedding generation: {e}")
        return None

def extract_refined_trends(text, max_tokens=4000):
    """
    Uses OpenAI's ChatCompletion to extract refined fashion trends from the text.
    """
    chunks = [text[i:i+max_tokens] for i in range(0, len(text), max_tokens)]
    all_trends = []

    for idx, chunk in enumerate(chunks, start=1):
        try:
            logger.info(f"Extracting trends from chunk {idx}/{len(chunks)}.")
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a fashion trends analyst. Format your response as 'Trend Name: Trend Description' for each trend."},
                    {"role": "user", "content": f"List and describe key fashion trends for fall 2024, separating each trend name from its description with a colon: {chunk}"}
                ],
                max_tokens=1500
            )
            trend_text = response['choices'][0]['message']['content']
            logger.info(f"Extracted trends from chunk {idx}.")
            all_trends.append(trend_text)
        except Exception as e:
            logger.error(f"Error in trend extraction for chunk {idx}: {e}")

    combined_trends = "\n".join(all_trends)
    logger.debug(f"Combined trends text length: {len(combined_trends)} characters.")
    return combined_trends

def deduplicate_trends(trends_list):
    """
    Deduplicates trends based on cosine similarity of their embeddings.
    """
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
            logger.debug(f"Merged trends at indices {similar_indices} into a unique trend.")

    logger.info(f"Deduplicated trends count: {len(unique_trends)}.")
    return unique_trends

def save_trends_to_db(trend_dict, db: Session):
    """
    Saves a dictionary of trends to the database.
    """
    try:
        for trend_name, trend_description in trend_dict.items():
            # Truncate trend_name if it's too long
            if len(trend_name) > 255:
                logger.warning(f"Truncating trend name from '{trend_name}' to 255 characters.")
                trend_name = trend_name[:252] + "..."
            trend = FashionTrend(
                trend_name=trend_name,
                trend_description=trend_description,
                date_added=datetime.utcnow()
            )
            db.add(trend)
        db.commit()
        logger.info("Trends successfully inserted into the database.")
    except Exception as e:
        db.rollback()
        logger.error(f"Failed to insert trends into the database: {e}")
        raise

def preprocess_text(text, max_words=1000):
    """
    Preprocesses text by truncating it to a maximum number of words.
    """
    words = text.split()
    preprocessed = " ".join(words[:max_words])
    logger.debug(f"Preprocessed text to {len(preprocessed)} characters.")
    return preprocessed

def summarize_cluster(text):
    """
    Summarizes a cluster of text using OpenAI's ChatCompletion.
    """
    try:
        logger.info("Summarizing cluster text.")
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Summarize the key fashion trends from the given text in 100 words or less."},
                {"role": "user", "content": text}
            ],
            max_tokens=150
        )
        summary = response['choices'][0]['message']['content']
        logger.info("Successfully summarized cluster text.")
        return summary
    except Exception as e:
        logger.error(f"Error in cluster summarization: {e}")
        return ""

def fetch_and_update_fashion_trends(db: Session):
    """
    Fetches, processes, and updates fashion trends in the database.
    """
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

    logger.info("Starting to fetch articles...")
    articles = [extract_text_from_url(url) for url in urls]
    articles = [article for article in articles if article]  # Filter out empty strings

    if not articles:
        logger.error("No articles were fetched successfully. Exiting fetch process.")
        return

    logger.info(f"Fetched {len(articles)} articles.")

    logger.info("Generating embeddings for articles...")
    embeddings = [get_embedding(article) for article in articles]
    embeddings = np.array([e for e in embeddings if e is not None])

    if len(embeddings) == 0:
        logger.error("No valid embeddings were generated. Exiting fetch process.")
        return

    logger.info(f"Generated {len(embeddings)} embeddings.")

    logger.info("Clustering embeddings...")
    labels = KMeans(n_clusters=5, random_state=42).fit_predict(embeddings)

    logger.info("Clustering completed. Labels assigned.")

    logger.info("Combining clustered articles...")
    clustered_text = [
        " ".join([articles[i] for i in range(len(labels)) if labels[i] == cluster]) 
        for cluster in set(labels)
    ]

    logger.info("Summarizing clusters...")
    summarized_clusters = [summarize_cluster(preprocess_text(text)) for text in clustered_text]

    logger.info("Extracting refined trends...")
    global_trends_text = extract_refined_trends(" ".join(summarized_clusters))

    if not global_trends_text:
        logger.error("No refined trends extracted. Exiting fetch process.")
        return

    trends_list = [trend.strip() for trend in global_trends_text.split('\n') if trend.strip()]

    if not trends_list:
        logger.error("No trends found in the extracted text. Exiting fetch process.")
        return

    logger.info(f"Extracted {len(trends_list)} trends.")

    logger.info("Deduplicating trends...")
    unique_trends = deduplicate_trends(trends_list)

    if not unique_trends:
        logger.error("No unique trends found after deduplication. Exiting fetch process.")
        return

    logger.info(f"Deduplicated to {len(unique_trends)} unique trends.")

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
        save_trends_to_db(trend_dict, db)
    else:
        logger.error("No trends to save to the database.")
