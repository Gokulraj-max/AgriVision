from fastapi import APIRouter
from pathlib import Path
from agrivision.config import SAMPLES_DIR

router = APIRouter(prefix="/api/v1/samples", tags=["Sample Library"])

@router.get("")
def list_sample_images():
    """
    Returns preloaded tomato leaf image presets for instant 1-click testing.
    """
    samples = [
        {
            "id": "sample-early-blight",
            "name": "Early Blight (Alternaria)",
            "disease_key": "Tomato___Early_blight",
            "description": "Foliar specimen showing prominent brown concentric target-ring lesions and mild chlorotic yellow margins.",
            "image_url": "/samples/sample_early_blight.jpg",
            "preset_weather": {"temperature": 27.5, "humidity": 82.0, "rainfall": 3.5, "stage": "Fruiting"}
        },
        {
            "id": "sample-late-blight",
            "name": "Late Blight (Phytophthora)",
            "disease_key": "Tomato___Late_blight",
            "description": "Specimen displaying dark, irregular water-soaked necrotic patches with rapid decay symptoms.",
            "image_url": "/samples/sample_late_blight.jpg",
            "preset_weather": {"temperature": 18.2, "humidity": 94.0, "rainfall": 12.0, "stage": "Vegetative"}
        },
        {
            "id": "sample-healthy",
            "name": "Healthy Tomato Leaf",
            "disease_key": "Tomato___healthy",
            "description": "Clean, vigorous dark green tomato foliage with intact serrated leaf margins and no foliar lesions.",
            "image_url": "/samples/sample_healthy.jpg",
            "preset_weather": {"temperature": 24.0, "humidity": 60.0, "rainfall": 0.0, "stage": "Flowering"}
        },
        {
            "id": "sample-bacterial-spot",
            "name": "Bacterial Spot (Xanthomonas)",
            "disease_key": "Tomato___Bacterial_spot",
            "description": "Numerous small, dark, angular water-soaked speckles surrounded by faint translucent halos.",
            "image_url": "/samples/sample_bacterial_spot.jpg",
            "preset_weather": {"temperature": 29.0, "humidity": 88.0, "rainfall": 8.5, "stage": "Vegetative"}
        },
        {
            "id": "sample-yellow-curl",
            "name": "Yellow Leaf Curl Virus (TYLCV)",
            "disease_key": "Tomato___Tomato_Yellow_Leaf_Curl_Virus",
            "description": "Severe interveinal chlorosis, pale upward leaf cupping, and reduced laminar leaf surface.",
            "image_url": "/samples/sample_yellow_curl.jpg",
            "preset_weather": {"temperature": 32.0, "humidity": 55.0, "rainfall": 0.5, "stage": "Flowering"}
        },
        {
            "id": "sample-spider-mites",
            "name": "Two-Spotted Spider Mites",
            "disease_key": "Tomato___Spider_mites_Two_spotted_spider_mite",
            "description": "Dense yellow stippling and speckled chlorotic bronzing across the upper leaf plane.",
            "image_url": "/samples/sample_spider_mites.jpg",
            "preset_weather": {"temperature": 33.5, "humidity": 42.0, "rainfall": 0.0, "stage": "Fruiting"}
        }
    ]
    return samples
