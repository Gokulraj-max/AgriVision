import cv2
import numpy as np
from pathlib import Path
import random

SAMPLES_DIR = Path(__file__).resolve().parent.parent / "samples"
SAMPLES_DIR.mkdir(parents=True, exist_ok=True)

def create_base_leaf(size=(480, 480), bg_color=(240, 240, 240)):
    """Draws an anatomically recognizable tomato leaflet with lobes and venation."""
    w, h = size
    img = np.full((h, w, 3), bg_color, dtype=np.uint8)

    # Leaflet outline points (Serrated tomato leaflet)
    center_x, center_y = w // 2, h // 2
    points = []
    num_pts = 60
    for i in range(num_pts):
        angle = (2 * np.pi * i) / num_pts
        # Base elliptical shape stretched vertically
        r = 175 * (1 + 0.35 * np.cos(angle) - 0.4 * np.abs(np.sin(angle)))
        
        # Lobes / serrations characteristic of Solanaceae foliage
        serration = 14 * np.sin(angle * 7) + 8 * np.sin(angle * 13)
        r += serration

        px = int(center_x + r * np.sin(angle) * 0.72)
        py = int(center_y - r * np.cos(angle) * 0.95)
        points.append([px, py])

    leaf_pts = np.array(points, dtype=np.int32)

    # Base leaf color (Lush chlorophyll green)
    cv2.fillPoly(img, [leaf_pts], (42, 138, 52))

    # Leaf mask
    mask = np.zeros((h, w), dtype=np.uint8)
    cv2.fillPoly(mask, [leaf_pts], 255)

    # Add realistic texture gradient & chlorophyll variation
    noise = np.random.normal(0, 7, (h, w, 3)).astype(np.int16)
    temp = img.astype(np.int16) + noise
    img = np.clip(temp, 0, 255).astype(np.uint8)
    img[mask == 0] = bg_color

    # Draw Central Primary Vein
    vein_color = (65, 175, 75)
    cv2.line(img, (center_x, center_y + 160), (center_x, center_y - 165), vein_color, 4, cv2.LINE_AA)

    # Draw Secondary Lateral Veins
    for dy in range(-120, 140, 32):
        y_start = center_y + dy
        # Left vein
        cv2.line(img, (center_x, y_start), (center_x - 90, y_start - 35), vein_color, 2, cv2.LINE_AA)
        # Right vein
        cv2.line(img, (center_x, y_start), (center_x + 90, y_start - 35), vein_color, 2, cv2.LINE_AA)

    return img, mask, (center_x, center_y)


def generate_healthy():
    img, _, _ = create_base_leaf()
    out_path = SAMPLES_DIR / "sample_healthy.jpg"
    cv2.imwrite(str(out_path), img)
    print(f"Generated {out_path.name}")


def generate_early_blight():
    img, mask, (cx, cy) = create_base_leaf()
    
    # Early Blight has characteristic concentric rings ("target board")
    lesion_centers = [
        (cx - 40, cy - 30, 38),
        (cx + 45, cy + 40, 28),
        (cx - 30, cy + 70, 22),
        (cx + 25, cy - 80, 20)
    ]

    for lx, ly, rad in lesion_centers:
        # Yellow chlorotic halo around lesion in BGR (B, G, R): (30, 200, 220)
        cv2.circle(img, (lx, ly), int(rad * 1.55), (30, 200, 220), -1)
        
        # Dark brown necrotic core in BGR: (20, 45, 95)
        cv2.circle(img, (lx, ly), rad, (20, 45, 95), -1)
        
        # Concentric darker rings inside
        for r_step in range(rad - 4, 4, -6):
            cv2.circle(img, (lx, ly), r_step, (12, 25, 60), 2)
            cv2.circle(img, (lx, ly), max(r_step - 2, 1), (30, 60, 110), 2)

    bg_color = (240, 240, 240)
    img[mask == 0] = bg_color

    out_path = SAMPLES_DIR / "sample_early_blight.jpg"
    cv2.imwrite(str(out_path), img)
    print(f"Generated {out_path.name}")


def generate_late_blight():
    img, mask, (cx, cy) = create_base_leaf()

    blotches = [
        (cx - 50, cy - 40, 55, 45),
        (cx + 40, cy - 20, 65, 50),
        (cx, cy + 60, 70, 50)
    ]

    for bx, by, rw, rh in blotches:
        # Faint pale green/yellow water-soaked halo in BGR
        cv2.ellipse(img, (bx, by), (int(rw * 1.25), int(rh * 1.25)), 25, 0, 360, (40, 150, 130), -1)
        # Deep necrotic dark brown / black rot in BGR
        cv2.ellipse(img, (bx, by), (rw, rh), 25, 0, 360, (20, 30, 50), -1)
        cv2.ellipse(img, (bx + 5, by - 5), (int(rw * 0.7), int(rh * 0.7)), 25, 0, 360, (12, 18, 30), -1)

    img[mask == 0] = (240, 240, 240)
    out_path = SAMPLES_DIR / "sample_late_blight.jpg"
    cv2.imwrite(str(out_path), img)
    print(f"Generated {out_path.name}")


def generate_bacterial_spot():
    img, mask, (cx, cy) = create_base_leaf()

    random.seed(42)
    for _ in range(75):
        rx = cx + random.randint(-110, 110)
        ry = cy + random.randint(-130, 130)
        if mask[min(max(ry, 0), 479), min(max(rx, 0), 479)] > 0:
            sz = random.randint(3, 7)
            # Yellow halo in BGR
            cv2.circle(img, (rx, ry), sz + 2, (30, 200, 210), -1)
            # Dark necrotic center in BGR
            cv2.circle(img, (rx, ry), sz, (15, 25, 45), -1)

    img[mask == 0] = (240, 240, 240)
    out_path = SAMPLES_DIR / "sample_bacterial_spot.jpg"
    cv2.imwrite(str(out_path), img)
    print(f"Generated {out_path.name}")


def generate_yellow_curl():
    img, mask, (cx, cy) = create_base_leaf()

    for y in range(480):
        for x in range(480):
            if mask[y, x] > 0:
                dist_from_center = np.sqrt((x - cx)**2 + (y - cy)**2)
                if dist_from_center > 60:
                    blend = min((dist_from_center - 60) / 90.0, 0.85)
                    curr = img[y, x].astype(np.float32)
                    yellow = np.array([35, 215, 225], dtype=np.float32)  # BGR yellow
                    img[y, x] = ((1 - blend) * curr + blend * yellow).astype(np.uint8)

    img[mask == 0] = (240, 240, 240)
    out_path = SAMPLES_DIR / "sample_yellow_curl.jpg"
    cv2.imwrite(str(out_path), img)
    print(f"Generated {out_path.name}")


def generate_spider_mites():
    img, mask, (cx, cy) = create_base_leaf()

    random.seed(101)
    for y in range(480):
        for x in range(480):
            if mask[y, x] > 0 and random.random() < 0.22:
                val = random.choice([(110, 225, 210), (180, 240, 235), (75, 205, 195)])
                cv2.circle(img, (x, y), 1, val, -1)

    img[mask == 0] = (240, 240, 240)
    out_path = SAMPLES_DIR / "sample_spider_mites.jpg"
    cv2.imwrite(str(out_path), img)
    print(f"Generated {out_path.name}")


if __name__ == "__main__":
    generate_healthy()
    generate_early_blight()
    generate_late_blight()
    generate_bacterial_spot()
    generate_yellow_curl()
    generate_spider_mites()
    print("All synthetic sample images successfully created!")
