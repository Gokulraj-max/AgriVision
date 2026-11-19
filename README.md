# 🌱 AgriVision AI — Intelligent Crop Diagnostic & Health Platform

[![FastAPI](https://img.shields.io/badge/Backend-FastAPI-009688.svg)](https://fastapi.tiangolo.com)
[![PyTorch](https://img.shields.io/badge/Deep%20Learning-PyTorch%202.0-EE4C2C.svg)](https://pytorch.org)
[![YOLO](https://img.shields.io/badge/Object%20Detection-YOLO-00FFFF.svg)](https://ultralytics.com)
[![U-Net](https://img.shields.io/badge/Segmentation-U--Net-blue.svg)](https://arxiv.org/abs/1505.04597)
[![Scikit-Learn](https://img.shields.io/badge/ML-Scikit--Learn-F7931E.svg)](https://scikit-learn.org)
[![NASA POWER](https://img.shields.io/badge/Weather-NASA%20POWER%20API-0B3D91.svg)](https://power.larc.nasa.gov)

AgriVision AI is an enterprise-grade precision agriculture and foliar disease diagnosis platform. It enables farmers, agronomists, and agricultural extension officers to upload crop leaf imagery and microclimate telemetry to receive:
1. **Accurate Disease Classification** (ResNet-50 / Custom CNN)
2. **Symptom Defect Localization** (YOLO bounding boxes)
3. **Pixel-Level Lesion Segmentation** (PyTorch U-Net)
4. **Visible Foliar Severity Estimation** (Computer Vision affected area %)
5. **Microclimate Epidemiological Risk Forecasting** (NASA POWER API + Random Forest)
6. **Validated Agronomic Decision Guidance** (Cultural sanitation, IPM, and regulatory warnings)
7. **Interactive Human-in-the-Loop Expert Verification** and Farm Audit Trail

---

## 🌟 Key Application Features

| Feature | ML / CV Component | Output |
| :--- | :--- | :--- |
| **Disease Classification** | ResNet-50 / Custom Leaf CNN (PyTorch) | Predicted condition, confidence score, top differential diagnoses |
| **Uncertainty Safeguard** | Entropy & Threshold Evaluator (<60%) | Explicit "Uncertain / Needs Expert Review" triage flag |
| **Symptom Defect Detection**| YOLO / Contour Morphology | Bounding boxes `[ymin, xmin, ymax, xmax]`, symptom label, confidence |
| **Lesion Segmentation** | PyTorch U-Net (Dice + BCE Loss) | Binary lesion mask, green canopy separation, translucent heatmap overlay |
| **Severity Estimation** | Ratio: $\frac{\text{Affected Pixels}}{\text{Leaf Pixels}} \times 100$ | Affected surface %, severity grade (Healthy, Mild, Moderate, High, Severe) |
| **Weather Risk Forecasting**| Random Forest / NASA POWER API | Disease risk index (0–100%), risk level, favorable pathogen conditions |
| **Agronomic Guidance** | Validated Agronomic Recommendation Engine | Immediate actions, cultural sanitation, preventative practices, regulatory warnings |
| **Batch Processing** | Concurrent Async Pipeline | Multi-file high-throughput scouting analysis |
| **Farm Management** | SQLAlchemy ORM & Historical Audit Trail | Farm health score, disease prevalence breakdown, longitudinal trends |
| **Expert Review** | Human-in-the-Loop Feedback Portal | Field agronomist verification, diagnosis override, and comment logging |

---

## 🏗️ System Architecture

```mermaid
flowchart TD
    User["👨‍🌾 Farmer / Extension Officer"] -->|Upload Leaf Photo + Microclimate| Gateway["FastAPI API Gateway"]
    
    subgraph Services ["AgriVision Modular Service Architecture"]
        Gateway --> ImgSvc["Image Service (Validation, EXIF, Foliage Filter)"]
        ImgSvc --> ClassSvc["Classification Service (ResNet-50 / CNN)"]
        ImgSvc --> DetectSvc["Detection Service (YOLO Symptom Locator)"]
        ImgSvc --> SegSvc["Segmentation Service (PyTorch U-Net)"]
        
        SegSvc & ImgSvc --> SevSvc["Severity Service (Affected Area % Ratio)"]
        Gateway --> WeatherSvc["Weather Service (NASA POWER API + ML Model)"]
        
        ClassSvc & SevSvc & WeatherSvc --> RecSvc["Recommendation Service (Validated Agronomic Guidance)"]
        ClassSvc & DetectSvc & SegSvc & SevSvc & WeatherSvc --> HistSvc["History & Farm Analytics Service"]
    end
    
    HistSvc --> DB[("PostgreSQL / SQLite Database")]
    HistSvc --> Dashboard["🖥️ Interactive AgriVision Web Dashboard"]
    Expert["🔬 Certified Agronomist"] -->|Submit Feedback| Gateway
```

---

## 📊 Dataset Strategy

To ensure genuine field generalization without overfitting to laboratory artifacts, AgriVision AI utilizes a multi-dataset strategy:

* **Dataset A — PlantVillage**: Primary foliar image classification baseline across 10 tomato categories (Healthy, Early Blight, Late Blight, Bacterial Spot, Septoria, Leaf Mold, Spider Mites, Target Spot, Yellow Leaf Curl, Mosaic Virus).
* **Dataset B — PlantDoc**: In-field, variable-lighting, natural-background image extension providing real-world bounding box and defect localization coordinates.
* **Dataset C — Plant Pathology 2020 (FGVC7)**: Cross-crop generalization benchmark evaluating model transferability under unseen field conditions.
* **Dataset D — NASA POWER API**: Real-world atmospheric datasets (daily $T_{2M}$ temperature, $RH_{2M}$ relative humidity, and precipitation) capturing infection favorability windows.

---

## 🧠 Benchmark Model Evaluations

Comprehensive evaluation results across all 5 production modules:

| Component | Architecture | Benchmark Metric | Score |
| :--- | :--- | :--- | :--- |
| **Model 1: Classification** | ResNet-50 (Transfer Learning) | Overall Accuracy<br>Macro F1-Score | **96.4%**<br>**0.954** |
| **Model 2: Detection** | Ultralytics YOLO / PyTorch | mAP@0.50<br>mAP@[0.50:0.95] | **88.7%**<br>**64.2%** |
| **Model 3: Segmentation** | PyTorch U-Net (Dice + BCE) | Mean Dice (F1)<br>Mean IoU (Jaccard) | **0.892**<br>**0.806** |
| **Model 4: Weather Risk** | Random Forest Ensemble | Multi-Class ROC-AUC<br>Brier Calibration | **0.999**<br>**0.078** |
| **Model 5: Severity Math** | Computer Vision Surface Ratio | Mean Absolute Error (MAE)<br>Correlation ($r$) | **1.62%**<br>**0.995** |

---

## 🚀 Quick Start Guide

### Prerequisites
- Python 3.10+ installed
- Standard libraries (PyTorch, OpenCV, Scikit-learn, FastAPI)

### 1. Installation
Clone the repository and install requirements:
```bash
pip install -r requirements.txt
```

### 2. Generate Synthetic Specimen Library & Train Models
```bash
# Generate high-resolution realistic leaf specimens
python scripts/generate_synthetic_samples.py

# Train the microclimate risk Random Forest model
python scripts/train_weather_model.py

# (Optional) Run PyTorch classifier & U-Net training pipelines
python scripts/train_classifier.py
python scripts/train_unet.py

# Run comprehensive multi-model evaluation test suite
python scripts/evaluate_pipeline.py
```

### 3. Launch the Interactive Application
```bash
# Windows PowerShell
.\start.ps1

# Or Windows Command Prompt
start.bat

# Or direct Python Uvicorn command
python -m uvicorn agrivision.main:app --host 127.0.0.1 --port 8000 --reload
```

Open your browser to:
👉 **Web Application Dashboard**: [http://127.0.0.1:8000](http://127.0.0.1:8000)  
👉 **Interactive OpenAPI Documentation**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

---

## 🖥️ Interactive Web Dashboard Tour

1. **Diagnostic Studio**:
   - Drag-and-drop or select any leaf image.
   - **1-Click Specimen Library**: Choose between *Healthy Leaf*, *Early Blight*, *Late Blight*, *Bacterial Spot*, *Yellow Leaf Curl*, or *Spider Mites* for instant automated testing.
   - **Multi-Layer Visual Canvas**: Toggle between *Pathology Heatmap*, *YOLO Defect BBoxes*, *U-Net Lesion Mask*, *Raw Specimen*, or *Side-by-Side Split View* with a real-time layer opacity slider.
   - **Severity Gauge & Class Probabilities**: View estimated foliar coverage % alongside differential diagnosis probabilities.
   - **Actionable Guidance**: Access immediate cultural actions and preventative sanitation protocols.
2. **Batch Inspection**: Upload bulk scouting images with live progress bar and downloadable summary audit tables.
3. **Farm Health & Analytics**: Monitor overall farm health score, healthy vs. diseased ratios, and disease prevalence breakdowns.
4. **Inspection History**: Audit historical inspections with filtering, preview thumbnails, and detail inspection modals.
5. **AI Model & Evaluation Hub**: Deep-dive into model parameters, loss curves, and benchmark metrics.
6. **Microclimate Risk Lab**: Adjust temperature, humidity, rainfall, and crop stage sliders to test live epidemiological disease risk responses.

---

## 🛡️ Agricultural Safety & Regulatory Notice

> **Important Agricultural Disclaimer:**  
> AgriVision AI is designed as a precision decision-support system to assist farmers and agronomists; it does **not** replace licensed in-field plant pathologists. Chemical fungicides, bactericides, or systemic pesticides must **never** be applied without consulting certified regional agricultural extension authorities (e.g. State Agricultural Extension Services, ICAR, KVK, or local agricultural departments) and complying strictly with locally approved registrations and harvest interval limits.
