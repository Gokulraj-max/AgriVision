import io
import uuid
import numpy as np
from PIL import Image, ImageOps
import cv2
import torch
from torchvision import transforms
from agrivision.config import UPLOAD_DIR, IMAGE_SIZE, UNET_INPUT_SIZE

# PyTorch Inference Transform
CLASSIFIER_TRANSFORM = transforms.Compose([
    transforms.Resize(IMAGE_SIZE),
    transforms.ToTensor(),
    transforms.Normalize(
        mean=[0.485, 0.456, 0.406],
        std=[0.229, 0.224, 0.225]
    )
])

UNET_TRANSFORM = transforms.Compose([
    transforms.Resize(UNET_INPUT_SIZE),
    transforms.ToTensor()
])

class ImageService:
    @staticmethod
    def validate_and_load(file_bytes: bytes, filename: str = "upload.jpg"):
        """
        Validates the raw image bytes, checks size, format, corruption, and leaf presence.
        Returns:
            dict containing PIL image, status, metadata, and error message if any.
        """
        if len(file_bytes) < 1024:
            return {"valid": False, "error": "File size too small (minimum 1KB required)."}
        if len(file_bytes) > 20 * 1024 * 1024:
            return {"valid": False, "error": "File size exceeds 20MB limit."}

        try:
            image = Image.open(io.BytesIO(file_bytes))
            # Auto-orient based on EXIF tag if present
            image = ImageOps.exif_transpose(image)
            image = image.convert("RGB")
        except Exception as e:
            return {"valid": False, "error": f"Invalid or corrupt image format: {str(e)}"}

        width, height = image.size
        if width < 50 or height < 50:
            return {"valid": False, "error": f"Image resolution too low ({width}x{height}). Minimum 50x50."}

        # Check leaf presence heuristic via vegetation index (Excess Green: 2G - R - B)
        np_img = np.array(image)
        r = np_img[:, :, 0].astype(np.float32)
        g = np_img[:, :, 1].astype(np.float32)
        b = np_img[:, :, 2].astype(np.float32)
        exg = 2 * g - r - b
        green_ratio = np.mean(exg > 10)

        # Non-leaf warning indicator
        is_likely_foliage = bool(green_ratio > 0.05 or np.mean(g) > 40)

        return {
            "valid": True,
            "image": image,
            "width": width,
            "height": height,
            "is_foliage": is_likely_foliage,
            "green_ratio": float(green_ratio),
            "error": None if is_likely_foliage else "Warning: Image does not appear to contain standard crop foliage."
        }

    @staticmethod
    def save_image(image: Image.Image, prefix: str = "leaf") -> tuple[str, str]:
        """
        Saves image to uploads directory and returns (relative_url, absolute_path).
        """
        filename = f"{prefix}_{uuid.uuid4().hex[:10]}.jpg"
        filepath = UPLOAD_DIR / filename
        image.save(filepath, format="JPEG", quality=90)
        rel_url = f"/uploads/{filename}"
        return rel_url, str(filepath)

    @staticmethod
    def prepare_classifier_tensor(image: Image.Image) -> torch.Tensor:
        """Converts PIL Image to normalized PyTorch tensor [1, 3, 224, 224]."""
        tensor = CLASSIFIER_TRANSFORM(image)
        return tensor.unsqueeze(0)

    @staticmethod
    def prepare_unet_tensor(image: Image.Image) -> torch.Tensor:
        """Converts PIL Image to PyTorch tensor [1, 3, 256, 256]."""
        tensor = UNET_TRANSFORM(image)
        return tensor.unsqueeze(0)
