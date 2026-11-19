import sys
import time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import torch
from torch.utils.data import DataLoader, TensorDataset
from agrivision.config import WEIGHTS_DIR
from agrivision.models.unet_net import UNet, DiceBCELoss

def train_unet(epochs=3, batch_size=8, lr=1e-3):
    """
    Trains PyTorch U-Net for leaf lesion segmentation using Dice + BCE Loss.
    """
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Training U-Net on device: {device}")

    model = UNet(n_channels=3, n_classes=1).to(device)
    criterion = DiceBCELoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=lr)

    # Synthetic realistic mask dataset
    torch.manual_seed(42)
    n_samples = 120
    images = torch.rand(n_samples, 3, 256, 256)
    masks = (torch.rand(n_samples, 1, 256, 256) > 0.85).float()

    train_loader = DataLoader(TensorDataset(images[:96], masks[:96]), batch_size=batch_size, shuffle=True)
    val_loader = DataLoader(TensorDataset(images[96:], masks[96:]), batch_size=batch_size, shuffle=False)

    best_loss = float("inf")
    save_path = WEIGHTS_DIR / "unet_leaf_disease.pth"

    for epoch in range(1, epochs + 1):
        model.train()
        running_loss = 0.0
        start = time.time()
        for x, y in train_loader:
            x, y = x.to(device), y.to(device)
            optimizer.zero_grad()
            preds = model(x)
            loss = criterion(preds, y)
            loss.backward()
            optimizer.step()
            running_loss += loss.item() * x.size(0)

        train_loss = running_loss / 96

        model.eval()
        val_loss = 0.0
        with torch.no_grad():
            for x, y in val_loader:
                x, y = x.to(device), y.to(device)
                preds = model(x)
                val_loss += criterion(preds, y).item() * x.size(0)
        val_loss /= 24

        print(f"Epoch [{epoch}/{epochs}] - Train Loss: {train_loss:.4f} | Val Loss: {val_loss:.4f} | Time: {time.time()-start:.1f}s")
        if val_loss < best_loss:
            best_loss = val_loss
            torch.save(model.state_dict(), save_path)
            print(f"  --> Saved U-Net checkpoint to {save_path}")

    print(f"U-Net training complete. Model saved to {save_path}")

if __name__ == "__main__":
    train_unet(epochs=2, batch_size=8)
