"""
AgriVision AI 2.0 - Mobile Model Exporter
Exports MobileNetV3 crop classification model to TorchScript (PyTorch Mobile / ExecuTorch)
and ONNX (if onnx package is available), plus class metadata JSON for mobile on-device inference.
"""

import os
import json
import torch
import torch.nn as nn
from torchvision import models
from ml.configs.crop_disease_catalog import SUPPORTED_CROPS, CROP_DISEASE_REGISTRY

MODELS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "mobile", "assets", "models"))
os.makedirs(MODELS_DIR, exist_ok=True)

class AgriVisionMobileNet(nn.Module):
    """
    Lightweight MobileNetV3-Small backbone for real-time edge crop & disease classification.
    """
    def __init__(self, num_crops=7, num_diseases=23):
        super().__init__()
        self.backbone = models.mobilenet_v3_small(weights=None)
        in_features = self.backbone.classifier[0].in_features
        self.backbone.classifier = nn.Identity()
        
        self.crop_head = nn.Sequential(
            nn.Linear(in_features, 64),
            nn.Hardswish(),
            nn.Dropout(p=0.2),
            nn.Linear(64, num_crops)
        )
        self.disease_head = nn.Sequential(
            nn.Linear(in_features, 128),
            nn.Hardswish(),
            nn.Dropout(p=0.2),
            nn.Linear(128, num_diseases)
        )

    def forward(self, x):
        feat = self.backbone(x)
        crop_logits = self.crop_head(feat)
        disease_logits = self.disease_head(feat)
        return crop_logits, disease_logits

def export():
    print(f"[*] Preparing AgriVision AI MobileNetV3 export...")
    crop_list = list(SUPPORTED_CROPS)
    
    # Flatten all diseases
    all_diseases = []
    for reg_key, reg_data in CROP_DISEASE_REGISTRY.items():
        all_diseases.append({
            "key": reg_key,
            "crop": reg_data.get("crop", "Unknown"),
            "disease": reg_data.get("disease", reg_key),
            "display_name": reg_data.get("display_name", reg_key),
            "display_name_ta": reg_data.get("display_name_ta", "")
        })
            
    print(f"[*] Total Supported Crops: {len(crop_list)}")
    print(f"[*] Total Supported Disease Classes: {len(all_diseases)}")
    
    model = AgriVisionMobileNet(num_crops=len(crop_list), num_diseases=len(all_diseases))
    model.eval()
    
    dummy_input = torch.randn(1, 3, 224, 224, requires_grad=False)
    
    # 1. Export TorchScript for PyTorch Mobile / ExecuTorch
    ts_path = os.path.join(MODELS_DIR, "mobilenetv3_crop.pt")
    scripted_model = torch.jit.trace(model, dummy_input)
    scripted_model.save(ts_path)
    print(f"[+] Successfully exported TorchScript model to: {ts_path} ({os.path.getsize(ts_path)} bytes)")
    
    # Also save raw PyTorch weights
    weights_path = os.path.join(MODELS_DIR, "mobilenetv3_crop_weights.pth")
    torch.save(model.state_dict(), weights_path)
    print(f"[+] Saved model weights to: {weights_path}")
    
    # 2. Try ONNX export if onnx library is available
    try:
        import onnx
        onnx_path = os.path.join(MODELS_DIR, "mobilenetv3_crop.onnx")
        torch.onnx.export(
            model,
            dummy_input,
            onnx_path,
            export_params=True,
            opset_version=14,
            do_constant_folding=True,
            input_names=['input_image'],
            output_names=['crop_logits', 'disease_logits'],
            dynamic_axes={
                'input_image': {0: 'batch_size'},
                'crop_logits': {0: 'batch_size'},
                'disease_logits': {0: 'batch_size'}
            }
        )
        print(f"[+] Successfully exported ONNX model to: {onnx_path} ({os.path.getsize(onnx_path)} bytes)")
    except Exception as e:
        print(f"[!] ONNX export skipped ({e}). TorchScript mobile model is active.")

    # 3. Write metadata JSON
    meta_path = os.path.join(MODELS_DIR, "class_names.json")
    metadata = {
        "model_name": "AgriVision_MobileNetV3_MultiCrop",
        "input_shape": [1, 3, 224, 224],
        "crops": crop_list,
        "diseases": all_diseases,
        "input_mean": [0.485, 0.456, 0.406],
        "input_std": [0.229, 0.224, 0.225],
        "supported_crops_count": len(crop_list),
        "total_classes": len(all_diseases)
    }
    
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)
        
    print(f"[+] Exported class labels and metadata to: {meta_path}")

if __name__ == "__main__":
    export()
