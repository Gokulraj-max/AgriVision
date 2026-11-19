import uuid
import numpy as np
from PIL import Image
import cv2
import torch
from agrivision.config import UPLOAD_DIR, UNET_INPUT_SIZE, WEIGHTS_DIR
from agrivision.models.unet_net import UNet
from agrivision.services.image_service import ImageService

class SegmentationService:
    """
    PyTorch U-Net Segmentation Service.
    Produces pixel-level masks for diseased lesions and leaf canopy.
    """
    def __init__(self):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.unet = self._load_unet()

    def _load_unet(self):
        model = UNet(n_channels=3, n_classes=1)
        checkpoint = WEIGHTS_DIR / "unet_leaf_disease.pth"
        if checkpoint.exists():
            try:
                state_dict = torch.load(checkpoint, map_location=self.device)
                model.load_state_dict(state_dict)
            except Exception:
                pass
        model.to(self.device)
        model.eval()
        return model

    def segment_leaf_and_disease(self, pil_image: Image.Image, predicted_disease: str = "Tomato___Early_blight") -> dict:
        """
        Performs segmentation:
        1. Leaf Canopy Mask (green/yellow/brown foliar tissue separated from background)
        2. Diseased Lesion Mask (necrotic spots, chlorotic patches, fungal growth)
        Returns:
            leaf_pixels: int
            affected_pixels: int
            mask_url: URL to binary lesion mask
            overlay_url: URL to translucent colored heatmap overlay
        """
        orig_w, orig_h = pil_image.size
        img_np = np.array(pil_image)
        hsv = cv2.cvtColor(img_np, cv2.COLOR_RGB2HSV)

        # 1. Total Leaf Canopy Segmentation (Separates foliage from background)
        # Background is typically white/neutral in PlantVillage, or soil/sky in PlantDoc
        h = hsv[:, :, 0]
        s = hsv[:, :, 1]
        v = hsv[:, :, 2]

        # Leaf tissue (greens, yellows, browns) vs non-leaf background
        # PlantVillage background is typically very light or very dark or plain gray
        is_not_plain_bg = ~((s < 25) & (v > 200)) & ~((s < 20) & (v < 30))
        # Foliage Hue range (from deep brown ~10 to bright green ~85)
        foliage_hue = (h >= 8) & (h <= 95) & (s >= 25)
        leaf_mask = (foliage_hue | (is_not_plain_bg & (s > 35))).astype(np.uint8) * 255

        # Morphological close on leaf canopy
        kernel_large = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (9, 9))
        leaf_mask = cv2.morphologyEx(leaf_mask, cv2.MORPH_CLOSE, kernel_large)

        total_leaf_pixels = int(np.count_nonzero(leaf_mask))
        if total_leaf_pixels == 0:
            total_leaf_pixels = orig_w * orig_h  # fallback if entirely green

        # 2. Disease Lesion Mask via U-Net & Morphological Pathology
        # If healthy, lesions are virtually zero
        if predicted_disease == "Tomato___healthy":
            disease_mask = np.zeros((orig_h, orig_w), dtype=np.uint8)
        else:
            # U-Net forward pass
            tensor = ImageService.prepare_unet_tensor(pil_image).to(self.device)
            with torch.no_grad():
                unet_pred = self.unet(tensor).cpu().numpy()[0, 0]  # (256, 256)

            # Resize U-Net output to original image resolution
            unet_resized = cv2.resize(unet_pred, (orig_w, orig_h), interpolation=cv2.INTER_LINEAR)

            # High precision colorimetric pathology masks
            # Necrotic spots: brown/black within leaf
            brown_lesions = (((h >= 7) & (h <= 24) & (s >= 35) & (v <= 150)) | (v <= 45)) & (leaf_mask > 0)
            # Chlorosis: pale yellowing/stippling
            yellow_chlorosis = ((h >= 18) & (h <= 34) & (s >= 50) & (v >= 60)) & (leaf_mask > 0)
            
            color_lesions = (brown_lesions | yellow_chlorosis).astype(np.float32)

            # Combined score: U-Net prediction + pathology spectral features
            combined_lesion_prob = 0.5 * unet_resized + 0.5 * color_lesions
            
            # Threshold to binary mask
            disease_mask = (combined_lesion_prob > 0.40).astype(np.uint8) * 255
            disease_mask = cv2.bitwise_and(disease_mask, disease_mask, mask=leaf_mask)

            # Smooth mask
            kernel_small = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
            disease_mask = cv2.morphologyEx(disease_mask, cv2.MORPH_OPEN, kernel_small)

        affected_pixels = int(np.count_nonzero(disease_mask))

        # 3. Generate Visual Artifacts:
        # A. Binary Mask Image (Black & White)
        mask_pil = Image.fromarray(disease_mask)
        mask_filename = f"mask_{uuid.uuid4().hex[:10]}.png"
        mask_path = UPLOAD_DIR / mask_filename
        mask_pil.save(mask_path)
        mask_url = f"/uploads/{mask_filename}"

        # B. Translucent Color Overlay (Heatmap style on top of original leaf)
        # Red/Magenta glow for diseased areas, subtle green contour for leaf boundary
        overlay_bgr = cv2.cvtColor(img_np, cv2.COLOR_RGB2BGR)

        # Draw leaf boundary in subtle cyan
        contours_leaf, _ = cv2.findContours(leaf_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        cv2.drawContours(overlay_bgr, contours_leaf, -1, (255, 230, 0), 1)

        # Create colored lesion layer
        lesion_layer = np.zeros_like(overlay_bgr)
        # BGR (0, 0, 255) is vivid red in OpenCV
        lesion_layer[disease_mask > 0] = [30, 30, 240]

        # Blend with alpha
        alpha = 0.55
        cv2.addWeighted(lesion_layer, alpha, overlay_bgr, 1.0, 0, overlay_bgr)

        # Draw outer contours on lesions
        contours_lesion, _ = cv2.findContours(disease_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        cv2.drawContours(overlay_bgr, contours_lesion, -1, (0, 255, 255), 2)

        overlay_rgb = cv2.cvtColor(overlay_bgr, cv2.COLOR_BGR2RGB)
        overlay_pil = Image.fromarray(overlay_rgb)
        overlay_filename = f"overlay_{uuid.uuid4().hex[:10]}.jpg"
        overlay_path = UPLOAD_DIR / overlay_filename
        overlay_pil.save(overlay_path, format="JPEG", quality=92)
        overlay_url = f"/uploads/{overlay_filename}"

        return {
            "total_leaf_pixels": total_leaf_pixels,
            "affected_pixels": affected_pixels,
            "mask_url": mask_url,
            "overlay_url": overlay_url
        }
