# outfit_suggester.py

import logging
from typing import List, Dict, Any
from sqlalchemy.orm import Session
from models import FashionTrend, EcommerceProduct, OutfitSuggestion, WeatherData, User
from fetch_ebay_data import fetch_similar_ebay_products
import itertools
import random 
import openai
import re
import traceback 
from typing import Optional
import itertools
from typing import List, Dict, Any
import inflect

p = inflect.engine()

from constants import ALLOWED_CATEGORIES

logger = logging.getLogger(__name__)


def singularize(word: str) -> str:
    return p.singular_noun(word) or word

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
        
        # 5. Shuffle Clothing Items to Ensure Randomization (Optional: Already handled in generate_outfit_combinations)
        # random.shuffle(selected_items)
        # logger.debug("Shuffled clothing items for random selection.")
        
        # 6. Generate Outfit Combinations with Unique 'Top' Items
        outfit_combinations = generate_outfit_combinations(selected_items)
        if not outfit_combinations:
            raise ValueError("Insufficient clothing items across categories to form outfits. Please add more items to your wardrobe.")
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
        clothing_types.update(['Shorts', 'Tank Top', 'Sandals', 'Sneakers', 'Shoe', 'Skirts', 'Blouse', 'Dress'])
    elif 60 < temp_max <= 75:
        clothing_types.update(['Jeans', 'T-Shirt', 'Sneakers', 'Shoe', 'Light Jacket', 'Blouse', 'Skirts', 'Dress', 'Leggings'])
    elif 45 < temp_max <= 60:
        clothing_types.update(['Sweater', 'Jacket', 'Boots', 'Sneakers', 'Shoe', 'Blazer', 'Pants', 'Jeans', 'Hoodie'])
    else:
        clothing_types.update(['Coat', 'Hoodie', 'Insulated Boots', 'Shoe', 'Scarf', 'Sweater', 'Pants', 'Leggings', 'Blazer'])

        
    # Incorporate fashion trends
    for trend in trends:
        trend_clothing = extract_clothing_types_from_trend(trend.trend_description)
        clothing_types.update(trend_clothing)
    
    return list(clothing_types)

def extract_clothing_types_from_trend(description: str) -> List[str]:
    """
    Extracts clothing types from a trend description using simple keyword matching.
    """
    keywords = ['jacket', 'blouse', 'skirt', 'sweater', 'dress', 'jeans', 't-shirt', 'shorts', 'boots', 'sandals', 'sneakers', 'coat', 'hoodie', 'tank top', 'heavy boots']
    extracted = [word.capitalize() for word in keywords if word in description.lower()]
    return extracted

def select_relevant_clothing_items(db: Session, clothing_types: List[str], user_id: int) -> List[EcommerceProduct]:
    """
    Selects relevant clothing items based on clothing types and user gender.
    
    Args:
        db (Session): Database session.
        clothing_types (List[str]): List of specific clothing types.
        user_id (int): ID of the user.
        
    Returns:
        List[EcommerceProduct]: List of relevant clothing items.
    """
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

    # Format clothing types to lowercase to match the mapping function
    clothing_types_formatted = [ctype.lower().strip() for ctype in clothing_types]
    logger.debug(f"Clothing types being searched: {clothing_types_formatted}")

    # Query the database for products matching the specific categories and allowed genders
    products = db.query(EcommerceProduct).filter(
        EcommerceProduct.suggested_item_type.in_(clothing_types_formatted),
        EcommerceProduct.gender.in_(allowed_genders)
    ).all()

    logger.debug(f"Number of products fetched: {len(products)}")
    for product in products:
        logger.debug(f"Fetched product_id={product.product_id}, name='{product.product_name}', type='{product.suggested_item_type}', gender='{product.gender}'")

    category_distribution = {}
    for product in products:
        category = map_product_to_category(product.suggested_item_type)
        if category:
            category_distribution[category] = category_distribution.get(category, 0) + 1
            logger.debug(f"Product '{product.product_name}' categorized under '{category}'")
        else:
            logger.warning(f"Product '{product.product_name}' with type '{product.suggested_item_type}' could not be mapped to a general category.")

    logger.info(f"Category distribution: {category_distribution}")

    return products



def map_product_to_category(suggested_item_type: str) -> Optional[str]:
    """
    Maps a specific clothing item type to a general category.
    
    Args:
        suggested_item_type (str): The specific type of clothing item.
        
    Returns:
        Optional[str]: The general category ('Top', 'Bottom', 'Shoes') or None if no mapping is found.
    """
    # Singularize and lowercase the suggested_item_type to handle plural forms and case
    singular_type = singularize(suggested_item_type).strip().lower()
    suggested_item_type_lower = suggested_item_type.strip().lower()
    
    categories = {
    'Top': ['t-shirt', 'tank top', 'sweater', 'jacket', 'coat', 'hoodie', 'blazer', 'blouse', 'cardigan'],
    'Bottom': ['shorts', 'jeans', 'jean', 'dress', 'skirt', 'pants', 'trouser', 'cargo pants', 'corduroy pants'],
    'Shoes': ['sandals', 'sneakers', 'boots', 'heavy boot', 'shoe', 'boot']
}

    
    for category, types in categories.items():
        if singular_type in types:
            logger.debug(f"Mapping '{suggested_item_type}' (singular: '{singular_type}') to '{category}'")
            return category
        elif suggested_item_type_lower in types:
            logger.debug(f"Mapping '{suggested_item_type}' to '{category}'")
            return category
    logger.warning(f"No mapping found for '{suggested_item_type}' (singular: '{singular_type}')")
    return None


def generate_outfit_combinations(clothing_items: List[EcommerceProduct], max_outfits: int = 5) -> List[List[Dict[str, Any]]]:
    """
    Generates possible outfit combinations by selecting one unique 'Top' from each outfit,
    and randomly pairing it with a 'Bottom' and 'Shoes'.

    Args:
        clothing_items (List[EcommerceProduct]): List of relevant clothing items.
        max_outfits (int): Maximum number of outfits to generate.

    Returns:
        List[List[Dict[str, Any]]]: List of outfit combinations.
    """
    categories = ['Top', 'Bottom', 'Shoes']
    grouped_items = {category: [] for category in categories}
    
    # Categorize items
    for item in clothing_items:
        category = map_product_to_category(item.suggested_item_type)
        if category:
            grouped_items[category].append(item)
            logger.debug(f"Assigned '{item.product_name}' to category '{category}'")
        else:
            logger.debug(f"Item '{item.product_name}' with type '{item.suggested_item_type}' could not be mapped to a general category.")

    # Log the number of items in each category
    for category, items in grouped_items.items():
        logger.info(f"Category '{category}' has {len(items)} items.")
    
    # Check if all categories have at least one item
    if any(len(items) == 0 for items in grouped_items.values()):
        missing = [cat for cat, items in grouped_items.items() if len(items) == 0]
        logger.warning(f"Missing items in categories: {missing}. Cannot form complete outfits.")
        return []
    
    # Shuffle 'Top' items to ensure variety
    tops = grouped_items['Top']
    bottoms = grouped_items['Bottom']
    shoes = grouped_items['Shoes']
    
    random.shuffle(tops)
    random.shuffle(bottoms)
    random.shuffle(shoes)
    logger.debug("Shuffled items in all categories for randomness.")
    
    # Determine the number of outfits to generate
    num_outfits = min(len(tops), max_outfits)
    
    outfit_combinations = []
    
    for i in range(num_outfits):
        top = tops[i]
        bottom = random.choice(bottoms)
        shoe = random.choice(shoes)
        
        outfit = [
            {
                'clothing_type': 'Top',
                'item_id': top.product_id,
                'product_name': top.product_name,
                'image_url': top.image_url,
                'eBay_link': None,
                'gender': top.gender
            },
            {
                'clothing_type': 'Bottom',
                'item_id': bottom.product_id,
                'product_name': bottom.product_name,
                'image_url': bottom.image_url,
                'eBay_link': None,
                'gender': bottom.gender
            },
            {
                'clothing_type': 'Shoes',
                'item_id': shoe.product_id,
                'product_name': shoe.product_name,
                'image_url': shoe.image_url,
                'eBay_link': None,
                'gender': shoe.gender
            }
        ]
        
        outfit_combinations.append(outfit)
        logger.debug(f"Generated outfit combination: {[c['product_name'] for c in outfit]}")
    
    logger.info(f"Generated {len(outfit_combinations)} outfit combinations.")
    return outfit_combinations





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

