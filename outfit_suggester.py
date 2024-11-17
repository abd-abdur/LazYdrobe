# outfit_suggester.py

import logging
from typing import List, Dict, Any
from sqlalchemy.orm import Session
from models import FashionTrend, EcommerceProduct, OutfitSuggestion, WeatherData
from fetch_ebay_data import fetch_similar_ebay_products
import itertools

logger = logging.getLogger(__name__)

def suggest_outfits(user_id: int, db: Session) -> OutfitSuggestion:
    """
    Suggests outfits based on current weather and fashion trends.
    Fetches similar products from eBay API for each clothing item in the outfits.
    """
    logger.info(f"Starting outfit suggestion for user_id={user_id}")
    
    try:
        # 1. Retrieve Current Weather
        weather = get_latest_weather(db, user_id)
        if not weather:
            logger.warning(f"No weather data available for user ID {user_id}.")
            raise ValueError("Weather data not available.")
        logger.info(f"Retrieved weather data: {weather.special_condition}, Temp Max: {weather.temp_max}°F")
        
        # 2. Retrieve Current Fashion Trends
        trends = get_current_fashion_trends(db)
        if not trends:
            logger.warning("No fashion trends available.")
            raise ValueError("Fashion trends not available.")
        logger.info(f"Retrieved {len(trends)} fashion trends.")
        
        # 3. Determine Suitable Clothing Types
        suitable_clothing_types = determine_clothing_types(weather, trends)
        logger.info(f"Determined suitable clothing types: {suitable_clothing_types}")
        
        # 4. Select Relevant Clothing Items from Ecommerce Products
        selected_items = select_relevant_clothing_items(db, suitable_clothing_types)
        logger.info(f"Selected {len(selected_items)} clothing items for outfit suggestions.")
        
        if not selected_items:
            logger.warning("No clothing items found matching the suitable clothing types.")
            raise ValueError("No suitable clothing items found.")
        
        # 5. Generate Outfit Combinations
        outfit_combinations = generate_outfit_combinations(selected_items)
        logger.info(f"Generated {len(outfit_combinations)} outfit combinations.")
        
        # 6. Fetch Similar Products from eBay
        enriched_outfits = fetch_similar_products_for_outfits(outfit_combinations)
        logger.info("Fetched similar products from eBay for all outfits.")
        
        # 7. Save Outfit Suggestions to Database
        outfit_suggestion = OutfitSuggestion(
            user_id=user_id,
            outfit_details=enriched_outfits  # This should be a list of lists containing outfit components with eBay links
        )
        db.add(outfit_suggestion)
        db.commit()
        db.refresh(outfit_suggestion)
        logger.info(f"Saved outfit suggestion ID {outfit_suggestion.suggestion_id} for user ID {user_id}.")
        
        return outfit_suggestion
    
    except ValueError as ve:
        logger.error(f"ValueError during outfit suggestion: {ve}")
        raise ve  # To be handled by the API endpoint
    except Exception as e:
        logger.error(f"Unexpected error during outfit suggestion: {e}")
        raise ValueError("Failed to suggest outfits.")  # Generic error message

def get_latest_weather(db: Session, user_id: int) -> WeatherData:
    """
    Retrieves the latest weather data for the user from the database.
    """
    return db.query(WeatherData).filter(WeatherData.user_id == user_id).order_by(WeatherData.date.desc()).first()

def get_current_fashion_trends(db: Session) -> List[FashionTrend]:
    """
    Retrieves the latest fashion trends from the database.
    """
    return db.query(FashionTrend).order_by(FashionTrend.date_added.desc()).limit(10).all()

def determine_clothing_types(weather: WeatherData, trends: List[FashionTrend]) -> List[str]:
    """
    Determines suitable clothing types based on weather conditions and fashion trends.
    """
    clothing_types = set()
    
    # Analyze weather conditions
    temp_max = weather.temp_max
    temp_min = weather.temp_min
    condition = weather.special_condition.lower()
    
    if temp_max > 75:
        clothing_types.update(['Shorts', 'Tank Top', 'Sandals'])
    elif 60 < temp_max <= 75:
        clothing_types.update(['Jeans', 'T-Shirt', 'Sneakers'])
    elif 45 < temp_max <= 60:
        clothing_types.update(['Sweater', 'Jacket', 'Boots'])
    else:
        clothing_types.update(['Coat', 'Hoodie', 'Heavy Boots'])
    
    # Incorporate fashion trends
    for trend in trends:
        trend_clothing = extract_clothing_types_from_trend(trend.trend_description)
        clothing_types.update(trend_clothing)
    
    return list(clothing_types)

def extract_clothing_types_from_trend(description: str) -> List[str]:
    """
    Extracts clothing types from a trend description using simple keyword matching.
    """
    keywords = ['jacket', 'sweater', 'dress', 'jeans', 't-shirt', 'shorts', 'boots', 'sandals', 'sneakers', 'coat', 'hoodie', 'tank top', 'heavy boots']
    extracted = [word.capitalize() for word in keywords if word in description.lower()]
    return extracted

def select_relevant_clothing_items(db: Session, clothing_types: List[str]) -> List[EcommerceProduct]:
    """
    Selects clothing items from the ecommerce_products table that match the desired clothing types.
    """
    return db.query(EcommerceProduct).filter(EcommerceProduct.suggested_item_type.in_(clothing_types)).all()

def generate_outfit_combinations(clothing_items: List[EcommerceProduct]) -> List[List[Dict[str, Any]]]:
    """
    Generates outfit combinations by grouping clothing items logically.
    Each outfit is a list of clothing components (e.g., top, bottom, shoes).
    """
    # Define categories (e.g., top, bottom, shoes)
    categories = {
        'Top': ['T-Shirt', 'Tank Top', 'Sweater', 'Jacket', 'Coat', 'Hoodie'],
        'Bottom': ['Shorts', 'Jeans', 'Dress'],
        'Shoes': ['Sandals', 'Sneakers', 'Boots', 'Heavy Boots']
    }
    
    # Group items by category
    grouped_items = {category: [] for category in categories}
    for item in clothing_items:
        for category, types in categories.items():
            if item.suggested_item_type in types:
                grouped_items[category].append(item)
                break  # Assume each item belongs to only one category
    
    # Remove categories with no items
    grouped_items = {k: v for k, v in grouped_items.items() if v}
    
    if not grouped_items:
        logger.warning("No clothing items available to form outfits.")
        return []
    
    # Generate all possible combinations taking one item from each category
    outfit_combinations = []
    category_order = list(grouped_items.keys())
    all_combinations = itertools.product(*[grouped_items[cat] for cat in category_order])
    
    for combination in all_combinations:
        outfit = []
        for idx, item in enumerate(combination):
            component = {
                'clothing_type': category_order[idx],
                'product_id': item.product_id,
                'product_name': item.product_name,
                'image_url': item.image_url,
                'eBay_link': None  # To be filled later
            }
            outfit.append(component)
        outfit_combinations.append(outfit)
        if len(outfit_combinations) >= 5:
            break  # Limit to 5 outfits for practicality
    
    return outfit_combinations

def fetch_similar_products_for_outfits(outfit_combinations: List[List[Dict[str, Any]]]) -> List[List[Dict[str, Any]]]:
    """
    For each clothing item in the outfits, fetch similar products from eBay and add the links.
    """
    for outfit in outfit_combinations:
        for component in outfit:
            product_name = component['product_name']
            try:
                similar_links = fetch_similar_ebay_products(product_name, limit=3)
                component['eBay_link'] = similar_links
                logger.info(f"Fetched {len(similar_links)} eBay links for '{product_name}'.")
            except Exception as e:
                logger.error(f"Failed to fetch eBay links for '{product_name}': {e}")
                component['eBay_link'] = []  # Assign empty list
    return outfit_combinations
