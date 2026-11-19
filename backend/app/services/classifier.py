from PIL import Image
from ml.src.classification.crop_identifier import CropIdentifier
from ml.src.classification.multi_crop_classifier import MultiCropDiseaseClassifier

class ClassifierService:
    def __init__(self):
        self.crop_identifier = CropIdentifier()
        self.disease_classifier = MultiCropDiseaseClassifier()

    def identify_crop(self, image: Image.Image, requested_crop: str = None) -> dict:
        return self.crop_identifier.identify_crop(image, requested_crop)

    def diagnose_disease(self, image: Image.Image, crop: str = "Tomato") -> dict:
        return self.disease_classifier.predict(image, crop)
