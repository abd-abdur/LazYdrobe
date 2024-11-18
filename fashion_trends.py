# fashion_trends.py

import requests
from bs4 import BeautifulSoup
import os
from dotenv import load_dotenv
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from sqlalchemy.orm import Session, scoped_session, sessionmaker
from datetime import datetime
import time
import openai
import logging
from typing import List, Optional
import re
import string
import traceback
from sqlalchemy import create_engine
import spacy

# Initialize SpaCy English model
nlp = spacy.load("en_core_web_sm")

from models import FashionTrend, EcommerceProduct  
from constants import ALLOWED_CATEGORIES

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
DATABASE_URL = os.getenv('DATABASE_URL') 
EBAY_APP_ID = os.getenv("EBAY_APP_ID")

if not OPENAI_API_KEY:
    logger.error("OPENAI_API_KEY is not set in the environment variables.")
    raise ValueError("OPENAI_API_KEY is not set in the environment variables.")

if not EBAY_APP_ID:
    logger.error("EBAY_APP_ID is not set in the environment variables.")
    raise ValueError("EBAY_APP_ID is not set in the environment variables.")

# Initialize OpenAI client
openai.api_key = OPENAI_API_KEY

# Setup headers for web scraping
headers = {'User-Agent': 'Mozilla/5.0'}

# Constants
MAX_EMBEDDING_TOKENS = 8000
MAX_SUMMARY_TOKENS = 4000
MAX_SEARCH_PHRASE_WORDS = 5
SIMILARITY_THRESHOLD = 0.7
ELBOW_METHOD_MAX_K = 10
EBAY_API_MAX_ENTRIES_PER_PAGE = 100
VALIDATION_LIMIT = 1  # Number of items to fetch for validation

def debug_ecommerce_product():
    """
    Debug function to print attributes of EcommerceProduct.
    """
    ecommerce_product = EcommerceProduct()
    print("EcommerceProduct Attributes:", ecommerce_product.__dict__)
    
def categorize_clothing_item_gpt(product_name: str) -> Optional[str]:
    """
    Categorizes a clothing item into one of the predefined categories using GPT-4.
    
    Args:
        product_name (str): The name or description of the product.
        
    Returns:
        Optional[str]: The categorized clothing type or None if categorization fails.
    """
    try:
        logger.info(f"Categorizing product: '{product_name}' using GPT-4.")
        prompt = (
            "You are an expert fashion assistant. Categorize the following clothing item into one of the predefined categories.\n"
            f"Predefined Categories: {', '.join(ALLOWED_CATEGORIES)}\n"
            f"Item Description: {product_name}\n"
            "Category:"
        )
        response = openai.ChatCompletion.create(
            model="gpt-4",  # Correct model name
            messages=[
                {"role": "system", "content": "You are an expert fashion assistant."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=10,
            temperature=0.0,  # Ensure deterministic output
        )
        category = response.choices[0].message.content.strip()
        # Validate the category
        if category in ALLOWED_CATEGORIES:
            logger.info(f"Categorized '{product_name}' as '{category}'.")
            return category
        else:
            logger.warning(f"GPT-4 returned invalid category '{category}' for product '{product_name}'.")
            return None
    except openai.error.OpenAIError as e:
        logger.error(f"OpenAI API error while categorizing product '{product_name}': {e}")
        logger.debug(traceback.format_exc())
        return None
    except Exception as e:
        logger.error(f"Unexpected error while categorizing product '{product_name}': {e}")
        logger.debug(traceback.format_exc())
        return None


def determine_product_gender_gpt(product_name: str) -> str:
    """
    Determines the gender category using GPT-4 based on the product name.
    Returns 'Male', 'Female', or 'Unisex'.
    Ensures that 'Unisex' is only used if explicitly stated.
    Discards the clothing if it cannot be determined as 'Male' or 'Female'.
    """
    try:
        logger.info(f"Determining gender for product: '{product_name}' using GPT-4.")
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are an expert in fashion trends and gender categorization. "
                        "Determine whether the following product is designed for 'Male', 'Female', or is 'Unisex'. "
                        "Respond with only one of these three options. "
                        "Only categorize as 'Unisex' if it is explicitly stated as such."
                    )
                },
                {
                    "role": "user",
                    "content": f"Product Name: {product_name}"
                }
            ],
            max_tokens=10,
            temperature=0.2,
        )
        gender = response['choices'][0]['message']['content'].strip()
        gender = gender.capitalize()
        if gender not in ['Male', 'Female', 'Unisex']:
            logger.warning(f"GPT-4 returned unexpected gender '{gender}' for product '{product_name}'. Defaulting to 'Unisex'.")
            return 'Unisex'
        logger.info(f"GPT-4 classified product '{product_name}' as '{gender}'.")
        return gender
    except Exception as e:
        logger.error(f"Error determining gender with GPT-4 for product '{product_name}': {e}")
        logger.debug(traceback.format_exc())
        return 'Unisex'  # Default to 'Unisex' in case of failure
    
def extract_text_from_url(url: str, retries: int = 3, delay: int = 2) -> str:
    """
    Fetches and extracts text content from a given URL.
    Retries on failure with specified delay between attempts.
    
    Args:
        url (str): The URL to fetch.
        retries (int): Number of retry attempts.
        delay (int): Delay in seconds between retries.
        
    Returns:
        str: Extracted text or empty string if failed.
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
            logger.debug(traceback.format_exc())
    logger.error(f"Failed to fetch {url} after {retries} attempts.")
    return ""

def truncate_text(text: str, max_tokens: int = MAX_EMBEDDING_TOKENS) -> str:
    """
    Truncates text to a maximum number of tokens.
    Assumes an average of 4 characters per token for simplicity.
    
    Args:
        text (str): The text to truncate.
        max_tokens (int): Maximum number of tokens.
        
    Returns:
        str: Truncated text.
    """
    words = text.split()
    truncated = " ".join(words[:max_tokens // 4])
    logger.debug(f"Truncated text to {len(truncated)} characters.")
    return truncated

def get_embedding(text: str) -> Optional[np.ndarray]:
    """
    Generates an embedding for the given text using OpenAI's API.
    
    Args:
        text (str): The input text.
        
    Returns:
        Optional[np.ndarray]: The embedding vector or None if failed.
    """
    truncated_text = truncate_text(text, MAX_EMBEDDING_TOKENS)
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
        logger.debug(traceback.format_exc())
        return None

def extract_refined_trends(text: str, max_tokens: int = MAX_SUMMARY_TOKENS) -> str:
    """
    Uses OpenAI's ChatCompletion to extract refined fashion trends from the text.
    Formats each trend as 'Trend Name: Trend Description'.
    
    Args:
        text (str): The combined summarized cluster texts.
        max_tokens (int): Maximum number of tokens per chunk.
        
    Returns:
        str: Combined trends text.
    """
    chunks = [text[i:i+max_tokens] for i in range(0, len(text), max_tokens)]
    all_trends = []

    for idx, chunk in enumerate(chunks, start=1):
        try:
            logger.info(f"Extracting trends from chunk {idx}/{len(chunks)}.")
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are a fashion trends analyst. "
                            "Format your response as 'Trend Name: Trend Description' for each trend."
                        )
                    },
                    {
                        "role": "user",
                        "content": f"List and describe key fashion trends for fall 2024, separating each trend name from its description with a colon: {chunk}"
                    }
                ],
                max_tokens=1500,
                temperature=0.5
            )
            trend_text = response['choices'][0]['message']['content']
            logger.info(f"Extracted trends from chunk {idx}.")
            all_trends.append(trend_text)
        except Exception as e:
            logger.error(f"Error in trend extraction for chunk {idx}: {e}")
            logger.debug(traceback.format_exc())

    combined_trends = "\n".join(all_trends)
    logger.debug(f"Combined trends text length: {len(combined_trends)} characters.")
    return combined_trends

def deduplicate_trends(trends_list: List[str]) -> List[str]:
    """
    Deduplicates trends based on cosine similarity of their TF-IDF vectors.
    
    Args:
        trends_list (List[str]): List of trend descriptions.
        
    Returns:
        List[str]: List of unique trends.
    """
    vectorizer = TfidfVectorizer(stop_words='english')
    X = vectorizer.fit_transform(trends_list)
    similarity_matrix = cosine_similarity(X)
    unique_trends = []
    threshold = SIMILARITY_THRESHOLD
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

def generate_search_keywords(description: str, min_keywords: int = 3, max_keywords: int = 5) -> Optional[str]:
    """
    Extracts key fashion keywords from the trend description using OpenAI's ChatCompletion.
    Ensures that the generated keywords do not contain any punctuation and are suitable for eBay search queries.
    
    Args:
        description (str): The trend description text.
        min_keywords (int): Minimum number of keywords to extract.
        max_keywords (int): Maximum number of keywords to extract.
        
    Returns:
        Optional[str]: A space-separated string of extracted keywords or None if failed.
    """
    try:
        logger.info("Generating search keywords using GPT.")
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are an expert in fashion trend analysis. "
                        "Extract the most relevant keywords or short phrases from the following trend description. "
                        "Ensure that the keywords are suitable for eBay product searches and do not contain any punctuation."
                    )
                },
                {
                    "role": "user",
                    "content": f"Extract {min_keywords} to {max_keywords} key fashion keywords from this trend description without any punctuation: {description}"
                }
            ],
            max_tokens=60,
            temperature=0.5
        )
        
        # Extract and clean the response
        keywords = response['choices'][0]['message']['content'].strip()
        
        # Remove all punctuation using str.translate
        translator = str.maketrans('', '', string.punctuation)
        keywords = keywords.translate(translator)
        
        # Additionally, remove any non-ASCII characters
        keywords = keywords.encode('ascii', 'ignore').decode()
        
        # Replace multiple spaces with a single space
        keywords = re.sub(r'\s+', ' ', keywords)
        
        # Ensure the number of keywords is within the specified range
        keyword_list = keywords.split()
        if len(keyword_list) < min_keywords:
            logger.warning(f"Generated keywords have less than {min_keywords} words. Attempting to regenerate.")
            # Optionally, implement regeneration logic here
        elif len(keyword_list) > max_keywords:
            keyword_list = keyword_list[:max_keywords]
            keywords = ' '.join(keyword_list)
        
        logger.info(f"Generated search keywords: '{keywords}'")
        return keywords
    except Exception as e:
        logger.error(f"Error generating search keywords: {e}")
        logger.debug(traceback.format_exc())
        return None


def save_trends_to_db(trend_dict: dict, db: Session, max_regenerations: int = 2):
    """
    Saves a dictionary of trends to the database, generating and validating search phrases.
    
    Args:
        trend_dict (dict): A dictionary where keys are trend names and values are trend descriptions.
        db (Session): SQLAlchemy session object.
        max_regenerations (int): Maximum number of times to attempt regeneration if validation fails.
    """
    try:
        for trend_name, trend_description in trend_dict.items():
            # Truncate trend_name if it's too long
            if len(trend_name) > 255:
                logger.warning(f"Truncating trend name from '{trend_name}' to 255 characters.")
                trend_name = trend_name[:252] + "..."
            
            # Initialize regeneration attempt counter
            regeneration_attempts = 0
            search_keywords = None
            
            while regeneration_attempts <= max_regenerations:
                # Generate search keywords using GPT
                search_keywords = generate_search_keywords(trend_description)
                if not search_keywords:
                    logger.warning(f"Failed to generate search keywords for trend '{trend_name}'. Skipping.")
                    break
                
                # Validate the search phrase
                if validate_search_phrase(search_keywords):
                    logger.info(f"Search phrase '{search_keywords}' validated successfully.")
                    break  # Validated successfully
                else:
                    regeneration_attempts += 1
                    logger.warning(f"Validation failed for search phrase '{search_keywords}'. Attempt {regeneration_attempts} of {max_regenerations}.")
                    search_keywords = None  # Reset search_keywords for regeneration
            
            if not search_keywords:
                logger.warning(f"Could not generate a valid search phrase for trend '{trend_name}' after {max_regenerations} attempts. Skipping.")
                continue  # Move to the next trend
            
            # Check if the trend already exists to avoid duplicates
            existing_trend = db.query(FashionTrend).filter(
                FashionTrend.trend_name == trend_name,
                FashionTrend.trend_search_phrase == search_keywords
            ).first()
            if existing_trend:
                logger.info(f"Trend '{trend_name}' with search phrase '{search_keywords}' already exists. Skipping insertion.")
                continue
            
            # Insert the validated trend into the database
            trend = FashionTrend(
                trend_name=trend_name,
                trend_description=trend_description,
                trend_search_phrase=search_keywords,
                date_added=datetime.utcnow()
            )
            db.add(trend)
            logger.info(f"Inserted trend '{trend_name}' with search phrase '{search_keywords}' into the database.")
        
        db.commit()
        logger.info("Trends successfully inserted into the database.")
    except Exception as e:
        db.rollback()
        logger.error(f"Failed to insert trends into the database: {e}")
        logger.debug(traceback.format_exc())
        raise


def preprocess_text(text: str, max_words: int = 1000) -> str:
    """
    Preprocesses text by truncating it to a maximum number of words.
    
    Args:
        text (str): The text to preprocess.
        max_words (int): Maximum number of words.
        
    Returns:
        str: Preprocessed text.
    """
    words = text.split()
    preprocessed = " ".join(words[:max_words])
    logger.debug(f"Preprocessed text to {len(preprocessed)} characters.")
    return preprocessed

def summarize_cluster(text: str) -> str:
    """
    Summarizes a cluster of text using OpenAI's ChatCompletion.
    
    Args:
        text (str): The text to summarize.
        
    Returns:
        str: Summary of the cluster.
    """
    try:
        logger.info("Summarizing cluster text.")
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a fashion trend summarizer. "
                        "Summarize the key fashion trends from the given text in 100 words or less."
                    )
                },
                {
                    "role": "user",
                    "content": text
                }
            ],
            max_tokens=150,
            temperature=0.5
        )
        summary = response['choices'][0]['message']['content'].strip()
        logger.info("Successfully summarized cluster text.")
        return summary
    except Exception as e:
        logger.error(f"Error in cluster summarization: {e}")
        logger.debug(traceback.format_exc())
        return ""

def validate_search_phrase(search_phrase: str) -> bool:
    """
    Validates the search phrase by performing a mock search on eBay.
    Returns True if results are found, False otherwise.
    
    Args:
        search_phrase (str): The search keywords.
        
    Returns:
        bool: Validation result.
    """
    try:
        # Perform a test search with a limited number of items
        products = fetch_ebay_products(search_phrase, limit=VALIDATION_LIMIT)
        if products:
            logger.info(f"Validation successful for search phrase: '{search_phrase}'")
            return True
        else:
            logger.warning(f"Validation failed for search phrase: '{search_phrase}'")
            return False
    except Exception as e:
        logger.error(f"Error during validation of search phrase '{search_phrase}': {e}")
        logger.debug(traceback.format_exc())
        return False

def determine_optimal_clusters(embeddings: np.ndarray, max_k: int = ELBOW_METHOD_MAX_K) -> int:
    """
    Determines the optimal number of clusters using the Elbow Method.
    """
    num_samples = len(embeddings)
    if num_samples < 2:
        logger.error("Insufficient samples for clustering.")
        raise ValueError("At least 2 samples are required for clustering.")

    max_k = min(max_k, num_samples)  # Adjust max_k to the number of samples
    inertia = []
    K = range(2, max_k + 1)

    for k in K:
        kmeans = KMeans(n_clusters=k, random_state=42)
        kmeans.fit(embeddings)
        inertia.append(kmeans.inertia_)

    # Use a heuristic to find the elbow point (or return a default value)
    optimal_k = max(2, min(5, max_k))  # Simple heuristic for demonstration
    logger.info(f"Determined optimal number of clusters: {optimal_k}")
    return optimal_k

def fetch_ebay_products(search_query: str, limit: int = 50, max_pages: int = 10) -> List[dict]:
    """
    Fetches products from eBay API based on the search_query.
    Returns a list of dictionaries containing product details.
    
    Args:
        search_query (str): The search keywords.
        limit (int): Number of products to fetch.
        max_pages (int): Maximum number of pages to fetch per query.
        
    Returns:
        List[dict]: A list of product dictionaries.
    """
    ebay_api_url = "https://svcs.ebay.com/services/search/FindingService/v1"
    headers_api = {
        "X-EBAY-SOA-SECURITY-APPNAME": EBAY_APP_ID,
        "X-EBAY-SOA-OPERATION-NAME": "findItemsByKeywords",
        "X-EBAY-SOA-SERVICE-VERSION": "1.0.0",
        "X-EBAY-SOA-RESPONSE-DATA-FORMAT": "JSON",
    }
    params = {
        "keywords": search_query,
        "paginationInput.entriesPerPage": min(limit, EBAY_API_MAX_ENTRIES_PER_PAGE),  # eBay allows max 100 per page
        "paginationInput.pageNumber": 1,
        "outputSelector": "SellerInfo",
    }

    products = []
    try:
        logger.info(f"Making request to eBay API with search query: '{search_query}'")
        response = requests.get(ebay_api_url, headers=headers_api, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        # Check API response acknowledgment
        search_response = data.get('findItemsByKeywordsResponse', [{}])[0]
        ack = search_response.get('ack', [None])[0]
        if ack != 'Success':
            error_message = search_response.get('errorMessage', [{}])[0].get('error', [{}])[0].get('message', ['Unknown error'])[0]
            logger.error(f"eBay API Error: {error_message}")
            return products

        # Extract items
        items = search_response.get('searchResult', [{}])[0].get('item', [])
        logger.info(f"Fetched {len(items)} items from eBay for query '{search_query}'.")

        for item in items:
            ebay_item_id = item.get("itemId", [None])[0]
            product_name = item.get("title", [None])[0]
            category_name = item.get("primaryCategory", [{}])[0].get("categoryName", [None])[0]
            price = float(item.get("sellingStatus", [{}])[0].get("currentPrice", [{}])[0].get("__value__", 0.0))
            currency = item.get("sellingStatus", [{}])[0].get("currentPrice", [{}])[0].get("__currency__", "USD")
            product_url = item.get("viewItemURL", [None])[0]
            image_url = item.get("galleryURL", [None])[0]
            

            # Skip items with missing essential data
            if not all([ebay_item_id, product_name, product_url]):
                logger.warning(f"Skipping item due to missing data: {item}")
                continue

            # Map category to clothing type
            clothing_type = categorize_clothing_item_gpt(category_name)
            gender = determine_product_gender_gpt(product_name)

            product = {
                'ebay_item_id': ebay_item_id,
                'product_name': product_name,
                'suggested_item_type': clothing_type,
                'price': price,
                'currency': currency,
                'product_url': product_url,
                'image_url': image_url,
                'date_suggested': datetime.utcnow(),
                'user_id': None,  # Set to appropriate user_id if necessary
                'gender': gender
            }

            products.append(product)

            if len(products) >= limit:
                break

        # Handle pagination if more items are needed
        pagination_output = search_response.get('paginationOutput', [{}])[0]
        total_entries = int(pagination_output.get('totalEntries', [0])[0])
        total_pages = int(pagination_output.get('totalPages', [1])[0])
        logger.info(f"Total entries: {total_entries}, Total pages: {total_pages}")

        current_page = 1
        while len(products) < limit and current_page < total_pages and current_page < max_pages:
            current_page += 1
            params["paginationInput.pageNumber"] = current_page
            logger.info(f"Fetching page {current_page} for query '{search_query}'")
            response = requests.get(ebay_api_url, headers=headers_api, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            search_response = data.get('findItemsByKeywordsResponse', [{}])[0]
            ack = search_response.get('ack', [None])[0]
            if ack != 'Success':
                error_message = search_response.get('errorMessage', [{}])[0].get('error', [{}])[0].get('message', ['Unknown error'])[0]
                logger.error(f"eBay API Error on page {current_page}: {error_message}")
                break

            items = search_response.get('searchResult', [{}])[0].get('item', [])
            logger.info(f"Fetched {len(items)} items from eBay on page {current_page} for query '{search_query}'.")

            if not items:
                logger.info(f"No more items found on page {current_page}. Stopping pagination.")
                break  # Exit if no items are found on the current page

            for item in items:
                ebay_item_id = item.get("itemId", [None])[0]
                product_name = item.get("title", [None])[0]
                category_name = item.get("primaryCategory", [{}])[0].get("categoryName", [None])[0]
                price = float(item.get("sellingStatus", [{}])[0].get("currentPrice", [{}])[0].get("__value__", 0.0))
                currency = item.get("sellingStatus", [{}])[0].get("currentPrice", [{}])[0].get("__currency__", "USD")
                product_url = item.get("viewItemURL", [None])[0]
                image_url = item.get("galleryURL", [None])[0]

                # Skip items with missing essential data
                if not all([ebay_item_id, product_name, product_url]):
                    logger.warning(f"Skipping item due to missing data: {item}")
                    continue

                gender = determine_product_gender_gpt(product_name)

                product = {
                    'ebay_item_id': ebay_item_id,
                    'product_name': product_name,
                    'suggested_item_type': clothing_type,
                    'price': price,
                    'currency': currency,
                    'product_url': product_url,
                    'image_url': image_url,
                    'date_suggested': datetime.utcnow(),
                    'user_id': None, # Set to appropriate user_id if necessary
                    'gender': gender
                }

                products.append(product)

                if len(products) >= limit:
                    break

        logger.info(f"Total products fetched: {len(products)}")
        return products

    except requests.exceptions.HTTPError as http_err:
        logger.error(f"HTTP error occurred: {http_err}")
        logger.debug(traceback.format_exc())
    except Exception as e:
        logger.error(f"Error fetching products from eBay: {e}")
        logger.debug(traceback.format_exc())
    return products


def fetch_and_insert_trend_products(db: Session, trend: FashionTrend, limit_per_trend: int = 10):
    """
    Fetches products for a given trend's search phrase and inserts them into the database.
    Ensures no duplicates based on ebay_item_id.
    
    Args:
        db (Session): SQLAlchemy session object.
        trend (FashionTrend): The fashion trend object.
        limit_per_trend (int): Maximum number of products to fetch per trend.
    """
    search_phrase = trend.trend_search_phrase
    if not search_phrase:
        logger.warning(f"Trend ID {trend.trend_id} does not have a search phrase. Skipping.")
        return

    logger.info(f"Fetching products for trend '{trend.trend_name}' with search phrase '{search_phrase}'.")
    
    # Fetch products from eBay with a maximum of 10 pages
    products = fetch_ebay_products(search_phrase, limit=limit_per_trend, max_pages=10)
    
    logger.info(f"Fetched {len(products)} products for trend '{trend.trend_name}'.")

    # Insert products into the database
    inserted_count = 0
    for product in products:
        # Check for duplicates based on ebay_item_id
        existing_product = db.query(EcommerceProduct).filter(
            EcommerceProduct.ebay_item_id == product['ebay_item_id']
        ).first()
        if existing_product:
            logger.info(f"Product '{product['product_name']}' (eBay ID: {product['ebay_item_id']}) already exists. Skipping.")
            continue

        try:
            new_product = EcommerceProduct(
                ebay_item_id=product['ebay_item_id'],
                product_name=product['product_name'],
                suggested_item_type=product['suggested_item_type'],
                price=product['price'],
                currency=product['currency'],
                product_url=product['product_url'],
                image_url=product['image_url'],
                date_suggested=product['date_suggested'],
                user_id=product['user_id'],
                gender=product['gender'] 
            )
            db.add(new_product)
            inserted_count += 1
        except Exception as e:
            logger.error(f"Error creating EcommerceProduct instance: {e}")
            logger.debug(traceback.format_exc())
            continue

    try:
        db.commit()
        logger.info(f"Inserted {inserted_count} new products for trend '{trend.trend_name}'.")
    except Exception as e:
        db.rollback()
        logger.error(f"Error inserting products for trend '{trend.trend_name}': {e}")
        logger.debug(traceback.format_exc())


def populate_ecommerce_products(db: Session, limit_per_trend: int = 10):
    """
    Populates the ecommerce_products table based on the current fashion trends.
    
    Args:
        db (Session): SQLAlchemy session object.
        limit_per_trend (int): Maximum number of products to fetch per trend.
    """
    trends = db.query(FashionTrend).filter(FashionTrend.trend_search_phrase.isnot(None)).all()
    logger.info(f"Found {len(trends)} trends with search phrases.")

    for trend in trends:
        try:
            fetch_and_insert_trend_products(db, trend, limit_per_trend)
        except Exception as e:
            logger.error(f"Failed to fetch and insert products for trend '{trend.trend_name}': {e}")
            logger.debug(traceback.format_exc())
            continue  # Proceed with the next trend

def fetch_and_update_fashion_trends(db: Session):
    """
    Fetches, processes, and updates fashion trends in the database.
    
    Args:
        db (Session): SQLAlchemy session object.
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

    logger.info("Determining optimal number of clusters...")
    optimal_k = determine_optimal_clusters(embeddings, ELBOW_METHOD_MAX_K)

    logger.info("Clustering embeddings...")
    kmeans = KMeans(n_clusters=optimal_k, random_state=42)
    labels = kmeans.fit_predict(embeddings)

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

def main():
    """
    Main function to execute the fashion trends fetching and product population.
    """
    # Initialize database session (assuming SQLAlchemy sessionmaker is set up)
    engine = create_engine(DATABASE_URL, pool_size=20, max_overflow=10, pool_timeout=30, pool_recycle=1800)
    SessionFactory = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    SessionScoped = scoped_session(SessionFactory)
    db = SessionScoped()

    try:
        # Fetch and update fashion trends
        fetch_and_update_fashion_trends(db)

        # Populate ecommerce products based on the updated trends
        populate_ecommerce_products(db, limit_per_trend=10)
    finally:
        db.remove()  # Use remove() with scoped_session to properly handle sessions

if __name__ == "__main__":
    main()
