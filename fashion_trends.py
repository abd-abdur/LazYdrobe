## Fashion Trends Extractor

# Step 0 - Setting Things Up

# Import modules
from openai import OpenAI
import requests
from bs4 import BeautifulSoup
import random
import time
import os
from dotenv import load_dotenv
import sklearn
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

# OpenAI API
load_dotenv()
OPENAI_API_KEY = os.getenv('OPENAI_API_KEYS')

if OPENAI_API_KEY:
    print(f"The API key is found.")
else:
    print("No API key found in the environment variables.")

openai = OpenAI(api_key=OPENAI_API_KEY)


# Headers to mimic a browser request
headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
}


# Step 1 - Get HTML files
urls = ["https://www.vogue.com/",
             "https://www.vogue.com/article/corduroy-pants#intcid=_vogue-verso-hp-trending_a5d8dd57-5bc8-447f-8eb9-98495b16e7f9_popular4-1",
             "https://www.glamour.com/story/2024-fashion-trends",
             "https://www.whowhatwear.com/fashion/trends/autumn-winter-2024-fashion-trends",
             "https://www.nordstrom.com/browse/content/fall-fashion-trends",
             "https://www.thewardrobeconsultant.com/blog/fall-fashion-trends-2024-style-guide",
             "https://www.whowhatwear.com/fall-winter-fashion-trends-2024",
             "https://www.travelandleisure.com/fall-fashion-trends-travel-clothes-september-2024-8707774",
             
             ]

# Function to extract text from a webpage given a URL with rate-limiting
def extract_text_from_url(url, delay=2):
    """Scrape a URL with a delay between requests to prevent overloading servers."""
    # Headers to mimic a browser request
    headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
    }

    try:
        response = requests.get(url, headers)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, "html.parser")
            # Rate limiting: sleep for `delay` seconds before returning text
            time.sleep(delay)
            return soup.get_text(separator=' ', strip=True)
        else:
            print(f"Failed to retrieve {url}")
            return ""
    except Exception as e:
        print(f"Error occurred while fetching {url}: {e}")
        return ""

# Extract text from each URL with rate limiting (2 seconds between requests)
articles = [extract_text_from_url(url, delay=2) for url in urls]


# Step 2 - Generating article embeddings

# Function to truncate text (and meet LLM token limits)
def truncate_text(text, max_tokens=8000):
    """Truncate the text to fit within the maximum token limit."""
    words = text.split()
    # Estimate that each word is approximately 4 tokens
    max_words = max_tokens // 4
    return " ".join(words[:max_words])

# Function to generate embeddings for each article
def get_embedding(text):
    truncated_text = truncate_text(text)
    response = openai.embeddings.create(
        input=truncated_text,
        model="text-embedding-3-small"
    )
    return response.data[0].embedding

# Generate embeddings for all articles
embeddings = [get_embedding(article) for article in articles]


# Step 3 - Cluster Embeddings

# Function to cluster embeddings using KMeans
def cluster_embeddings(embeddings, n_clusters=5):
    kmeans = KMeans(n_clusters=n_clusters, random_state=42)
    kmeans.fit(embeddings)
    return kmeans.labels_

# Cluster the articles into themes
labels = cluster_embeddings(embeddings, n_clusters=5)


# Step 4 - Cluster summaries

# Function to summarize the articles in each cluster
def extract_refined_trends(text):

    response = openai.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a fashion trends analyst."},
            {"role": "user", "content": f"List and describe the key fashion trends for fall 2024, condensing similar trends across these articles: {text}"}
        ]
    )
    return response.choices[0].message.content

# Combine articles by clusters and extract global trends
clustered_articles = [" ".join([articles[i] for i in range(len(labels)) if labels[i] == label]) for label in set(labels)]
global_trends = extract_refined_trends(" ".join(clustered_articles))


# Step 5 - Keywords
def deduplicate_trends(trends_list):
    vectorizer = TfidfVectorizer(stop_words='english')
    X = vectorizer.fit_transform(trends_list)
    
    # Compute cosine similarity matrix
    similarity_matrix = cosine_similarity(X)
    unique_trends = []
    
    # Set a similarity threshold (e.g., 0.7)
    threshold = 0.7
    added = set()
    
    for i in range(len(trends_list)):
        if i not in added:
            similar_indices = np.where(similarity_matrix[i] > threshold)[0]
            merged_trend = " ".join([trends_list[j] for j in similar_indices if j not in added])
            unique_trends.append(merged_trend)
            added.update(similar_indices)
    
    return unique_trends

# Deduplicate and merge similar trends
unique_trends = deduplicate_trends(global_trends.split('\n'))

trend_dict = {}
for trend in unique_trends:
    if ':' in trend:
        trend_name, trend_description = trend.split(':', 1)
        trend_dict[trend_name.strip()] = trend_description.strip()

# Print final trend dictionary
print(trend_dict)

keys = trend_dict
for key in keys:
    print(key)

print(trend_dict["9. **Leopard Print**"])