import sys
import asyncio
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import httpx
from agrivision.main import app
from agrivision.config import SAMPLES_DIR

async def test_async_endpoints():
    print("Testing AgriVision ASGI Endpoints with httpx.ASGITransport...")
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
        # 1. Health
        res = await client.get("/health")
        assert res.status_code == 200, f"Health failed: {res.text}"
        print("  --> /health: 200 OK", res.json())

        # 2. Models
        res = await client.get("/api/v1/models")
        assert res.status_code == 200
        models = res.json()["models"]
        print(f"  --> /api/v1/models: 200 OK ({len(models)} models registered)")

        # 3. Farms
        res = await client.get("/api/v1/farms")
        assert res.status_code == 200
        farms = res.json()
        print(f"  --> /api/v1/farms: 200 OK ({len(farms)} farms found)")

        # 4. Samples
        res = await client.get("/api/v1/samples")
        assert res.status_code == 200
        samples = res.json()
        print(f"  --> /api/v1/samples: 200 OK ({len(samples)} samples available)")

        # 5. Weather Risk
        res = await client.get("/api/v1/weather/risk?temperature=26&humidity=80&rainfall=3")
        assert res.status_code == 200
        w = res.json()
        print(f"  --> /api/v1/weather/risk: 200 OK (Risk: {w['risk_score']}%, Level: {w['risk_level']})")

        # 6. POST /api/v1/inspect with real image
        sample_path = SAMPLES_DIR / "sample_early_blight.jpg"
        with open(sample_path, "rb") as f:
            files = {"file": ("sample_early_blight.jpg", f.read(), "image/jpeg")}
            data = {
                "farm_id": farms[0]["farm_id"],
                "temperature": "26.5",
                "humidity": "82.0",
                "rainfall": "4.0",
                "growth_stage": "Fruiting"
            }
            res = await client.post("/api/v1/inspect", data=data, files=files)
            assert res.status_code == 200, f"Inspect failed: {res.text}"
            insp = res.json()
            print(f"  --> /api/v1/inspect: 200 OK (Inspection ID: {insp['inspection_id']}, Condition: {insp['classification']['disease_display']})")

        # 7. GET /api/v1/inspections
        res = await client.get("/api/v1/inspections")
        assert res.status_code == 200
        print(f"  --> /api/v1/inspections: 200 OK ({len(res.json())} inspections recorded)")

        # 8. GET /api/v1/farms/{id}/health
        res = await client.get(f"/api/v1/farms/{farms[0]['farm_id']}/health")
        assert res.status_code == 200
        print(f"  --> /api/v1/farms/{{id}}/health: 200 OK (Health Index: {res.json()['health_score']})")

        # 9. POST /api/v1/feedback
        fb_payload = {
            "inspection_id": insp["inspection_id"],
            "verified_disease": "Tomato___Early_blight",
            "agreement": "agree",
            "comments": "Early blight verified by foliar analysis.",
            "expert_name": "Dr. K. Patel"
        }
        res = await client.post("/api/v1/feedback", json=fb_payload)
        assert res.status_code == 200
        print(f"  --> /api/v1/feedback: 200 OK (Status: {res.json()['inspection_status']})")

    print("\nALL ASGI API ENDPOINTS FULLY VERIFIED AND PASSING!")

if __name__ == "__main__":
    asyncio.run(test_async_endpoints())
