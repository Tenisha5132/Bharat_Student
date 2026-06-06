from pydantic import BaseModel, Field
from typing import List, Optional

class BasicInfo(BaseModel):
    name: str
    state: str
    city: str
    type: str # e.g. "Public", "Private"
    university: str

class RegulatoryInfo(BaseModel):
    ugc_recognized: bool
    aicte_approved: bool
    naac_grade: Optional[str] = None
    naac_score: Optional[float] = None
    approved_intake: Optional[int] = None

class FeeInfo(BaseModel):
    annual_tuition: float
    hostel: Optional[float] = None
    state_regulated: bool

class PlacementInfo(BaseModel):
    self_reported_percentage: float
    top_recruiters: List[str]
    avg_package: float # in LPA

class RedFlags(BaseModel):
    grievances: int
    legal_cases: int
    news: List[str]

class Reviews(BaseModel):
    google_rating: float
    shiksha_rating: float
    ai_summary: str

class CollegeProfile(BaseModel):
    id: Optional[str] = None # MongoDB ObjectId as string
    basic: BasicInfo
    regulatory: RegulatoryInfo
    fees: FeeInfo
    placements: PlacementInfo
    red_flags: RedFlags
    reviews: Reviews

class TrustMetrics(BaseModel):
    score: float # 0 to 10
    positives: List[str] = []
    risk_factors: List[str] = []
