# fetch_ebay_data.py

import os
import requests
from sqlalchemy.orm import Session
from models import EcommerceProduct
from dotenv import load_dotenv
from datetime import datetime
import logging
import argparse
from typing import List, Optional

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Database configuration
DATABASE_URL = os.getenv("DATABASE_URL")
EBAY_APP_ID = os.getenv("EBAY_APP_ID")

if not DATABASE_URL:
    logger.error("DATABASE_URL is not set in the environment variables.")
    exit(1)

if not EBAY_APP_ID:
    logger.error("EBAY_APP_ID is not set in the environment variables.")
    exit(1)

# Create the SQLAlchemy engine
from sqlalchemy import create_engine

engine = create_engine(DATABASE_URL, echo=False)

# Create a configured "Session" class
from sqlalchemy.orm import sessionmaker

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def fetch_ebay_products(search_query: str, limit: int = 50) -> List[dict]:
    """
    Fetch products from eBay API based on the search_query.
    Handles pagination to retrieve up to 'limit' items.
    """
    ebay_api_url = "https://svcs.ebay.com/services/search/FindingService/v1"
    headers = {
        "X-EBAY-SOA-SECURITY-APPNAME": EBAY_APP_ID,
        "X-EBAY-SOA-OPERATION-NAME": "findItemsByKeywords",
        "X-EBAY-SOA-SERVICE-VERSION": "1.0.0",
        "X-EBAY-SOA-RESPONSE-DATA-FORMAT": "JSON",
    }
    entries_per_page = min(limit, 100)  # eBay allows max 100 per page
    items_fetched = []
    page_number = 1
    total_pages = 1  # Initialize to enter the loop

    while len(items_fetched) < limit and page_number <= total_pages:
        params = {
            "keywords": search_query,
            "paginationInput.entriesPerPage": entries_per_page,
            "paginationInput.pageNumber": page_number,
            "itemFilter(0).name": "HideDuplicateItems",
            "itemFilter(0).value": "true",
        }

        try:
            response = requests.get(ebay_api_url, headers=headers, params=params)
            response.raise_for_status()
            data = response.json()

            # Check API response acknowledgment
            search_response = data.get('findItemsByKeywordsResponse', [{}])[0]
            ack = search_response.get('ack', [None])[0]
            if ack != 'Success':
                error_message = search_response.get('errorMessage', [{}])[0].get('error', [{}])[0].get('message', ['Unknown error'])[0]
                logger.error(f"eBay API Error: {error_message}")
                break

            # Determine total pages from the response
            pagination = search_response.get('paginationOutput', [{}])[0]
            total_pages = int(pagination.get('totalPages', [1])[0])

            # Extract items
            items = search_response.get('searchResult', [{}])[0].get('item', [])
            logger.info(f"Fetched {len(items)} items from eBay for query '{search_query}' on page {page_number}.")

            for item in items:
                if len(items_fetched) >= limit:
                    break
                item_data = {
                    'ebay_item_id': item.get("itemId", [None])[0],
                    'product_name': item.get("title", [None])[0],
                    'suggested_item_type': item.get("primaryCategory", [{}])[0].get("categoryName", [None])[0],
                    'price': float(item.get("sellingStatus", [{}])[0].get("currentPrice", [{}])[0].get("__value__", 0.0)),
                    'currency': item.get("sellingStatus", [{}])[0].get("currentPrice", [{}])[0].get("__currency__", "USD"),
                    'product_url': item.get("viewItemURL", [None])[0],
                    'image_url': item.get("galleryURL", [None])[0],
                    'date_suggested': datetime.utcnow(),
                    'user_id': None  # Set to appropriate user_id if necessary
                }

                # Validate essential fields
                if not all([item_data['ebay_item_id'], item_data['product_name'], item_data['product_url']]):
                    logger.warning(f"Missing essential data for item: {item_data}")
                    continue

                items_fetched.append(item_data)

            page_number += 1

        except requests.exceptions.HTTPError as http_err:
            logger.error(f"HTTP error occurred: {http_err}")
            break
        except Exception as err:
            logger.error(f"An unexpected error occurred: {err}")
            break

    logger.info(f"Total items fetched: {len(items_fetched)}")
    return items_fetched

def fetch_similar_ebay_products(product_name: str, limit: int = 3) -> List[str]:
    """
    Fetches similar products from eBay based on the product name.
    Returns a list of eBay product URLs.
    """
    ebay_api_url = "https://svcs.ebay.com/services/search/FindingService/v1"
    headers = {
        "X-EBAY-SOA-SECURITY-APPNAME": EBAY_APP_ID,
        "X-EBAY-SOA-OPERATION-NAME": "findItemsByKeywords",
        "X-EBAY-SOA-SERVICE-VERSION": "1.0.0",
        "X-EBAY-SOA-RESPONSE-DATA-FORMAT": "JSON",
    }

    params = {
        "keywords": product_name,
        "paginationInput.entriesPerPage": limit,
        "paginationInput.pageNumber": 1,
        "itemFilter(0).name": "HideDuplicateItems",
        "itemFilter(0).value": "true",
    }

    try:
        response = requests.get(ebay_api_url, headers=headers, params=params)
        response.raise_for_status()
        data = response.json()

        # Check API response acknowledgment
        search_response = data.get('findItemsByKeywordsResponse', [{}])[0]
        ack = search_response.get('ack', [None])[0]
        if ack != 'Success':
            error_message = search_response.get('errorMessage', [{}])[0].get('error', [{}])[0].get('message', ['Unknown error'])[0]
            logger.error(f"eBay API Error: {error_message}")
            return []

        # Extract items
        items = search_response.get('searchResult', [{}])[0].get('item', [])
        ebay_links = [item.get("viewItemURL", [None])[0] for item in items if item.get("viewItemURL", [None])[0]]

        logger.info(f"Fetched {len(ebay_links)} similar products from eBay for '{product_name}'.")
        return ebay_links

    except requests.exceptions.HTTPError as http_err:
        logger.error(f"HTTP error occurred while fetching eBay products: {http_err}")
    except Exception as err:
        logger.error(f"An unexpected error occurred while fetching eBay products: {err}")

    return []

def insert_products(session: Session, items: List[dict]):
    """
    Insert fetched products into the ecommerce_products table.
    Utilizes bulk operations for efficiency.
    """
    if not items:
        logger.info("No items to insert.")
        return

    # Prepare list of EcommerceProduct instances
    new_products = []
    for item in items:
        # Check for duplicates
        existing_product = session.query(EcommerceProduct).filter(
            EcommerceProduct.ebay_item_id == item['ebay_item_id']
        ).first()
        if existing_product:
            logger.info(f"Product '{item['product_name']}' (eBay ID: {item['ebay_item_id']}) already exists. Skipping.")
            continue

        new_product = EcommerceProduct(
            ebay_item_id=item['ebay_item_id'],
            product_name=item['product_name'],
            suggested_item_type=item['suggested_item_type'],
            price=item['price'],
            product_url=item['product_url'],
            image_url=item['image_url'],
            date_suggested=item['date_suggested'],
            user_id=item['user_id']
        )
        new_products.append(new_product)

    if not new_products:
        logger.info("No new products to insert after checking for duplicates.")
        return

    # Bulk insert
    session.bulk_save_objects(new_products)

    # Commit the transaction
    try:
        session.commit()
        logger.info(f"Successfully inserted {len(new_products)} new products into ecommerce_products.")
    except Exception as e:
        session.rollback()
        logger.error(f"Error inserting products: {e}")
