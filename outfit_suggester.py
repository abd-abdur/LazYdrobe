# outfit_suggester.py

import logging
from typing import List, Dict, Any
from sqlalchemy.orm import Session
from models import FashionTrend, EcommerceProduct, OutfitSuggestion, WeatherData, User
from fetch_ebay_data import fetch_similar_ebay_products
import itertools
import random  # Import random for shuffling
import openai
import re
import traceback 


logger = logging.getLogger(__name__)

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

def suggest_outfits(user_id: int, db: Session) -> OutfitSuggestion:
    """
    Suggests outfits based on current weather and fashion trends.
    Fetches similar products from eBay API for each clothing item in the outfits.
    Determines the overall gender of the outfit.
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
        selected_items = select_relevant_clothing_items(db, suitable_clothing_types, user_id)
        logger.info(f"Selected {len(selected_items)} clothing items for outfit suggestions.")
        
        if not selected_items:
            logger.warning("No clothing items found matching the suitable clothing types.")
            raise ValueError("No suitable clothing items found.")
        
        # 5. Shuffle Clothing Items to Ensure Randomization
        random.shuffle(selected_items)
        logger.debug("Shuffled clothing items for random selection.")
        
        # 6. Generate Outfit Combinations
        outfit_combinations = generate_outfit_combinations(selected_items)
        logger.info(f"Generated {len(outfit_combinations)} outfit combinations.")
        
        # 7. Fetch Similar Products from eBay
        enriched_outfits = fetch_similar_products_for_outfits(outfit_combinations, db)
        logger.info("Fetched similar products from eBay for all outfits.")
        
        # 8. Determine Overall Outfit Gender
        outfit_genders = []
        for outfit in enriched_outfits:
            # Collect genders of individual products
            product_genders = []
            for component in outfit:
                gender = component.get('gender')
                if not gender:
                    # Use GPT-4 to determine gender
                    gender = determine_product_gender_gpt(component['product_name'])
                product_genders.append(gender)
            
            # Determine overall outfit gender
            if all(g == 'Male' for g in product_genders):
                outfit_gender = 'Male'
            elif all(g == 'Female' for g in product_genders):
                outfit_gender = 'Female'
            else:
                outfit_gender = 'Unisex'
            
            outfit_genders.append(outfit_gender)
            logger.info(f"Determined outfit gender: {outfit_gender} for outfit with items {[c['product_name'] for c in outfit]}")
        
        # 9. Save Outfit Suggestions to Database
        overall_gender = determine_overall_outfit_gender(outfit_genders)
        
        outfit_suggestion = OutfitSuggestion(
            user_id=user_id,
            outfit_details=enriched_outfits,  # This should be a list of lists containing outfit components with eBay links
            gender=overall_gender  # Aggregate gender
        )
        db.add(outfit_suggestion)
        db.commit()
        db.refresh(outfit_suggestion)
        logger.info(f"Saved outfit suggestion ID {outfit_suggestion.suggestion_id} for user ID {user_id} with gender '{overall_gender}'.")
        
        return outfit_suggestion
            
    except ValueError as ve:
        logger.error(f"Value error occurred: {str(ve)}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error occurred while suggesting outfits for user {user_id}: {str(e)}")
        db.rollback()
        raise

def determine_overall_outfit_gender(outfit_genders: List[str]) -> str:
    """
    Determines the overall gender of the outfit based on individual component genders.
    """
    if all(g == 'Male' for g in outfit_genders):
        return 'Male'
    elif all(g == 'Female' for g in outfit_genders):
        return 'Female'
    else:
        return 'Unisex'


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

def select_relevant_clothing_items(db: Session, clothing_types: List[str], user_id: int) -> List[EcommerceProduct]:
    # Retrieve user's gender
    user = db.query(User).filter(User.user_id == user_id).first()
    user_gender = user.gender.lower() if user.gender else 'unisex'
    logger.debug(f"User ID {user_id} gender: {user_gender}")

    # Map user gender to clothing item gender
    gender_mapping = {
        'male': ['Male', 'Unisex'],
        'female': ['Female', 'Unisex'],
        'unisex': ['Unisex']
    }

    allowed_genders = gender_mapping.get(user_gender, ['Unisex'])
    logger.debug(f"Allowed genders for user {user_id}: {allowed_genders}")

    # Format clothing types to include both singular and plural forms
    clothing_types_formatted = []
    for ctype in clothing_types:
        ctype_cap = ctype.capitalize()
        clothing_types_formatted.append(ctype_cap)
        if not ctype_cap.endswith('s'):
            clothing_types_formatted.append(ctype_cap + 's')
    clothing_types_formatted = list(set(clothing_types_formatted))
    logger.debug(f"Clothing types being searched: {clothing_types_formatted}")

    # Query the database
    products = db.query(EcommerceProduct).filter(
        EcommerceProduct.suggested_item_type.in_(clothing_types_formatted),
        EcommerceProduct.gender.in_(allowed_genders)
    ).all()

    logger.debug(f"Found {len(products)} matching products for user {user_id}.")

    return products



def generate_outfit_combinations(clothing_items: List[EcommerceProduct]) -> List[List[Dict[str, Any]]]:
    categories = {
        'Top': ['T-Shirt', 'Tank Top', 'Sweater', 'Jacket', 'Coat', 'Hoodie'],
        'Bottom': ['Shorts', 'Jeans', 'Dress', 'Pants', 'Trousers'],
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
                'item_id': item.product_id,  # Correct field
                'product_name': item.product_name,
                'image_url': item.image_url,
                'eBay_link': None  # To be filled later
            }
            outfit.append(component)
        outfit_combinations.append(outfit)
        if len(outfit_combinations) >= 5:
            break  # Limit to 5 outfits for practicality
    
    return outfit_combinations

# outfit_suggester.py

def fetch_similar_products_for_outfits(outfit_combinations: List[List[Dict[str, Any]]], db: Session) -> List[List[Dict[str, Any]]]:
    """
    For each clothing item in the outfits, fetch similar products from eBay and add the links.
    """
    for outfit in outfit_combinations:
        for component in outfit:
            product_name = component['product_name']
            try:
                similar_links = fetch_similar_ebay_products(product_name, limit=3)
                component['eBay_link'] = similar_links
                
                # Fetch or determine the gender
                product = db.query(EcommerceProduct).filter(EcommerceProduct.product_id == component['item_id']).first()
                if product and product.gender:
                    component['gender'] = product.gender
                else:
                    # Use GPT-4 to determine gender
                    component['gender'] = determine_product_gender_gpt(product_name)
                
                logger.info(f"Fetched {len(similar_links)} eBay links for '{product_name}'.")
            except Exception as e:
                logger.error(f"Failed to fetch eBay links for '{product_name}': {e}")
                component['eBay_link'] = []  # Assign empty list
                component['gender'] = 'Unisex'  # Default
    return outfit_combinations

