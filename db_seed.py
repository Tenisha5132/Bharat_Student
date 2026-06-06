import os
import sys
from pymongo import MongoClient

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from config import settings

def seed_db():
    client = MongoClient(settings.MONGODB_URI)
    db = client[settings.MONGODB_DB_NAME]
    collection = db[settings.MONGODB_COLLECTION_NAME]

    # Drop existing to start fresh
    collection.drop()

    colleges = [
        {
            "basic": {
                "name": "Osmania University", "state": "Telangana", "city": "Hyderabad",
                "type": "Public", "university": "State University"
            },
            "regulatory": {
                "ugc_recognized": True, "aicte_approved": True,
                "naac_grade": "A+", "naac_score": 3.52, "approved_intake": 4000
            },
            "fees": {"annual_tuition": 25000, "hostel": 15000, "state_regulated": True},
            "placements": {"self_reported_percentage": 75.0, "top_recruiters": ["TCS", "Infosys"], "avg_package": 4.5},
            "red_flags": {"grievances": 12, "legal_cases": 2, "news": ["Delay in exam results reported in 2023"]},
            "reviews": {"google_rating": 4.3, "shiksha_rating": 4.1, "ai_summary": "Good academic environment but administrative delays are common."}
        },
        {
            "basic": {
                "name": "Jawaharlal Nehru Technological University Hyderabad (JNTUH)", "state": "Telangana", "city": "Hyderabad",
                "type": "Public", "university": "State University"
            },
            "regulatory": {
                "ugc_recognized": True, "aicte_approved": True,
                "naac_grade": "A", "naac_score": 3.15, "approved_intake": 5000
            },
            "fees": {"annual_tuition": 35000, "hostel": 20000, "state_regulated": True},
            "placements": {"self_reported_percentage": 80.0, "top_recruiters": ["Wipro", "Tech Mahindra", "Accenture"], "avg_package": 5.0},
            "red_flags": {"grievances": 5, "legal_cases": 0, "news": []},
            "reviews": {"google_rating": 4.2, "shiksha_rating": 4.0, "ai_summary": "Strong engineering programs, though campus infrastructure needs updates."}
        },
        {
            "basic": {
                "name": "IIT Bombay", "state": "Maharashtra", "city": "Mumbai",
                "type": "Public", "university": "Institute of National Importance"
            },
            "regulatory": {
                "ugc_recognized": True, "aicte_approved": True,
                "naac_grade": "A++", "naac_score": 3.90, "approved_intake": 1200
            },
            "fees": {"annual_tuition": 200000, "hostel": 50000, "state_regulated": False},
            "placements": {"self_reported_percentage": 95.0, "top_recruiters": ["Google", "Microsoft", "Jane Street"], "avg_package": 20.0},
            "red_flags": {"grievances": 3, "legal_cases": 1, "news": ["Recent protests regarding fee hikes"]},
            "reviews": {"google_rating": 4.8, "shiksha_rating": 4.9, "ai_summary": "Exceptional opportunities and brilliant peer group, highly competitive."}
        },
        {
            "basic": {
                "name": "VIT Vellore", "state": "Tamil Nadu", "city": "Vellore",
                "type": "Private", "university": "Deemed University"
            },
            "regulatory": {
                "ugc_recognized": True, "aicte_approved": True,
                "naac_grade": "A++", "naac_score": 3.66, "approved_intake": 7000
            },
            "fees": {"annual_tuition": 198000, "hostel": 100000, "state_regulated": False},
            "placements": {"self_reported_percentage": 85.0, "top_recruiters": ["TCS", "Cognizant", "Intel"], "avg_package": 8.0},
            "red_flags": {"grievances": 25, "legal_cases": 0, "news": ["Strict campus rules often debated by students"]},
            "reviews": {"google_rating": 4.1, "shiksha_rating": 4.2, "ai_summary": "Great placements and campus life, but high intake numbers and strict rules."}
        },
        {
            "basic": {
                "name": "Delhi University", "state": "Delhi", "city": "New Delhi",
                "type": "Public", "university": "Central University"
            },
            "regulatory": {
                "ugc_recognized": True, "aicte_approved": False,
                "naac_grade": "A+", "naac_score": 3.28, "approved_intake": 100000
            },
            "fees": {"annual_tuition": 15000, "hostel": 20000, "state_regulated": True},
            "placements": {"self_reported_percentage": 60.0, "top_recruiters": ["Deloitte", "KPMG", "EY"], "avg_package": 6.5},
            "red_flags": {"grievances": 50, "legal_cases": 5, "news": ["Frequent administrative protests"]},
            "reviews": {"google_rating": 4.4, "shiksha_rating": 4.3, "ai_summary": "Excellent diverse environment and low fees, but highly politicized."}
        }
    ]

    collection.insert_many(colleges)
    print("Database seeded with 5 colleges successfully.")

if __name__ == "__main__":
    seed_db()
