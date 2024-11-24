# outfit_suggester.py

import logging
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from models import FashionTrend, EcommerceProduct, OutfitSuggestion, WeatherData, User
from fetch_ebay_data import fetch_similar_ebay_products
import random
import openai
import traceback
import inflect
import fal_client 
import os

p = inflect.engine()

from constants import ALLOWED_CATEGORIES

logger = logging.getLogger(__name__)

# Configure Logger (Ensure this configuration is done once in your main application)
if not logger.handlers:
    logger.setLevel(logging.DEBUG)  # Set to DEBUG for detailed logs; adjust as needed
    handler = logging.StreamHandler()
    formatter = logging.Formatter('[%(levelname)s] %(asctime)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)


def singularize(word: str) -> str:
    """
    Converts a plural noun to its singular form. If the word is already singular, returns it unchanged.
    """
    return p.singular_noun(word) or word


def map_product_to_category(suggested_item_type: str) -> Optional[str]:
    """
    Maps a specific clothing item type to a general category.
    
    Args:
        suggested_item_type (str): The specific type of the clothing item.
    
    Returns:
        Optional[str]: The general category of the clothing item or None if no match found.
    """
    singular_type = singularize(suggested_item_type).strip().lower()
    suggested_item_type_lower = suggested_item_type.strip().lower()

    categories = {
        'Top': [
            't-shirt', 'tank top', 'blouse', 'sweater', 'hoodie', 'cardigan',
            'shirt', 'crop top', 'camisole', 'polo shirt', 'long sleeve shirt',
            'turtleneck', 'thermal wear'
        ],
        'Bottom': [
            'jeans', 'shorts', 'skirt', 'pants', 'trouser', 'cargo pants',
            'corduroy pants', 'leggings', 'capri pants', 'sweatpants',
            'jumpsuit', 'culottes', 'thermal wear', 'tights'
        ],
        'Shoes': [
            'sneakers', 'sandals', 'boots', 'heavy boot', 'shoe',
            'loafers', 'flats', 'slippers', 'heels'
        ],
        'Outerwear': [
            'jacket', 'coat', 'blazer', 'raincoat', 'windbreaker',
            'denim jacket', 'leather jacket', 'trench coat', 'poncho',
            'winter coat'
        ],
        'Accessories': [
            'gloves', 'necklace', 'scarf', 'sunglasses', 'hat', 'belt',
            'watch', 'earrings', 'bracelet', 'handbag'
        ],
        'Set': [
            'set', 'suit set', 'complete suit', 'jumpsuit', 'dress'
        ]
    }

    for category, items in categories.items():
        if singular_type in items or suggested_item_type_lower in items:
            logger.debug(f"Mapped '{suggested_item_type}' to category '{category}'.")
            return category
    logger.warning(f"Could not map '{suggested_item_type}' to any category.")
    return None


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
            "You are an expert fashion assistant with a deep understanding of various clothing categories. "
            "Categorize the following clothing item into one of the predefined categories listed below. "
            "Ensure that each category is mutually exclusive and avoid overlaps. "
            "Provide only one category as the output.\n\n"
            "Predefined Categories: " + ", ".join(ALLOWED_CATEGORIES) + "\n\n"
            "Examples:\n"
            "- 'Slim Fit Leather Jacket for Men' -> Jacket\n"
            "- 'Women's Floral Summer Dress Set' -> Set\n"
            "- 'Classic Blue Denim Jeans' -> Jeans\n"
            "- 'Coordinated Blazer and Skirt Suit' -> Set\n"
            "- 'Warm Thermal Sweatpants' -> Sweatpants\n\n"
            f"Item Description: {product_name}\n"
            "Category (choose one from the list):"
        )
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are an expert fashion assistant with a deep understanding of various clothing categories."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=10,
            temperature=0.0,  # Ensure deterministic output
            n=1,
            stop=["\n"]  # Stop at newline to prevent extra text
        )
        category = response.choices[0].message.content.strip()

        # Clean the category text
        category = category.split('\n')[0].strip()

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
    Defaults to 'Unisex' in case of uncertainty.
    
    Args:
        product_name (str): The name or description of the product.
    
    Returns:
        str: The determined gender category.
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
        gender = response['choices'][0].message.content.strip()
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
    
    Args:
        user_id (int): ID of the user.
        db (Session): Database session.
    
    Returns:
        OutfitSuggestion: The created outfit suggestion.
    """
    logger.info(f"Starting outfit suggestion for user_id={user_id}")

    try:
        # 1. Retrieve User Profile
        user = db.query(User).filter(User.user_id == user_id).first()
        if not user:
            logger.warning(f"User with ID {user_id} not found.")
            raise ValueError("User not found.")

        if not user.location:
            logger.warning(f"User with ID {user_id} does not have a location set.")
            raise ValueError("User location not set.")

        location = user.location
        logger.info(f"User location: {location}")

        # 2. Retrieve Current Weather
        weather = get_latest_weather(db, user_id)
        if not weather:
            logger.warning(f"No weather data available for user ID {user_id}.")
            raise ValueError("Weather data not available.")
        logger.info(f"Retrieved weather data: {weather.special_condition}, Temp Max: {weather.temp_max}°F")

        # 3. Retrieve Current Fashion Trends
        trends = get_current_fashion_trends(db)
        if not trends:
            logger.warning("No fashion trends available.")
            raise ValueError("Fashion trends not available.")
        logger.info(f"Retrieved {len(trends)} fashion trends.")

        # 4. Determine Suitable Clothing Types
        suitable_clothing_types = determine_clothing_types(weather, trends)
        logger.info(f"Determined suitable clothing types: {suitable_clothing_types}")

        # 5. Select Relevant Clothing Items from Ecommerce Products
        selected_items = select_relevant_clothing_items(db, suitable_clothing_types, user_id)
        logger.info(f"Selected {len(selected_items)} clothing items for outfit suggestions.")

        if not selected_items:
            logger.warning("No clothing items found matching the suitable clothing types.")
            raise ValueError("No suitable clothing items found.")

        # 6. Determine if Outerwear Should Be Included
        include_outerwear = should_include_outerwear(weather)
        logger.info(f"Outerwear inclusion based on weather: {'Yes' if include_outerwear else 'No'}")

        # 7. Generate Outfit Combinations
        outfit_combinations = generate_outfit_combinations(
            selected_items,
            max_outfits=1,
            include_outerwear=include_outerwear
        )
        if not outfit_combinations:
            raise ValueError("Insufficient clothing items across categories to form outfits. Please add more items to your wardrobe.")
        logger.info(f"Generated {len(outfit_combinations)} outfit combination(s).")

        # 8. Fetch Similar Products from eBay
        enriched_outfits = fetch_similar_products_for_outfits(outfit_combinations, db)
        logger.info("Fetched similar products from eBay for all outfits.")

        # 9. Determine Overall Outfit Gender
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

        # 10. Save Outfit Suggestions to Database
        overall_gender = determine_overall_outfit_gender(outfit_genders)

        # 11. Generate Image using Flux AI
        image_url = generate_outfit_image(enriched_outfits[0])  # Assuming one outfit combination

        outfit_suggestion = OutfitSuggestion(
            user_id=user_id,
            outfit_details=enriched_outfits,  # List of outfit components with eBay links
            gender=overall_gender,  # Aggregate gender
            image_url=image_url  # Store the generated image URL
        )
        db.add(outfit_suggestion)
        db.commit()
        db.refresh(outfit_suggestion)
        logger.info(f"Saved outfit suggestion ID {outfit_suggestion.suggestion_id} for user ID {user_id} with gender '{overall_gender}' and image URL '{image_url}'.")

        return outfit_suggestion

    except ValueError as ve:
        logger.error(f"Value error occurred: {str(ve)}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error occurred while suggesting outfits for user {user_id}: {str(e)}")
        db.rollback()
        raise


def should_include_outerwear(weather: WeatherData) -> bool:
    """
    Determines whether Outerwear should be included based on the current weather conditions.
    
    Args:
        weather (WeatherData): Current weather data.
        
    Returns:
        bool: True if Outerwear should be included, False otherwise.
    """
    temp_max = weather.temp_max
    condition = weather.special_condition.lower()

    # Define a temperature threshold for cold weather (e.g., <= 60°F)
    cold_threshold = 35

    # Additional conditions for cold weather
    cold_conditions = ['snow', 'sleet', 'blizzard', 'freezing', 'cold']

    if temp_max <= cold_threshold or any(word in condition for word in cold_conditions):
        return True
    return False


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


def get_latest_weather(db: Session, user_id: int) -> Optional[WeatherData]:
    """
    Retrieves the latest weather data for the user's location.
    
    Args:
        db (Session): Database session.
        user_id (int): ID of the user.
        
    Returns:
        Optional[WeatherData]: The latest weather data or None if not found.
    """
    user = db.query(User).filter(User.user_id == user_id).first()
    if not user or not user.location:
        logger.debug("User or user location not found.")
        return None

    weather = db.query(WeatherData).filter(
        WeatherData.location == user.location
    ).order_by(WeatherData.date.desc()).first()

    if weather:
        logger.debug(f"Fetched WeatherData: date={weather.date}, temp_max={weather.temp_max}, location={weather.location}")
    else:
        logger.debug("No WeatherData found for the user.")
    return weather


def get_current_fashion_trends(db: Session) -> List[FashionTrend]:
    """
    Retrieves the latest fashion trends from the database.
    """
    return db.query(FashionTrend).order_by(FashionTrend.date_added.desc()).limit(10).all()


def determine_clothing_types(weather: WeatherData, trends: List[FashionTrend]) -> List[str]:
    """
    Determines suitable clothing types based on weather conditions and fashion trends.
    Includes considerations for various weather conditions and accessories.
    
    Args:
        weather (WeatherData): Current weather data.
        trends (List[FashionTrend]): Current fashion trends.
        
    Returns:
        List[str]: List of suitable clothing types.
    """
    clothing_types = set()

    # Analyze weather conditions
    temp_max = weather.temp_max
    condition = weather.special_condition.lower()

    # Rainy Weather
    if any(word in condition for word in ['rain', 'drizzle', 'shower', 'storm', 'wet']):
        clothing_types.update(['Raincoat', 'Umbrella', 'Waterproof Boots', 'Rain Hat', 'Poncho', 'Scarf'])

    # Sunny Weather
    if any(word in condition for word in ['sunny', 'clear', 'partly cloudy', 'hot']):
        clothing_types.update(['Sunglasses', 'Wide-Brim Hat', 'Cap'])

    # Snowy Weather
    if 'snow' in condition or 'sleet' in condition:
        clothing_types.update(['Snow Boots', 'Winter Coat', 'Gloves', 'Beanie', 'Scarf', 'Thermal Pants'])

    # Cold Weather (<= 35°F)
    if temp_max <= 35:
        clothing_types.update([ 'Sneakers', 'Sweater', 'Jeans', 'Pants', 'Thermal Wear', 'Gloves', 'Beanie', 'Insulated Boots', 'Scarf', 'Turtleneck', 'Boots', 'Hoodie', 'Cardigan'])

    # Warm Weather (> 75°F)
    if temp_max > 75:
        clothing_types.update(['Shorts', 'Flats', 'Heels', 'Jeans', 'T-Shirt', 'Pants', 'Tank Top', 'Sandals', 'Shoe', 'Sneakers', 'Skirt', 'Blouse', 'Dress', 'Camisole', 'Crop Top'])

    # Mild Weather (60°F to 75°F)
    if 60 < temp_max <= 75:
        clothing_types.update(['Jeans', 'Heels', 'Boots', 'T-Shirt', 'Shoe', 'Pants', 'Sneakers', 'Light Jacket', 'Blouse', 'Skirt', 'Dress', 'Leggings', 'Capri Pants'])

    # Cool Weather (35°F to 60°F)
    if 35 < temp_max <= 60:
        clothing_types.update(['Sweater', 'Shoe', 'Boots', 'T-Shirt', 'Sneakers', 'Jacket', 'Coat', 'Pants', 'Jeans', 'Hoodie', 'Cardigan', 'Thermal Wear'])

    # Special Weather Conditions
    if 'windy' in condition:
        clothing_types.update(['Windbreaker', 'Scarf'])
    if 'humid' in condition:
        clothing_types.update(['Breathable Fabrics', 'Linen Shirt', 'Shorts', 'Sandals'])
    if 'fog' in condition:
        clothing_types.update(['Reflective Jacket', 'Scarf'])

    # Incorporate fashion trends
    for trend in trends:
        trend_clothing = extract_clothing_types_from_trend(trend.trend_description)
        clothing_types.update(trend_clothing)

    # Ensure proper list output
    return sorted(list(clothing_types))


def extract_clothing_types_from_trend(description: str) -> List[str]:
    """
    Extracts clothing types from a trend description using simple keyword matching.
    
    Args:
        description (str): The description of the fashion trend.
    
    Returns:
        List[str]: List of clothing types extracted from the trend.
    """
    keywords = [
        'jacket', 'blouse', 'skirt', 'sweater', 'dress', 'jeans', 't-shirt', 'shorts',
        'boots', 'sandals', 'sneakers', 'coat', 'hoodie', 'tank top', 'heavy boots',
        'set', 'suit set', 'complete suit', 'jumpsuit', 'gloves', 'necklace', 'scarf',
        'flats', 
    ]
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


import random  # Ensure you have imported random at the top of your file

def generate_outfit_combinations(
    clothing_items: List[EcommerceProduct],
    max_outfits: int = 1,
    include_outerwear: bool = False
) -> List[List[Dict[str, Any]]]:
    required_categories = ['Shoes']
    optional_categories = ['Accessories']
    grouped_items = {category: [] for category in required_categories + optional_categories + ['Set', 'Top', 'Bottom', 'Outerwear']}

    # Categorize items
    for item in clothing_items:
        category = map_product_to_category(item.suggested_item_type)
        if category:
            grouped_items[category].append(item)
            logger.debug(f"Assigned '{item.product_name}' to category '{category}'")
        else:
            logger.debug(f"Item '{item.product_name}' with type '{item.suggested_item_type}' could not be mapped to a general category.")

    # Logging the number of items in each category
    for category, items in grouped_items.items():
        logger.info(f"Category '{category}' has {len(items)} items.")

    # Outfit Requirements
    if len(grouped_items['Shoes']) == 0:
        logger.warning("Missing items in required categories: Shoes. Cannot form complete outfits.")
        raise ValueError("Insufficient clothing items in category: Shoes. Please add more items to your wardrobe.")

    # Determine if 'Set' or 'Top-Bottom' can be used
    can_use_set = len(grouped_items['Set']) > 0
    can_use_top_bottom = len(grouped_items['Top']) > 0 and len(grouped_items['Bottom']) > 0

    if not can_use_set and not can_use_top_bottom:
        logger.warning("Insufficient clothing items to form either Sets or Top-Bottom combinations.")
        raise ValueError("Insufficient clothing items to form either Sets or Top-Bottom combinations. Please add more items to your wardrobe.")

    # Shuffle items for randomness
    for category in grouped_items:
        random.shuffle(grouped_items[category])

    # Determine the number of outfits to generate
    num_outfits = min(max_outfits, max(len(grouped_items['Set']), len(grouped_items['Top']), len(grouped_items['Bottom'])))

    outfit_combinations = []

    for i in range(num_outfits):
        outfit = []
        # Randomly decide to use 'Set' or 'Top-Bottom'
        use_set = False
        if can_use_set and can_use_top_bottom:
            use_set = random.choice([True, False])
        elif can_use_set:
            use_set = True
        elif can_use_top_bottom:
            use_set = False

        if use_set:
            set_item = grouped_items['Set'][i % len(grouped_items['Set'])]
            outfit.append({
                'clothing_type': 'Set',
                'item_id': set_item.product_id,
                'product_name': set_item.product_name,
                'image_url': set_item.image_url,
                'eBay_link': None,
                'gender': set_item.gender
            })
            logger.debug(f"Using Set: '{set_item.product_name}'")
        else:
            top = grouped_items['Top'][i % len(grouped_items['Top'])]
            bottom = grouped_items['Bottom'][i % len(grouped_items['Bottom'])]
            outfit.extend([
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
                }
            ])
            logger.debug(f"Using Top: '{top.product_name}' and Bottom: '{bottom.product_name}'")

        # Always add 'Shoes'
        shoe = grouped_items['Shoes'][i % len(grouped_items['Shoes'])]
        outfit.append({
            'clothing_type': 'Shoes',
            'item_id': shoe.product_id,
            'product_name': shoe.product_name,
            'image_url': shoe.image_url,
            'eBay_link': None,
            'gender': shoe.gender
        })
        logger.debug(f"Adding Shoes: '{shoe.product_name}' to the outfit.")

        # Optionally add 'Outerwear'
        if include_outerwear and len(grouped_items['Outerwear']) > 0:
            outer = grouped_items['Outerwear'][random.randint(0, len(grouped_items['Outerwear']) - 1)]
            outfit.append({
                'clothing_type': 'Outerwear',
                'item_id': outer.product_id,
                'product_name': outer.product_name,
                'image_url': outer.image_url,
                'eBay_link': None,
                'gender': outer.gender
            })
            logger.debug(f"Added 'Outerwear': '{outer.product_name}' to the outfit.")

        # Optionally add 'Accessories'
        if len(grouped_items['Accessories']) > 0:
            accessory = grouped_items['Accessories'][random.randint(0, len(grouped_items['Accessories']) - 1)]
            outfit.append({
                'clothing_type': 'Accessories',
                'item_id': accessory.product_id,
                'product_name': accessory.product_name,
                'image_url': accessory.image_url,
                'eBay_link': None,
                'gender': accessory.gender
            })
            logger.debug(f"Added 'Accessories': '{accessory.product_name}' to the outfit.")

        outfit_combinations.append(outfit)
        logger.debug(f"Generated outfit combination: {[c['product_name'] for c in outfit]}")

    logger.info(f"Generated {len(outfit_combinations)} outfit combination(s).")
    return outfit_combinations


def fetch_similar_products_for_outfits(outfit_combinations: List[List[Dict[str, Any]]], db: Session) -> List[List[Dict[str, Any]]]:
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


def generate_outfit_image(outfit_components: List[Dict[str, Any]]) -> Optional[str]:
    """
    Generates an image of the outfit using Flux AI by sending the clothing item names.
    
    Args:
        outfit_components (List[Dict[str, Any]]): List of clothing components in the outfit.
    
    Returns:
        Optional[str]: URL of the generated image or None if generation fails.
    """
    try:
        logger.info("Starting image generation using Flux AI.")
        
        # Extract clothing item descriptions
        clothing_descriptions = []
        for component in outfit_components:
            clothing_type = component['clothing_type']
            product_name = component['product_name']
            # Customize the description as needed
            description = f"**{clothing_type}:** {product_name}"
            clothing_descriptions.append(description)
        
        # Compose the prompt
        prompt = (
            "Create an image of a stylish individual wearing the following outfit:\n\n" +
            "\n".join([f"{idx + 1}. {desc}" for idx, desc in enumerate(clothing_descriptions)]) +
            "\n\n"
            "The individual should have a confident and relaxed pose, evoking a modern and elegant aesthetic. "
            "Make sure you read the outfit names properly and work hard to accurately create the outfit specially the color"
            "Use a neutral studio background with soft lighting to highlight the outfit. Ensure the outfit fits naturally and realistically on the individual, "
            "emphasizing the textures and styles of the clothing items."
        )
        
        # Set your Flux AI API key
        fal_client_key = os.getenv("FAL_KEY")
        if not fal_client_key:
            logger.error("FAL_KEY is not set in environment variables.")
            return None  # Alternatively, raise an exception

        os.environ["FAL_KEY"] = fal_client_key  # Ensure the API key is set

        # Function to handle log updates
        def on_queue_update(update):
            if isinstance(update, fal_client.InProgress):
                for log_entry in update.logs:
                    logger.debug(f"Flux AI Log: {log_entry['message']}")

        # Submit the request to Flux AI
        logger.info("Submitting image generation request to Flux AI.")
        result = fal_client.subscribe(
            "fal-ai/flux/dev",  # Model identifier; adjust as needed
            arguments={
                "prompt": prompt,
                "image_size": "landscape_16_9",  # Aspect ratio suitable for human model display
                "num_inference_steps": 50,      # High-quality output
                "guidance_scale": 8.0,          # Strong adherence to the prompt
                "num_images": 1,                # Generate one image
                "enable_safety_checker": True   # Enable safety checks
            },
            with_logs=True,                    # Enable logs for updates
            on_queue_update=on_queue_update    # Log handler for real-time feedback
        )

        # Extract the image URL
        image_url = result['images'][0]['url']
        logger.info(f"Image generated successfully: {image_url}")
        return image_url

    except Exception as e:
        logger.error(f"Error generating outfit image: {e}")
        logger.debug(traceback.format_exc())
        return None