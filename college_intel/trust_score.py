from .schema import CollegeProfile, TrustMetrics

class TrustScoreCalculator:
    def calculate(self, profile: CollegeProfile) -> TrustMetrics:
        score = 0.0
        positives = []
        risk_factors = []
        
        # 1. NAAC Grade (Max 3.0 points / 30%)
        reg = profile.regulatory
        if reg.naac_grade:
            grade = reg.naac_grade.upper()
            if grade == "A++":
                score += 3.0
                positives.append("Top-tier NAAC A++ Accreditation")
            elif grade == "A+":
                score += 2.5
                positives.append("Excellent NAAC A+ Accreditation")
            elif grade == "A":
                score += 2.0
                positives.append("Strong NAAC A Accreditation")
            else:
                score += 1.0
                positives.append(f"NAAC Accredited ({grade})")
        else:
            risk_factors.append("Missing NAAC Accreditation")

        # 2. AICTE / UGC Approval (Max 2.0 points / 20%)
        if reg.ugc_recognized or reg.aicte_approved:
            score += 2.0
            bodies = []
            if reg.ugc_recognized: bodies.append("UGC")
            if reg.aicte_approved: bodies.append("AICTE")
            positives.append(f"Approved by: {', '.join(bodies)}")
        else:
            risk_factors.append("Lacks basic UGC/AICTE approvals (High Risk)")

        # 3. Reviews (Max 2.0 points / 20%)
        google_rating = profile.reviews.google_rating
        review_score = (google_rating / 5.0) * 2.0
        score += review_score
        if google_rating >= 4.0:
            positives.append(f"Strong student reviews ({google_rating}/5)")
        else:
            risk_factors.append(f"Poor student reviews ({google_rating}/5)")

        # Base score out of 7 so far. The remaining 3.0 is a base that gets penalized by red flags.
        red_flag_score = 3.0
        
        # 4. Red Flags (Penalty up to 3.0 points / 30%)
        flags = profile.red_flags
        total_issues = flags.grievances + (flags.legal_cases * 10) # legal cases weighted more
        
        if total_issues == 0 and not flags.news:
            positives.append("Clean record with no legal cases or major grievances")
        else:
            penalty = min(3.0, (total_issues * 0.1) + (len(flags.news) * 0.5))
            red_flag_score -= penalty
            if flags.legal_cases > 0:
                risk_factors.append(f"Active legal cases ({flags.legal_cases})")
            if flags.grievances > 10:
                risk_factors.append(f"High number of grievances ({flags.grievances})")
                
        score += red_flag_score
            
        return TrustMetrics(
            score=round(max(0.0, min(10.0, score)), 1),
            positives=positives,
            risk_factors=risk_factors
        )
