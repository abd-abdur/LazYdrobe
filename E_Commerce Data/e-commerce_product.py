import requests
import pandas as pd
import os
from dotenv import load_dotenv

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

def search_ebay(ebay_API_KEY, entries = 20, keywords="clothing"):
    if ebay_API_KEY == None:
        print("No key")
        return
    
    # Get data
    url = (f"https://svcs.ebay.com/services/search/FindingService/v1?" +
        f"OPERATION-NAME=findItemsAdvanced&" +
        f"SERVICE-VERSION=1.0.0&" +
        f"SECURITY-APPNAME={ebay_API_KEY}&" +
        f"RESPONSE-DATA-FORMAT=JSON&" +
        f"REST-PAYLOAD=true&" +
        f"paginationInput.entriesPerPage={entries}&" +
        f"keywords={keywords}")
    response = requests.get(url)

    # If getting data was successful
    if response.status_code != 200:
        print(f"Failed to get the search on eBay for {keywords}. Please check for correct inputs and keys")
        return
    data = response.json()
    if 'findItemsAdvancedResponse' not in data:
        print(f"Unable to get {keywords} items")
        return []

    # Cleaning data
    # timestamp = data['findItemsByKeywordsResponse'][0]['timestamp'] # In case timestamp is needed
    items = data['findItemsAdvancedResponse'][0]['searchResult'][0]['item']
    
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
    return report

# Convert weather data to csv file    
def search_to_file(data):
    df = pd.DataFrame(data)
    # Make product_id first column
    cols = ['product_id'] + [col for col in df.columns if col != 'product_id']
    df = df[cols] # Reorder the columns

    # Clean CSV file
    df.columns = df.columns.str.lower().str.replace(' ', '_') # Make all columns lower space and replacing spaces with _
    df = df.apply(lambda col: col.fillna(0) if col.dtype in ['int64', 'float64'] else col.fillna('Unknown'))
    df.to_csv(f'e-commerce-products.csv', index=False)
    print("Check your folder for product data.")

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

def get_search():
    # Get key
    ebay_API_KEY = get_API_KEY('ebay_API_KEY')

    # Search
    amt = get_amount()
    keyword = get_keyword()
    data = search_ebay(ebay_API_KEY, amt, keyword)
    search_to_file(data)
    return

if __name__ == "__main__":
    get_search()