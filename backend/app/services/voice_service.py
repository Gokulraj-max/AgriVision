"""
AgriVision AI 2.0 - Multilingual Voice Service (Tamil & English)
Provides text-to-speech phonetic cues and speech processing metadata.
"""

class VoiceService:
    @staticmethod
    def get_speech_config(language: str = "en") -> dict:
        """
        Returns Web Speech / Native TTS voice configuration.
        """
        if language == "ta":
            return {
                "voice_name": "ta-IN-Standard-A",
                "language_code": "ta-IN",
                "pitch": 1.0,
                "speaking_rate": 0.95,
                "label": "தமிழ் (Tamil)"
            }
        return {
            "voice_name": "en-US-Standard-C",
            "language_code": "en-US",
            "pitch": 1.0,
            "speaking_rate": 1.0,
            "label": "English"
        }

    @staticmethod
    def format_spoken_diagnosis(crop: str, disease: str, confidence: float, severity_pct: float, language: str = "en") -> str:
        """
        Generates farmer-friendly spoken voice announcement for disease diagnosis.
        """
        conf_int = int(confidence * 100)
        sev_int = int(severity_pct)

        if language == "ta":
            return (
                f"கணிக்கப்பட்ட பயிர்: {crop}. "
                f"நோய் நிலை: {disease}. "
                f"நம்பகத்தன்மை: நூற்றுக்கு {conf_int} சதவீதம். "
                f"இலையில் பாதிக்கப்பட்ட பகுதி தோராயமாக {sev_int} சதவீதம். "
                f"மேலாண்மை நடவடிக்கைகளை திரையில் பார்க்கவும்."
            )
        return (
            f"Crop identified as {crop}. "
            f"Detected condition is {disease} with {conf_int} percent confidence. "
            f"Estimated foliar severity is {sev_int} percent. "
            f"Please review the recommended cultural practices on your screen."
        )
