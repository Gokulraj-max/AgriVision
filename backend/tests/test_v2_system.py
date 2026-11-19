"""
AgriVision AI 2.0 - End-to-End System & API Verification Test Suite
"""

import urllib.request
import json
import base64
import numpy as np
import cv2

BASE_URL = "http://127.0.0.1:8000"

def test_health():
    print("[*] Testing /health...")
    with urllib.request.urlopen(f"{BASE_URL}/health") as resp:
        assert resp.status == 200
        data = json.loads(resp.read().decode())
        assert data["status"] == "healthy"
        assert len(data["supported_crops"]) == 7
        assert "ta" in data["multilingual_voice"]
    print("    [+] /health OK:", data["platform"])

def test_supported_crops():
    print("[*] Testing /api/v1/crops/supported...")
    with urllib.request.urlopen(f"{BASE_URL}/api/v1/crops/supported") as resp:
        assert resp.status == 200
        data = json.loads(resp.read().decode())
        assert "crops" in data
        assert len(data["crops"]) == 7
        assert "registry" in data
    print(f"    [+] /api/v1/crops/supported OK: {len(data['crops'])} crops, {len(data['registry'])} disease classes.")

def test_weather_risk():
    print("[*] Testing /api/v1/weather/risk...")
    with urllib.request.urlopen(f"{BASE_URL}/api/v1/weather/risk?lat=11.0168&lon=76.9558&crop=Tomato") as resp:
        assert resp.status == 200
        data = json.loads(resp.read().decode())
        assert "current" in data
        assert "disease_risk_index" in data["current"]
        assert "pathogen_alerts" in data["current"]
        assert "forecast" in data
    print(f"    [+] /api/v1/weather/risk OK: Risk Level = {data['current']['risk_level']}, Score = {data['current']['disease_risk_index']}")

def test_bilingual_assistant():
    print("[*] Testing /api/v1/assistant/chat (Tamil & English)...")
    
    # Tamil Query
    payload_ta = json.dumps({
        "message": "தக்காளியில் ஆரம்பகால கருகல் நோயை எவ்வாறு தடுப்பது?",
        "language": "ta",
        "crop": "Tomato"
    }).encode("utf-8")
    req_ta = urllib.request.Request(
        f"{BASE_URL}/api/v1/assistant/chat",
        data=payload_ta,
        headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(req_ta) as resp:
        assert resp.status == 200
        res_ta = json.loads(resp.read().decode())
        assert "reply" in res_ta
        assert res_ta["language"] == "ta"
        print("    [+] Tamil Assistant Reply:", res_ta["reply"][:60], "...")

    # English Query
    payload_en = json.dumps({
        "message": "What is the cultural management for rice blast?",
        "language": "en",
        "crop": "Rice"
    }).encode("utf-8")
    req_en = urllib.request.Request(
        f"{BASE_URL}/api/v1/assistant/chat",
        data=payload_en,
        headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(req_en) as resp:
        assert resp.status == 200
        res_en = json.loads(resp.read().decode())
        assert "reply" in res_en
        assert res_en["language"] == "en"
        print("    [+] English Assistant Reply:", res_en["reply"][:60], "...")

def test_live_inspect():
    print("[*] Testing /api/v1/live/inspect (1-2 FPS frame sampling)...")
    # Create synthetic leaf image
    img = np.zeros((300, 300, 3), dtype=np.uint8)
    cv2.circle(img, (150, 150), 100, (40, 150, 40), -1) # Green leaf
    cv2.circle(img, (130, 130), 25, (30, 60, 120), -1)  # Necrotic spot
    _, buf = cv2.imencode(".jpg", img)
    b64_str = base64.b64encode(buf).decode("utf-8")

    payload = json.dumps({
        "image_base64": b64_str,
        "crop_hint": "Tomato"
    }).encode("utf-8")

    req = urllib.request.Request(
        f"{BASE_URL}/api/v1/live/inspect",
        data=payload,
        headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(req) as resp:
        assert resp.status == 200
        res = json.loads(resp.read().decode())
        assert res["has_leaf"] is True
        assert "boxes" in res
        assert "confidence" in res
        print(f"    [+] /api/v1/live/inspect OK: Disease = {res['disease_name']}, Boxes = {len(res['boxes'])}, Severity = {res['severity_pct']}%")

def test_farms():
    print("[*] Testing /api/v1/farms/...")
    with urllib.request.urlopen(f"{BASE_URL}/api/v1/farms/") as resp:
        assert resp.status == 200
        data = json.loads(resp.read().decode())
        assert "farms" in data
        print(f"    [+] /api/v1/farms/ OK: {len(data['farms'])} registered farms.")

def test_root_ui():
    print("[*] Testing GET / (HTML Mobile Simulator UI)...")
    with urllib.request.urlopen(f"{BASE_URL}/") as resp:
        assert resp.status == 200
        content = resp.read().decode()
        assert "AgriVision AI" in content
        assert "viewfinderCanvas" in content
    print("    [+] Root UI & Mobile Simulator successfully served!")

if __name__ == "__main__":
    print("=" * 60)
    print("AgriVision AI 2.0 - Running End-to-End System Tests")
    print("=" * 60)
    test_health()
    test_supported_crops()
    test_weather_risk()
    test_bilingual_assistant()
    test_live_inspect()
    test_farms()
    test_root_ui()
    print("=" * 60)
    print("ALL TESTS PASSED! AgriVision AI 2.0 is 100% operational.")
    print("=" * 60)
