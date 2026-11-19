class SeverityService:
    """
    Computer Vision Severity Estimation Service.
    Calculates visible foliar symptom coverage:
        Affected Area % = (Affected Pixels / Leaf Pixels) * 100
    """
    @staticmethod
    def calculate_severity(affected_pixels: int, leaf_pixels: int, is_healthy: bool = False) -> dict:
        if is_healthy or leaf_pixels <= 0 or affected_pixels <= 0:
            return {
                "affected_area_percentage": 0.0,
                "severity_level": "Healthy",
                "severity_class": "healthy",
                "affected_pixels": 0,
                "leaf_pixels": max(leaf_pixels, 1),
                "damage_category": "No Visible Lesions",
                "disclaimer": "Foliar surface exhibits healthy chlorophyll response with no detected necrotic or chlorotic lesions."
            }

        # Percentage
        affected_pct = (float(affected_pixels) / float(leaf_pixels)) * 100.0
        affected_pct = min(round(affected_pct, 2), 100.0)

        # Categorize
        if affected_pct < 10.0:
            level = "Mild"
            category = "Early Stage (0-10% foliar damage)"
            severity_class = "mild"
        elif affected_pct < 25.0:
            level = "Moderate"
            category = "Established Infection (10-25% foliar damage)"
            severity_class = "moderate"
        elif affected_pct < 50.0:
            level = "High"
            category = "Extensive Defoliation Risk (25-50% foliar damage)"
            severity_class = "high"
        else:
            level = "Severe"
            category = "Critical Canopy Necrosis (>50% foliar damage)"
            severity_class = "severe"

        return {
            "affected_area_percentage": affected_pct,
            "severity_level": level,
            "severity_class": severity_class,
            "affected_pixels": affected_pixels,
            "leaf_pixels": leaf_pixels,
            "damage_category": category,
            "disclaimer": "Calculated as estimated visible symptom coverage on the photographed leaf plane. Treat as decision-support guidance, not a laboratory systemic assessment."
        }
