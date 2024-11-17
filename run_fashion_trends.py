# run_fashion_trends.py

import os
from sqlalchemy.orm import Session
from models import Base, FashionTrend, EcommerceProduct
from fashion_trends import fetch_and_update_fashion_trends, populate_ecommerce_products
from dotenv import load_dotenv
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    logger.error("DATABASE_URL is not set in the environment variables.")
    raise ValueError("DATABASE_URL is not set in the environment variables.")

# Create the SQLAlchemy engine
from sqlalchemy import create_engine

engine = create_engine(DATABASE_URL, echo=False)

# Create a configured "Session" class
from sqlalchemy.orm import sessionmaker

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def main():
    db = SessionLocal()
    try:
        # Step 1: Fetch and update fashion trends
        fetch_and_update_fashion_trends(db)

        # Step 2: Populate ecommerce_products based on updated trends
        populate_ecommerce_products(db)

    finally:
        db.close()

if __name__ == "__main__":
    # Optional: Uncomment the following line to debug the EcommerceProduct model
    # debug_ecommerce_product()

    main()
