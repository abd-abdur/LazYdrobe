import requests
import pandas as pd
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from main import EcommerceProduct, Base  # Import your model and Base
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

# Retrieve API key
def get_API_KEY(key):
    load_dotenv()
    API_KEY = os.getenv(key)
    if API_KEY:
        print(f"{key} retrieved successfully!")
        return API_KEY
    else:
        print("Failed to retrieve {key}. Please check your setup.")
        return None

def search_ebay(ebay_API_KEY, entries = 20, keywords="clothing", page = 1):
    if entries <= 0:
        return []
    
    if ebay_API_KEY == None:
        print("No key")
        return []
    
    entriesPerPage = min(entries, 100)
    
    # Get data
    url = (f"https://svcs.ebay.com/services/search/FindingService/v1?" +
        f"OPERATION-NAME=findItemsByKeywords&" +
        f"SERVICE-VERSION=1.0.0&" +
        f"SECURITY-APPNAME={ebay_API_KEY}&" +
        f"RESPONSE-DATA-FORMAT=JSON&" +
        f"REST-PAYLOAD=true&" +
        f"paginationInput.entriesPerPage={entriesPerPage}&" +
        f"paginationInput.pageNumber={page}&" +
        f"keywords={keywords}"+
        f"&itemFilter(0).name=HideDuplicateItems&itemFilter(0).value=true")
    print(url)
    response = requests.get(url)

    # If getting data was successful
    if response.status_code != 200:
        print(f"Failed to get the search on eBay for {keywords}. Please check for correct inputs and keys")
        return []
    data = response.json()
    if 'findItemsByKeywordsResponse' not in data:
        print(f"Unable to get {keywords} items")
        return []

    # Cleaning data
    # timestamp = data['findItemsByKeywordsResponse'][0]['timestamp'] # In case timestamp is needed
    items = data.get('findItemsByKeywordsResponse', [{}])[0].get('searchResult', [{}])[0].get('item', [])

    report = []
    for item in items:
        info = {
            'product_id': item['itemId'][0],
            'suggested_item_type': item['primaryCategory'][0]['categoryName'][0],
            'product_name': item['title'][0],
            'price': item['sellingStatus'][0]['currentPrice'][0]['__value__'],
            'product_url': item['viewItemURL'][0],
            'image_url': item['galleryURL'][0]
        }
        report.append(info)

    print("Successfully retrieved!")
    if entries > 100:
        report += search_ebay(ebay_API_KEY, entries - 100, keywords, page + 1)

    return report

# Connect and Insert Data to Database
def insert_data_to_db(data):
    DATABASE_URL = os.getenv("DATABASE_URL")  # Use your database URL from .env
    engine = create_engine(DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    Base.metadata.create_all(bind=engine)  # Ensure tables are created

    session = SessionLocal()
    try:
        for item in data:
            product = EcommerceProduct(
                product_id=item['product_id'],
                suggested_item_type=item['suggested_item_type'],
                product_name=item['product_name'],
                price=item['price'],
                product_url=item['product_url'],
                image_url=item['image_url']
            )
            session.add(product)
        session.commit()
        print("Data inserted successfully!")
    except IntegrityError as e:
        session.rollback()
        print("Error inserting data:", e)
    finally:
        session.close()

# Get amount to search for on ebay
def get_amount():
    ans = input("How many search items do you want?: ")
    while (True):
        try:
            ans = int(ans)
            break
        except:
            ans = input("Please enter the amount as an int: ")
    return ans

# Get keyword to search for on ebay
def get_keyword():
    ans = input("What do you want to look for?: ")
    while(len(ans) < 1 or type(ans) != str):
        ans = input("What do you want to look for?: ")
    return ans

# Get restricted search entries of a keyword
def get_search():
    # Get key
    ebay_API_KEY = get_API_KEY('ebay_API_KEY')

    # Search
    amt = get_amount()
    keyword = get_keyword()
    data = search_ebay(ebay_API_KEY, amt, keyword, 1)
    if data:
        insert_data_to_db(data)

# Loop until there is no more items or API doesn't allow
def get_all_possible():
    ebay_API_KEY = get_API_KEY('ebay_API_KEY')
    keyword = get_keyword()
    page = 1
    report = []
    data = search_ebay(ebay_API_KEY, 100, keyword, page)
    while (data != []):
        report.extend(data)
        page += 1
        data = search_ebay(ebay_API_KEY, 100, keyword, page)
    if report:
        insert_data_to_db(data)

if __name__ == "__main__":
    # get_search()
    get_all_possible()