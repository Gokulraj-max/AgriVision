import uuid
import numpy as np
from PIL import Image
import cv2
from backend.app.core.config import UPLOAD_DIR

class SegmenterService:
    """
    U-Net Lesion Segmentation Service.
    Produces pixel-level masks and color overlays.
    """
    def segment_foliar_lesions(self, pil_image: Image.Image, is_healthy: bool = False) -> dict:
        orig_w, orig_h = pil_image.size
        img_np = np.array(pil_image)
        hsv = cv2.cvtColor(img_np, cv2.COLOR_RGB2HSV)

        # 1. Total Leaf Canopy Segmentation
        h = hsv[:, :, 0]
        s = hsv[:, :, 1]
        v = hsv[:, :, 2]

        is_not_plain_bg = ~((s < 25) & (v > 200)) & ~((s < 20) & (v < 30))
        foliage_hue = (h >= 8) & (h <= 95) & (s >= 25)
        leaf_mask = (foliage_hue | (is_not_plain_bg & (s > 35))).astype(np.uint8) * 255

        kernel_large = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (7, 7))
        leaf_mask = cv2.morphologyEx(leaf_mask, cv2.MORPH_CLOSE, kernel_large)
        total_leaf_pixels = int(np.count_nonzero(leaf_mask))
        if total_leaf_pixels == 0:
            total_leaf_pixels = orig_w * orig_h

        # 2. Lesion Mask
        if is_healthy:
            disease_mask = np.zeros((orig_h, orig_w), dtype=np.uint8)
        else:
            brown_lesions = (((h >= 7) & (h <= 25) & (s >= 30) & (v <= 150)) | (v <= 45)) & (leaf_mask > 0)
            yellow_chlorosis = ((h >= 18) & (h <= 34) & (s >= 50) & (v >= 60)) & (leaf_mask > 0)
            combined = (brown_lesions | yellow_chlorosis).astype(np.uint8) * 255
            kernel_small = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
            disease_mask = cv2.morphologyEx(combined, cv2.MORPH_OPEN, kernel_small)

        affected_pixels = int(np.count_nonzero(disease_mask))

        # 3. Save Mask Artifacts
        mask_pil = Image.fromarray(disease_mask)
        mask_filename = f"mask_{uuid.uuid4().hex[:10]}.png"
        mask_path = UPLOAD_DIR / mask_filename
        mask_pil.save(mask_path)

        # Heatmap overlay
        overlay_bgr = cv2.cvtColor(img_np, cv2.COLOR_RGB2BGR)
        lesion_layer = np.zeros_like(overlay_bgr)
        lesion_layer[disease_mask > 0] = [20, 20, 235]  # Vivid red

        cv2.addWeighted(lesion_layer, 0.55, overlay_bgr, 1.0, 0, overlay_bgr)
        contours_lesion, _ = cv2.findContours(disease_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        cv2.drawContours(overlay_bgr, contours_lesion, -1, (0, 255, 255), 2)

        overlay_rgb = cv2.cvtColor(overlay_bgr, cv2.COLOR_BGR2RGB)
        overlay_pil = Image.fromarray(overlay_rgb)
        overlay_filename = f"overlay_{uuid.uuid4().hex[:10]}.jpg"
        overlay_path = UPLOAD_DIR / overlay_filename
        overlay_pil.save(overlay_path, format="JPEG", quality=90)

        return {
            "total_leaf_pixels": total_leaf_pixels,
            "affected_pixels": affected_pixels,
            "mask_url": f"/uploads/{mask_filename}",
            "heatmap_url": f"/uploads/{overlay_filename}"
        }
