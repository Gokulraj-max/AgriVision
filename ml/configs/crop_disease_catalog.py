"""
AgriVision AI 2.0 - Comprehensive Multi-Crop & Disease Knowledge Base
Supports 7 major agricultural crops:
1. Tomato (Solanum lycopersicum)
2. Potato (Solanum tuberosum)
3. Rice (Oryza sativa)
4. Cotton (Gossypium hirsutum)
5. Maize / Corn (Zea mays)
6. Pepper (Capsicum annuum)
7. Apple (Malus domestica)
"""

SUPPORTED_CROPS = [
    "Tomato",
    "Potato",
    "Rice",
    "Cotton",
    "Maize",
    "Pepper",
    "Apple"
]

CROP_DISEASE_REGISTRY = {
    # 1. TOMATO
    "Tomato___healthy": {
        "crop": "Tomato",
        "disease": "Healthy",
        "display_name": "Healthy Tomato Foliage",
        "display_name_ta": "ஆரோக்கியமான தக்காளி இலை",
        "pathogen": "None",
        "description": "Vigorous chlorophyll response with clean margins and no necrotic lesions.",
        "management": "Continue regular drip irrigation and scout undersides of leaves weekly.",
        "management_ta": "வழக்கமான சொட்டு நீர்ப்பாசனத்தை தொடரவும், வாரந்தோறும் இலைகளை கண்காணிக்கவும்."
    },
    "Tomato___Early_blight": {
        "crop": "Tomato",
        "disease": "Early Blight",
        "display_name": "Tomato Early Blight (Alternaria solani)",
        "display_name_ta": "தக்காளி ஆரம்பகால கருகல் நோய்",
        "pathogen": "Alternaria solani (Fungus)",
        "description": "Target-board concentric ring brown lesions primarily on older lower leaves.",
        "management": "Prune lower infected leaves; apply organic mulch; avoid overhead watering.",
        "management_ta": "பாதிக்கப்பட்ட கீழ் இலைகளை வெட்டி அகற்றவும்; தழைக்கூளம் இடவும்; தெளிப்பு நீர்ப்பாசனத்தை தவிர்க்கவும்."
    },
    "Tomato___Late_blight": {
        "crop": "Tomato",
        "disease": "Late Blight",
        "display_name": "Tomato Late Blight (Phytophthora infestans)",
        "display_name_ta": "தக்காளி பிந்தைய கருகல் நோய்",
        "pathogen": "Phytophthora infestans (Oomycete)",
        "description": "Rapid water-soaked dark blights with pale halos in cool, humid microclimates.",
        "management": "Quarantine row; lower canopy humidity; notify extension officer for approved bio-fungicide.",
        "management_ta": "பாதிக்கப்பட்ட பகுதிகளை தனிமைப்படுத்தவும்; ஈரப்பதத்தை குறைக்கவும்; வேளாண்மை அதிகாரியை அணுகவும்."
    },
    "Tomato___Bacterial_spot": {
        "crop": "Tomato",
        "disease": "Bacterial Spot",
        "display_name": "Tomato Bacterial Spot (Xanthomonas)",
        "display_name_ta": "தக்காளி பாக்டீரியா புள்ளி நோய்",
        "pathogen": "Xanthomonas spp. (Bacteria)",
        "description": "Small dark angular water-soaked speckles that coalesce into ragged holes.",
        "management": "Never work in wet fields; sanitize tools with alcohol; hot-water treat seeds.",
        "management_ta": "ஈரமான பயிர்களில் வேலை செய்ய வேண்டாம்; கருவிகளை கிருமி நீக்கம் செய்யவும்."
    },
    "Tomato___Yellow_Leaf_Curl": {
        "crop": "Tomato",
        "disease": "Yellow Leaf Curl Virus",
        "display_name": "Tomato Yellow Leaf Curl Virus (TYLCV)",
        "display_name_ta": "தக்காளி இலை சுருள் நச்சுயிரி",
        "pathogen": "Begomovirus (Whitefly-transmitted)",
        "description": "Severe interveinal chlorosis, upward leaf cupping, and stunted bushy growth.",
        "management": "Install yellow sticky traps for whiteflies; rogue out infected plants; use reflective mulch.",
        "management_ta": "வெள்ளை ஈக்களை கட்டுப்படுத்த மஞ்சள் ஒட்டும் பொறிகளை நிறுவவும்; பாதிக்கப்பட்ட செடிகளை அகற்றவும்."
    },

    # 2. POTATO
    "Potato___healthy": {
        "crop": "Potato",
        "disease": "Healthy",
        "display_name": "Healthy Potato Foliage",
        "display_name_ta": "ஆரோக்கியமான உருளைக்கிழங்கு இலை",
        "pathogen": "None",
        "description": "Uniform green compound leaves without foliar spotting.",
        "management": "Ensure adequate hilling and balanced potassium fertilization.",
        "management_ta": "மண் அணைத்து சீரான பொட்டாஷ் உரமிடவும்."
    },
    "Potato___Early_blight": {
        "crop": "Potato",
        "disease": "Early Blight",
        "display_name": "Potato Early Blight (Alternaria solani)",
        "display_name_ta": "உருளைக்கிழங்கு முன் கருகல் நோய்",
        "pathogen": "Alternaria solani (Fungus)",
        "description": "Circular dark brown lesions with concentric rings on senescing foliage.",
        "management": "Maintain plant vigor; rotate with non-solanaceous crops for 3 years.",
        "management_ta": "செடியின் வளர்ச்சியை பராமரிக்கவும்; 3 ஆண்டுகளுக்கு பயிர் சுழற்சி செய்யவும்."
    },
    "Potato___Late_blight": {
        "crop": "Potato",
        "disease": "Late Blight",
        "display_name": "Potato Late Blight (Phytophthora infestans)",
        "display_name_ta": "உருளைக்கிழங்கு பின் கருகல் நோய்",
        "pathogen": "Phytophthora infestans (Oomycete)",
        "description": "Large irregular water-soaked dark blights that rapidly spread in wet conditions.",
        "management": "Destroy volunteer tubers; improve field drainage; consult extension agronomist.",
        "management_ta": "வயல் வடிகால் வசதியை மேம்படுத்தவும்; வேளாண் அதிகாரியின் பரிந்துரைப்படி செயல்படவும்."
    },

    # 3. RICE
    "Rice___healthy": {
        "crop": "Rice",
        "disease": "Healthy",
        "display_name": "Healthy Paddy Rice Leaf",
        "display_name_ta": "ஆரோக்கியமான நெல் இலை",
        "pathogen": "None",
        "description": "Slender linear blades with vibrant green chlorophyll content.",
        "management": "Maintain optimal standing water depth and balanced split nitrogen doses.",
        "management_ta": "சரியான நீர்மட்டத்தை பராமரிக்கவும், தழைச்சத்தை பிரித்து இடவும்."
    },
    "Rice___Bacterial_leaf_blight": {
        "crop": "Rice",
        "disease": "Bacterial Leaf Blight",
        "display_name": "Rice Bacterial Leaf Blight (Xanthomonas oryzae)",
        "display_name_ta": "நெல் பாக்டீரியா இலை கருகல் நோய்",
        "pathogen": "Xanthomonas oryzae pv. oryzae",
        "description": "Water-soaked streaks starting at blade margins, turning wavy gray-white.",
        "management": "Drain field temporarily; avoid top-dressing nitrogen during active infection.",
        "management_ta": "வயலில் உள்ள தண்ணீரை வடிகட்டவும்; தீவிரமான போது தழைச்சத்து உரமிடுவதை தவிர்க்கவும்."
    },
    "Rice___Blast": {
        "crop": "Rice",
        "disease": "Rice Leaf Blast",
        "display_name": "Rice Leaf Blast (Magnaporthe oryzae)",
        "display_name_ta": "நெல் இலை குலை நோய்",
        "pathogen": "Magnaporthe oryzae (Fungus)",
        "description": "Spindle-shaped or diamond lesions with grayish centers and brown borders.",
        "management": "Treat seeds with Pseudomonas fluorescens; maintain 2-3 cm continuous water submergence.",
        "management_ta": "சூடோமோனாஸ் மூலம் விதை நேர்த்தி செய்யவும்; வயலில் சீரான நீர் வைக்கவும்."
    },
    "Rice___Brown_spot": {
        "crop": "Rice",
        "disease": "Rice Brown Spot",
        "display_name": "Rice Brown Spot (Bipolaris oryzae)",
        "display_name_ta": "நெல் பழுப்பு புள்ளி நோய்",
        "pathogen": "Bipolaris oryzae (Fungus)",
        "description": "Oval brown spots with gray or whitish centers across the leaf blades.",
        "management": "Correct silicon and potassium soil deficiencies; treat nursery seedbeds.",
        "management_ta": "பொட்டாஷ் மற்றும் நுண்ணூட்டச்சத்து குறைபாடுகளை சரிசெய்யவும்."
    },

    # 4. COTTON
    "Cotton___healthy": {
        "crop": "Cotton",
        "disease": "Healthy",
        "display_name": "Healthy Cotton Foliage",
        "display_name_ta": "ஆரோக்கியமான பருத்தி இலை",
        "pathogen": "None",
        "description": "Vigorous palmate-lobed leaves free from bacterial angular water-soaking.",
        "management": "Monitor square development and maintain integrated pest management.",
        "management_ta": "பூ மொட்டுகளை கண்காணிக்கவும், ஒருங்கிணைந்த பூச்சி மேலாண்மை பின்பற்றவும்."
    },
    "Cotton___Bacterial_blight": {
        "crop": "Cotton",
        "disease": "Bacterial Blight",
        "display_name": "Cotton Angular Leaf Spot (Bacterial Blight)",
        "display_name_ta": "பருத்தி பாக்டீரியா கோண இலைப்புள்ளி",
        "pathogen": "Xanthomonas citri pv. malvacearum",
        "description": "Angular water-soaked spots bounded by leaf veins; can cause black arm on stems.",
        "management": "Use acid-delinted certified seeds; destroy crop residues post-harvest.",
        "management_ta": "சான்றளிக்கப்பட்ட விதைகளை பயன்படுத்தவும்; அறுவடைக்கு பின் எச்சங்களை அழிக்கவும்."
    },
    "Cotton___Leaf_curl": {
        "crop": "Cotton",
        "disease": "Cotton Leaf Curl Virus",
        "display_name": "Cotton Leaf Curl Virus (CLCuV)",
        "display_name_ta": "பருத்தி இலை சுருள் நச்சுயிரி",
        "pathogen": "Begomovirus (Whitefly-borne)",
        "description": "Upward or downward leaf curling, vein thickening, and enation cups under leaves.",
        "management": "Manage whitefly vectors with neem-based deterrents; cultivate resistant hybrids.",
        "management_ta": "வேப்ப எண்ணெய் கொண்டு வெள்ளை ஈக்களை கட்டுப்படுத்தவும்; எதிர்ப்பு ரகங்களை பயிரிடவும்."
    },

    # 5. MAIZE / CORN
    "Maize___healthy": {
        "crop": "Maize",
        "disease": "Healthy",
        "display_name": "Healthy Maize Leaf",
        "display_name_ta": "ஆரோக்கியமான மக்காச்சோள இலை",
        "pathogen": "None",
        "description": "Broad arching leaf blades with distinct pale central midrib.",
        "management": "Maintain balanced zinc and nitrogen fertilization.",
        "management_ta": "துத்தநாகம் மற்றும் தழைச்சத்து உரங்களை சரிவிகிதத்தில் இடவும்."
    },
    "Maize___Common_rust": {
        "crop": "Maize",
        "disease": "Common Rust",
        "display_name": "Maize Common Rust (Puccinia sorghi)",
        "display_name_ta": "மக்காச்சோள துரு நோய்",
        "pathogen": "Puccinia sorghi (Fungus)",
        "description": "Golden-brown to cinnamon-brown powdery pustules on both leaf surfaces.",
        "management": "Plant rust-resistant hybrids; rotate fields in subsequent cropping cycles.",
        "management_ta": "துரு நோய் எதிர்ப்பு ரகங்களை பயிரிடவும்; பயிர் சுழற்சி மேற்கொள்ளவும்."
    },
    "Maize___Northern_leaf_blight": {
        "crop": "Maize",
        "disease": "Northern Leaf Blight",
        "display_name": "Maize Northern Leaf Blight (Exserohilum turcicum)",
        "display_name_ta": "மக்காச்சோள வடக்கு இலை கருகல் நோய்",
        "pathogen": "Exserohilum turcicum (Fungus)",
        "description": "Cigar-shaped, grayish-green or tan elliptical lesions (3-15 cm long).",
        "management": "Incorporate infected stubble into soil; avoid high density monocropping.",
        "management_ta": "பயிர் கழிவுகளை மண்ணில் மட்கச் செய்யவும்; அதிக அடர்த்தி நடவை தவிர்க்கவும்."
    },

    # 6. PEPPER (BELL)
    "Pepper___healthy": {
        "crop": "Pepper",
        "disease": "Healthy",
        "display_name": "Healthy Pepper Foliage",
        "display_name_ta": "ஆரோக்கியமான குடைமிளகாய் இலை",
        "pathogen": "None",
        "description": "Glossy lanceolate leaves with uniform green color.",
        "management": "Ensure drip watering and adequate magnesium nutrition.",
        "management_ta": "சொட்டு நீர் பாசனம் மற்றும் மெக்னீசியம் சத்தை உறுதிப்படுத்தவும்."
    },
    "Pepper___Bacterial_spot": {
        "crop": "Pepper",
        "disease": "Bacterial Spot",
        "display_name": "Pepper Bacterial Spot (Xanthomonas)",
        "display_name_ta": "மிளகாய் பாக்டீரியா புள்ளி நோய்",
        "pathogen": "Xanthomonas euvesicatoria",
        "description": "Small yellowish-green circular spots with greasy raised margins.",
        "management": "Avoid overhead sprinklers; sanitize stakes and wire supports.",
        "management_ta": "தெளிப்பு நீர்ப்பாசனத்தை தவிர்க்கவும்; ஆதரவு கம்புகளை கிருமி நீக்கம் செய்யவும்."
    },

    # 7. APPLE
    "Apple___healthy": {
        "crop": "Apple",
        "disease": "Healthy",
        "display_name": "Healthy Apple Foliage",
        "display_name_ta": "ஆரோக்கியமான ஆப்பிள் இலை",
        "pathogen": "None",
        "description": "Dark green serrated ovate leaves without blemishes.",
        "management": "Annual winter pruning to ensure open canopy airflow.",
        "management_ta": "மரக்கிளைகளை கவாத்து செய்து சீரான காற்றோட்டத்தை ஏற்படுத்தவும்."
    },
    "Apple___Apple_scab": {
        "crop": "Apple",
        "disease": "Apple Scab",
        "display_name": "Apple Scab (Venturia inaequalis)",
        "display_name_ta": "ஆப்பிள் செதில் புள்ளி நோய்",
        "pathogen": "Venturia inaequalis (Fungus)",
        "description": "Olive-green to velvety brown velvety lesions that darken and distort leaves.",
        "management": "Rake and shred fallen autumn leaves; apply agricultural urea to accelerate leaf decomposition.",
        "management_ta": "விழுந்த இலைகளை அப்புறப்படுத்தி எரிக்கவும்; மட்கும் முறைகளை கையாளவும்."
    },
    "Apple___Black_rot": {
        "crop": "Apple",
        "disease": "Black Rot",
        "display_name": "Apple Black Rot (Botryosphaeria obtusa)",
        "display_name_ta": "ஆப்பிள் கருப்பு அழுகல் நோய்",
        "pathogen": "Botryosphaeria obtusa (Fungus)",
        "description": "Frog-eye leaf spots with purple margins and pale tan centers.",
        "management": "Prune out dead wood and mummified fruit where spores overwinter.",
        "management_ta": "காய்ந்த மரக்கிளைகள் மற்றும் அழுகிய பழங்களை வெட்டி அகற்றவும்."
    }
}
