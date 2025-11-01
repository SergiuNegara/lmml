import numpy as np
import torch
import torch.nn as nn
from torchvision import models
from PIL import Image

def test_perturbation():
    device = torch.device('cpu')
    
    # Load model
    model = models.mobilenet_v2(weights=None)
    model.classifier[1] = nn.Linear(model.last_channel, 3)
    model.load_state_dict(torch.load('pd_model.pth', map_location=device))
    model.to(device)
    model.eval()
    
    for module in model.modules():
        if hasattr(module, 'inplace'):
            module.inplace = False
    
    # Load image
    img = Image.open('cat_original_img.jpg').convert('RGB').resize((224, 224))
    image = np.array(img, dtype=np.float32) / 255.0
    
    # Load perturbation
    pert = np.load('perturbation.npy')
    
    # Verify format
    assert pert.shape == (224, 224, 3), f"Wrong shape: {pert.shape}"
    assert pert.dtype == np.float32, f"Wrong dtype: {pert.dtype}"
    
    # Apply perturbation (exactly as evaluation does)
    adv = np.clip(image + pert, 0, 1)
    
    # Test
    with torch.no_grad():
        adv_t = torch.from_numpy(adv).permute(2, 0, 1).unsqueeze(0).to(device).contiguous()
        pred = torch.softmax(model(adv_t), dim=1)[0].cpu().numpy()
    
    # Results
    classes = ['cats', 'dogs', 'panda']
    print(f"Shape: {pert.shape}")
    print(f"Dtype: {pert.dtype}")
    print(f"Range: [{pert.min():.4f}, {pert.max():.4f}]")
    print(f"\nPredictions:")
    for i, c in enumerate(pred):
        status = "PASS" if c >= 0.8 else ""
        print(f"  {classes[i]}: {c:.4f} {status}")
    
    if pred[2] >= 0.8:
        print(f"\nPASS on your model")
    else:
        print(f"\nFAIL - panda: {pred[2]:.4f} (need 0.8000)")

if __name__ == "__main__":
    test_perturbation()