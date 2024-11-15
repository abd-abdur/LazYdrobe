# outfit_suggester.py

import logging
from typing import List, Dict, Any
from sqlalchemy.orm import Session
from models import WardrobeItem, FashionTrend, WeatherData, OutfitSuggestion
from fetch_ebay_data import fetch_similar_ebay_products  

logger = logging.getLogger(__name__)


def suggest_outfits(user_id: int, db: Session) -> OutfitSuggestion:
    logger.info(f"Starting outfit suggestion for user_id={user_id}")
    
    try:
        # 1. Retrieve Current Weather
        weather = db.query(WeatherData).filter(WeatherData.user_id == user_id).order_by(WeatherData.date.desc()).first()
        if not weather:
            logger.warning(f"No weather data found for user ID {user_id}.")
            raise ValueError("Weather data not available.")
        logger.info(f"Retrieved weather data for user ID {user_id}: {weather.special_condition}")

        # 2. Retrieve Latest Fashion Trends
        trends = db.query(FashionTrend).order_by(FashionTrend.date_added.desc()).limit(10).all()
        if not trends:
            logger.warning("No fashion trends available.")
            raise ValueError("Fashion trends not available.")
        logger.info(f"Retrieved {len(trends)} fashion trends.")

        # 3. Retrieve User's Wardrobe Items
        wardrobe_items = db.query(WardrobeItem).filter(WardrobeItem.user_id == user_id).all()
        if not wardrobe_items:
            logger.warning(f"No wardrobe items found for user ID {user_id}.")
            raise ValueError("Wardrobe is empty.")
        logger.info(f"Retrieved {len(wardrobe_items)} wardrobe items for user ID {user_id}.")

        # 4. Determine Suitable Clothing Types Based on Weather and Trends
        suitable_clothing_types = determine_clothing_types(weather, trends)
        logger.info(f"Determined suitable clothing types: {suitable_clothing_types}")

        # 5. Select Wardrobe Items Matching the Criteria
        selected_items = select_wardrobe_items(wardrobe_items, suitable_clothing_types)
        logger.info(f"Selected {len(selected_items)} wardrobe items for outfits.")

        if not selected_items:
            logger.warning("No wardrobe items match the suitable clothing types.")
            raise ValueError("No suitable wardrobe items found.")

        # 6. Generate Outfit Combinations
        outfit_combinations = generate_outfits(selected_items)
        logger.info(f"Generated {len(outfit_combinations)} outfit combinations.")

        # 7. Fetch Similar Products from eBay
        for outfit_idx, outfit in enumerate(outfit_combinations, start=1):
            logger.info(f"Processing outfit combination {outfit_idx}/{len(outfit_combinations)}")
            for component_idx, component in enumerate(outfit, start=1):
                logger.info(f"Processing component {component_idx}/{len(outfit)}: {component['product_name']}")
                if component['eBay_link'] is None:
                    try:
                        similar_products = fetch_similar_ebay_products(component['product_name'])
                        component['eBay_link'] = similar_products
                        logger.info(f"Fetched {len(similar_products)} eBay links for {component['product_name']}")
                    except Exception as e:
                        logger.error(f"Failed to fetch eBay products for {component['product_name']}: {e}")
                        component['eBay_link'] = []  # Assign empty list

        # 8. Save Outfit Suggestion to Database
        outfit_suggestion = OutfitSuggestion(
            user_id=user_id,
            outfit_details=outfit_combinations
        )
        db.add(outfit_suggestion)
        db.commit()
        db.refresh(outfit_suggestion)
        logger.info(f"Saved outfit suggestion ID {outfit_suggestion.suggestion_id} for user ID {user_id}.")

        return outfit_suggestion

    except Exception as e:
        logger.error(f"Failed to create outfit suggestion for user_id={user_id}: {e}")
        raise ValueError("Failed to suggest outfits.")  # Raise a general error or custom message as needed




def determine_clothing_types(weather: WeatherData, trends: List[FashionTrend]) -> List[str]:
    """
    Determines suitable clothing types based on weather and fashion trends.
    """
    clothing_types = set()

    # Simple logic based on temperature
    if weather.temp_max > 25:
        clothing_types.update(['T-shirt', 'Shorts', 'Sandals'])
    elif 15 < weather.temp_max <= 25:
        clothing_types.update(['Shirt', 'Jeans', 'Sneakers'])
    else:
        clothing_types.update(['Jacket', 'Sweater', 'Boots'])

    # Incorporate fashion trends
    for trend in trends:
        # Assuming trend.trend_name contains clothing types or relevant keywords
        trend_clothing = extract_clothing_types_from_trend(trend.trend_description)
        clothing_types.update(trend_clothing)

    return list(clothing_types)

def extract_clothing_types_from_trend(description: str) -> List[str]:
    """
    Extracts clothing types from a trend description using simple keyword matching.
    For a more advanced approach, consider NLP techniques.
    """
    keywords = ['jacket', 'sweater', 'dress', 'jeans', 't-shirt', 'shorts', 'boots', 'sandals', 'sneakers', 'shirt']
    extracted = [word.capitalize() for word in keywords if word in description.lower()]
    return extracted

def select_wardrobe_items(wardrobe_items: List[WardrobeItem], clothing_types: List[str]) -> List[Dict[str, Any]]:
    """
    Selects wardrobe items that match the desired clothing types.
    """
    selected = []
    for item in wardrobe_items:
        if item.clothing_type in clothing_types:
            selected.append({
                'clothing_type': item.clothing_type,
                'item_id': item.item_id,
                'product_name': item.tags[0] if item.tags else item.clothing_type,  # Assuming tags contain product names
                'image_url': item.image_url,
                'eBay_link': None  # Initialize eBay_link
            })
    return selected

def generate_outfits(selected_items: List[Dict[str, Any]]) -> List[List[Dict[str, Any]]]:
    """
    Generates outfit combinations from selected wardrobe items.
    """
    # Simple approach: group items by clothing type and create combinations
    from itertools import product

    clothing_types = list(set([item['clothing_type'] for item in selected_items]))
    grouped_items = {ct: [item for item in selected_items if item['clothing_type'] == ct] for ct in clothing_types}

    # Create all possible combinations taking one item from each clothing type
    outfit_combinations = list(product(*grouped_items.values()))

    # Limit the number of outfits to, say, 5
    return [list(comb) for comb in outfit_combinations[:5]]
