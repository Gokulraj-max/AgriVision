class SeverityService:
    """
    Computer Vision Foliar Severity Estimator.
    Ratio: (Affected Pixels / Canopy Pixels) * 100
    """
    @staticmethod
    def calculate(affected_pixels: int, leaf_pixels: int, is_healthy: bool = False) -> dict:
        if is_healthy or leaf_pixels <= 0 or affected_pixels <= 0:
            return {
                "affected_area_percent": 0.0,
                "healthy_area_percent": 100.0,
                "severity_level": "Healthy",
                "affected_pixels": 0,
                "leaf_pixels": max(leaf_pixels, 1),
                "assessment": "No visible foliar lesions detected."
            }

        pct = (float(affected_pixels) / float(leaf_pixels)) * 100.0
        pct = min(round(pct, 2), 100.0)
        healthy_pct = round(100.0 - pct, 2)

        if pct < 10.0:
            level = "Mild"
            assessment = "Early localized infection (0-10% foliar damage)."
        elif pct < 25.0:
            level = "Moderate"
            assessment = "Established foliar infection (10-25% foliar damage)."
        elif pct < 50.0:
            level = "High"
            assessment = "Extensive foliar spread (25-50% foliar damage)."
        else:
            level = "Severe"
            assessment = "Critical canopy necrosis (>50% foliar damage)."

        return {
            "affected_area_percent": pct,
            "healthy_area_percent": healthy_pct,
            "severity_level": level,
            "affected_pixels": affected_pixels,
            "leaf_pixels": leaf_pixels,
            "assessment": assessment
        }
