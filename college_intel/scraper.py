import os
import sys
import logging
from pymongo import MongoClient
from typing import Optional

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import settings
from college_intel.schema import CollegeProfile

logger = logging.getLogger(__name__)

class CollegeScraper:
    def __init__(self):
        self.client = MongoClient(settings.MONGODB_URI)
        self.db = self.client[settings.MONGODB_DB_NAME]
        self.collection = self.db[settings.MONGODB_COLLECTION_NAME]

    def scrape(self, college_name: str) -> Optional[CollegeProfile]:
        """
        Simulates scraping by fetching verified data from MongoDB.
        Uses regex for fuzzy matching.
        """
        try:
            # Case insensitive search
            doc = self.collection.find_one({"basic.name": {"$regex": college_name, "$options": "i"}})
            if doc:
                # Convert ObjectId to string
                doc["id"] = str(doc["_id"])
                del doc["_id"]
                return CollegeProfile(**doc)
            return None
        except Exception as e:
            logger.error(f"Error fetching college data from MongoDB: {e}")
            return None
