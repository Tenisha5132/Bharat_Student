import os
import sys
import logging
from typing import Dict, Any
from llama_index.llms.ollama import Ollama

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import settings
from college_intel.schema import CollegeProfile, TrustMetrics
from college_intel.scraper import CollegeScraper
from college_intel.trust_score import TrustScoreCalculator

logger = logging.getLogger(__name__)

class ReportGenerator:
    def __init__(self):
        self.scraper = CollegeScraper()
        self.trust_calculator = TrustScoreCalculator()
        self.llm = Ollama(
            model=settings.OLLAMA_LLM_MODEL,
            base_url=settings.OLLAMA_BASE_URL,
            request_timeout=settings.LLM_TIMEOUT,
        )

    def generate_report(self, college_name: str) -> Dict[str, Any]:
        logger.info(f"Initiating report generation for {college_name}")
        
        # 1. Scrape Data
        profile = self.scraper.scrape(college_name)
        if not profile:
            logger.warning(f"College not found: {college_name}")
            return {
                "success": False,
                "error": f"Could not find intelligence data for '{college_name}'."
            }

        # 2. Calculate Trust Score
        trust_metrics = self.trust_calculator.calculate(profile)

        # 3. Prompt Llama 3
        prompt = f"""You are an expert Educational Analyst for BharatStudent.
Your task is to write a comprehensive College Intelligence Report based on the following verified data from MongoDB.

COLLEGE PROFILE:
Name: {profile.basic.name}
Location: {profile.basic.city}, {profile.basic.state}
Type: {profile.basic.type} ({profile.basic.university})
UGC Recognized: {profile.regulatory.ugc_recognized}
AICTE Approved: {profile.regulatory.aicte_approved}
NAAC Grade: {profile.regulatory.naac_grade} (Score: {profile.regulatory.naac_score})

FEES & PLACEMENTS:
Tuition: ₹{profile.fees.annual_tuition}
State Regulated Fees: {profile.fees.state_regulated}
Self-reported Placement: {profile.placements.self_reported_percentage}%
Average Package: {profile.placements.avg_package} LPA
Top Recruiters: {', '.join(profile.placements.top_recruiters)}

TRUST METRICS:
Overall Trust Score: {trust_metrics.score}/10
Positive Signals: {', '.join(trust_metrics.positives)}
Risk Factors: {', '.join(trust_metrics.risk_factors) if trust_metrics.risk_factors else 'None detected.'}

Please generate a professional, markdown-formatted report containing:
1. Executive Summary
2. Accreditation & Authenticity Analysis
3. Fee & Placement Reality Check
4. Trust Score Breakdown
5. Final Recommendation for Students

Keep it concise but informative. Do NOT invent data.
"""

        try:
            logger.info(f"Querying LLM ({settings.OLLAMA_LLM_MODEL}) for report...")
            response = self.llm.complete(prompt)
            
            return {
                "success": True,
                "college_name": profile.basic.name,
                "profile": profile.model_dump(),
                "trust_metrics": trust_metrics.model_dump(),
                "report_markdown": str(response)
            }
        except Exception as e:
            logger.error(f"Error generating report via LLM: {e}")
            pos_signals = "\n".join([f"    *   {pos}" for pos in trust_metrics.positives])
            risk_signals = "\n".join([f"    *   {risk}" for risk in trust_metrics.risk_factors]) if trust_metrics.risk_factors else '    *   No major risks or regulatory red flags detected.'
            
            fallback_report = f"""# College Intelligence Report: {profile.basic.name}
*(Note: Generated via fallback template as local Ollama is offline)*

### 1. Executive Summary
{profile.basic.name} is a **{profile.basic.type}** ({profile.basic.university}) institution located in **{profile.basic.city}, {profile.basic.state}**. It has been evaluated with an overall Trust Score of **{trust_metrics.score}/10**.

### 2. Accreditation & Authenticity Analysis
*   **UGC Recognition**: {'Recognized' if profile.regulatory.ugc_recognized else 'Not Recognized'}
*   **AICTE Approval**: {'Approved' if profile.regulatory.aicte_approved else 'Not Approved'}
*   **NAAC Accreditation**: Grade **{profile.regulatory.naac_grade}** with a cumulative score of **{profile.regulatory.naac_score}**.

### 3. Fee & Placement Reality Check
*   **Annual Tuition Fee**: ₹{profile.fees.annual_tuition:,} ({'State Regulated' if profile.fees.state_regulated else 'Decontrolled/Private Fee Structure'})
*   **Self-Reported Placements**: {profile.placements.self_reported_percentage}% placement rate.
*   **Average Package**: {profile.placements.avg_package} LPA.
*   **Key Recruiters**: {', '.join(profile.placements.top_recruiters)}.

### 4. Trust Score Breakdown
*   **Positive Signals**:
{pos_signals}
*   **Risk Factors**:
{risk_signals}

### 5. Final Recommendation
Based on the key accreditation indicators and placements, {profile.basic.name} {"is highly recommended" if trust_metrics.score >= 8 else "is recommended with reservations" if trust_metrics.score >= 6 else "requires caution due to lower trust metrics or red flags"}.
"""

            return {
                "success": True,
                "college_name": profile.basic.name,
                "profile": profile.model_dump(),
                "trust_metrics": trust_metrics.model_dump(),
                "report_markdown": fallback_report
            }

