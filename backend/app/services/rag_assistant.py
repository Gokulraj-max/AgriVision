import re
from typing import Dict, List, Optional
from ml.configs.crop_disease_catalog import CROP_DISEASE_REGISTRY, SUPPORTED_CROPS

class AgriculturalRAGAssistant:
    """
    Multilingual Agricultural Knowledge Assistant (Tamil & English).
    Powered by an agronomic knowledge base & retrieval-augmented synthesis.
    Distinguishes diagnostic hypotheses from certified chemical recommendations.
    """
    
    KNOWLEDGE_BASE = [
        {
            "topic": "yellow_leaves",
            "keywords": ["yellow", "yellowing", "chlorosis", "மஞ்சள்", "மஞ்சளாக"],
            "answer_en": "Yellow leaves (chlorosis) in crops can be caused by either viral infections (like Tomato Yellow Leaf Curl), nitrogen deficiency, or early fungal blight. If the leaves are also cupping upwards, it is likely Whitefly-transmitted Yellow Leaf Curl Virus. If older lower leaves show yellow halos around dark target spots, it indicates Early Blight. Action: Inspect the undersides of leaves for tiny whiteflies and avoid over-watering.",
            "answer_ta": "இலைகள் மஞ்சளாதல் (Chlorosis) பொதுவாக இலைச்சுருள் வைரஸ் (TYLCV), தழைச்சத்து குறைபாடு அல்லது ஆரம்ப கருகல் நோயால் ஏற்படுகிறது. இலைகள் மேல்நோக்கி கிண்ணம் போல சுருண்டால், அது வெள்ளை ஈக்கள் மூலம் பரவும் நச்சுயிரி நோயாகும். கீழ் இலைகளில் வளையப் புள்ளிகளுடன் மஞ்சள் வட்டம் இருந்தால் அது ஆரம்ப கருகல் நோய். நடவடிக்கை: இலைகளின் அடிப்பகுதியில் வெள்ளை ஈக்கள் உள்ளனவா எனப் பார்த்து, மஞ்சள் ஒட்டும் பொறிகளைப் பயன்படுத்தவும்."
        },
        {
            "topic": "blight_prevention",
            "keywords": ["blight", "early blight", "late blight", "prevent", "spread", "கருகல்", "பரவாமல்"],
            "answer_en": "To prevent blight from spreading: 1) Prune and immediately bag infected lower leaves (do not compost). 2) Switch entirely from overhead sprinklers to drip irrigation to avoid splashing spores. 3) Apply clean straw mulch to create a physical barrier between soil pathogens and foliage. 4) Consult your local extension office (KVK/ICAR) for officially registered copper-based bio-fungicides.",
            "answer_ta": "கருகல் நோய் பரவுவதை தடுக்க: 1) பாதிக்கப்பட்ட கீழ் இலைகளை வெட்டி பையில் போட்டு அப்புறப்படுத்தவும் (உரக்குழியில் போடாதீர்கள்). 2) தெளிப்பு நீர்ப்பாசனத்தை தவிர்த்து சொட்டு நீர்ப்பாசனம் செய்யவும். 3) மண்ணிலிருந்து பூஞ்சை வித்துக்கள் பரவாமல் தடுக்க வைக்கோல் தழைக்கூளம் இடவும். 4) அரசு சான்றளித்த காப்பர் அடிப்படையிலான தடுப்பு முறைகளுக்கு உள்ளூர் வேளாண்மை விரிவாக்க மையத்தை (KVK) அணுகவும்."
        },
        {
            "topic": "spray_precautions",
            "keywords": ["spray", "pesticide", "fungicide", "check", "dosage", "தெளிக்க", "மருந்து", "பூச்சிக்கொல்லி"],
            "answer_en": "Before applying any protective spray: 1) Scout during calm early morning or late afternoon (never during high heat or high wind >15 km/h). 2) Check the Pre-Harvest Interval (PHI) to prevent chemical residue in crops. 3) Confirm calibration of the spray nozzle for uniform droplet size. 4) AgriVision AI strictly advises consulting your certified extension officer for local label authorizations — never exceed prescribed dosages.",
            "answer_ta": "மருந்து தெளிப்பதற்கு முன் கவனிக்க வேண்டியவை: 1) அதிக வெயில் அல்லது பலத்த காற்று இல்லாத காலை அல்லது மாலை வேளையில் தெளிக்கவும். 2) அறுவடைக்கு முந்தைய இடைவெளியை (PHI) சரிபார்க்கவும். 3) தெளிப்பான் முனையை சரியாக அளவிடவும். 4) அரசு அங்கீகரித்த மருந்துகள் மற்றும் அளவுகளுக்கு உள்ளூர் வேளாண்மை அலுவலரின் வழிகாட்டுதலை மட்டுமே பின்பற்றவும்."
        },
        {
            "topic": "inspection_reports",
            "keywords": ["report", "history", "previous", "அறிக்கை", "முந்தைய", "ஆய்வு"],
            "answer_en": "You can view your complete inspection audit trail directly in the 'My Farms' or 'History' tab of the AgriVision mobile app. Each inspection records the disease class, estimated foliar severity percentage, localized symptom bounding boxes, and expert agronomist comments.",
            "answer_ta": "உங்கள் முந்தைய பயிர் ஆய்வு அறிக்கைகளை 'My Farms' அல்லது 'History' பகுதியில் பார்க்கலாம். அதில் கணிக்கப்பட்ட நோய், பாதிக்கப்பட்ட இலையின் பரப்பளவு %, புகைப்பட ஆதாரங்கள் மற்றும் வல்லுநர்களின் கருத்துக்கள் பதிவு செய்யப்பட்டுள்ளன."
        },
        {
            "topic": "rice_blast",
            "keywords": ["rice", "blast", "paddy", "நெல்", "குலை நோய்", "சாம்பல்"],
            "answer_en": "Rice Leaf Blast (Magnaporthe oryzae) presents spindle-shaped lesions with grayish centers and dark brown margins. Immediate action: Maintain 2-5 cm continuous water layer in paddy fields (drought stress accelerates blast). Avoid excessive nitrogen top-dressing. Seed treatment with Pseudomonas fluorescens (10g/kg seed) provides strong biological protection.",
            "answer_ta": "நெல் இலை குலை நோய் (Blast) கதிர் போன்ற நீள்வட்ட சாம்பல் நிற புள்ளிகளாக தோன்றும். உடனடி நடவடிக்கை: வயலில் 2 முதல் 5 செ.மீ நீர் எப்போதும் இருக்குமாறு பராமரிக்கவும் (வறட்சி இந்நோயை அதிகரிக்கும்). அதிக தழைச்சத்து இடுவதை தவிர்க்கவும். சூடோமோனாஸ் (Pseudomonas) கொண்டு விதை நேர்த்தி செய்வது சிறந்த இயற்கை பாதுகாப்பாகும்."
        },
        {
            "topic": "cotton_curl",
            "keywords": ["cotton", "curl", "whitefly", "பருத்தி", "சுருள்"],
            "answer_en": "Cotton Leaf Curl Virus causes leaf thickening, upward curling, and enations (leaf-like growths) beneath veins. Vector: Sweetpotato Whitefly (Bemisia tabaci). Management: Spray 5% neem seed kernel extract (NSKE) or approved insecticidal soap to deter whiteflies. Eradicate weed alternate hosts around field bunds.",
            "answer_ta": "பருத்தி இலை சுருள் நச்சுயிரி நோய் வெள்ளை ஈக்கள் மூலம் பரவுகிறது. இலைகள் தடித்து மேல்நோக்கி சுருளும். மேலாண்மை: 5% வேப்பங்கொட்டை கரைசல் தெளித்து வெள்ளை ஈக்களை கட்டுப்படுத்தவும். வயல் வரப்புகளில் உள்ள களைகளை அகற்றவும்."
        }
    ]

    def answer_query(self, query: str, context_crop: str = "Tomato") -> dict:
        """
        Synthesizes a domain-validated agronomic response based on query semantics.
        Detects language (Tamil vs. English).
        """
        query_lower = query.lower()
        
        # Detect if query contains Tamil unicode characters (U+0B80 to U+0BFF)
        is_tamil = bool(re.search(r'[\u0B80-\u0BFF]', query))
        lang = "ta" if is_tamil else "en"

        # Search knowledge base
        matched_item = None
        for item in self.KNOWLEDGE_BASE:
            for kw in item["keywords"]:
                if kw.lower() in query_lower:
                    matched_item = item
                    break
            if matched_item:
                break

        if matched_item:
            answer_text = matched_item["answer_ta"] if is_tamil else matched_item["answer_en"]
            topic = matched_item["topic"]
        else:
            # Context-sensitive fallback based on active crop
            crop_info = next((v for k, v in CROP_DISEASE_REGISTRY.items() if v["crop"].lower() == context_crop.lower() and "healthy" not in k), None)
            if is_tamil:
                answer_text = (
                    f"உங்கள் {context_crop} பயிர் தொடர்பான கேள்வி பதிவு செய்யப்பட்டது. "
                    "பயிர் இலைகளில் ஏதேனும் புள்ளிகள் அல்லது நிறமாற்றம் இருந்தால், 'Scan' கேமராவை பயன்படுத்தி புகைப்படம் எடுக்கவும். "
                    "எங்கள் AI மாதிரி உடனடியாக நோய் அறிகுறிகளை கண்டறிந்து மேலாண்மை முறைகளை வழங்கும். "
                    "பூச்சிக்கொல்லி பயன்பாட்டிற்கு முன் உள்ளூர் வேளாண்மை அலுவலரின் அனுமதியை பெறவும்."
                )
            else:
                answer_text = (
                    f"Thank you for your agronomic inquiry regarding {context_crop}. "
                    "If you observe specific foliar discoloration, lesions, or wilting, please use the 'Scan' camera tab to capture a leaf specimen. "
                    "AgriVision AI will segment affected areas and calculate severity. "
                    "Important: Consult your local certified agricultural extension authority before purchasing or applying synthetic agrochemicals."
                )
            topic = "general_inquiry"

        return {
            "query": query,
            "language": lang,
            "topic": topic,
            "answer": answer_text,
            "context_crop": context_crop,
            "voice_supported": True,
            "safety_disclaimer": "Agricultural decision-support guidance. Verify with certified local extension authorities before applying chemical treatments."
        }
