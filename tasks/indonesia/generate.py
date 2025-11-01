import numpy as np
import torch
import torch.nn as nn
from torchvision import models
from PIL import Image
import os

class PandaAttack:
    def __init__(self, model_path='pd_model.pth'):
        # Use CPU instead of MPS to avoid compatibility issues
        self.device = torch.device('cpu')
        
        self.model = models.mobilenet_v2(weights=None)
        self.model.classifier[1] = nn.Linear(self.model.last_channel, 3)
        self.model.load_state_dict(torch.load(model_path, map_location=self.device))
        self.model.to(self.device)
        self.model.eval()
        
        # Disable all in-place operations for compatibility
        for module in self.model.modules():
            if hasattr(module, 'inplace'):
                module.inplace = False
        
        print(f"Model loaded on {self.device}")
        
    def load_image(self, path):
        img = Image.open(path).convert('RGB').resize((224, 224))
        return np.array(img, dtype=np.float32) / 255.0
    
    def attack(self, image, target_class, max_iter=500, lr=0.01, eps=0.2):
        # Convert image to tensor with contiguous memory
        img_t = torch.from_numpy(image).permute(2, 0, 1).unsqueeze(0).to(self.device).contiguous()
        pert = torch.zeros_like(img_t, requires_grad=True, device=self.device)
        opt = torch.optim.Adam([pert], lr=lr)
        
        best_pert = None
        best_conf = 0.0
        
        for i in range(max_iter):
            opt.zero_grad()
            
            # Ensure tensors are contiguous
            adv = torch.clamp(img_t + pert, 0, 1).contiguous()
            out = self.model(adv)
            prob = torch.softmax(out, dim=1)[0, target_class]
            
            loss = -torch.log(prob + 1e-10) + 0.0005 * torch.sum(pert**2)
            loss.backward()
            opt.step()
            
            with torch.no_grad():
                pert.data.clamp_(-eps, eps)
            
            if i % 50 == 0:
                conf = prob.item()
                l2 = torch.norm(pert).item()
                print(f"Iter {i:3d} | Conf: {conf:.4f} | L2: {l2:.4f}")
                
                if conf > best_conf:
                    best_conf = conf
                    best_pert = pert.detach().cpu().numpy()[0].copy()
                
                if conf >= 0.82:
                    print(f"Target reached!")
                    break
        
        final = best_pert if best_pert is not None else pert.detach().cpu().numpy()[0]
        return np.transpose(final, (1, 2, 0)), best_conf
    
    def generate(self, img_path, out_path='perturbation.npy'):
        image = self.load_image(img_path)
        
        with torch.no_grad():
            img_t = torch.from_numpy(image).permute(2, 0, 1).unsqueeze(0).to(self.device).contiguous()
            pred = torch.softmax(self.model(img_t), dim=1)[0].cpu().numpy()
        
        print(f"Original predictions: {pred}")
        print(f"Predicted class: {np.argmax(pred)} ({['cats', 'dogs', 'panda'][np.argmax(pred)]})")
        
        best_pert = None
        best_conf = 0.0
        best_cls = None
        
        for cls in range(3):
            print(f"\n{'='*50}")
            print(f"Attempting class {cls} ({['cats', 'dogs', 'panda'][cls]}) as target")
            print(f"{'='*50}")
            
            pert, conf = self.attack(image, cls, max_iter=500, lr=0.01, eps=0.2)
            
            if conf > best_conf:
                best_conf = conf
                best_pert = pert
                best_cls = cls
            
            if conf >= 0.8:
                print(f"\nSuccess with class {cls} ({['cats', 'dogs', 'panda'][cls]})!")
                break
        
        print(f"\n{'='*50}")
        print(f"Best result: class {best_cls} ({['cats', 'dogs', 'panda'][best_cls]})")
        print(f"Confidence: {best_conf:.4f}")
        print(f"{'='*50}")
        
        if best_conf < 0.8:
            print("\nConfidence below threshold. Retrying with stronger parameters...")
            pert, conf = self.attack(image, best_cls, max_iter=800, lr=0.015, eps=0.2)
            if conf > best_conf:
                best_pert = pert
                best_conf = conf
                print(f"New best confidence: {best_conf:.4f}")
        
        best_pert = best_pert.astype(np.float32)
        np.save(out_path, best_pert)
        print(f"\nPerturbation saved to {out_path}")
        
        self.verify(image, out_path)
        return best_pert
    
    def verify(self, image, pert_path):
        pert = np.load(pert_path)
        
        print(f"\n{'='*50}")
        print("VERIFICATION")
        print(f"{'='*50}")
        print(f"Shape: {pert.shape} (expected: (224, 224, 3))")
        print(f"Dtype: {pert.dtype} (expected: float32)")
        print(f"Range: [{pert.min():.4f}, {pert.max():.4f}]")
        print(f"L2 norm: {np.linalg.norm(pert):.4f}")
        print(f"L-inf norm: {np.abs(pert).max():.4f}")
        
        adv = np.clip(image + pert, 0, 1)
        
        with torch.no_grad():
            adv_t = torch.from_numpy(adv).permute(2, 0, 1).unsqueeze(0).to(self.device).contiguous()
            pred = torch.softmax(self.model(adv_t), dim=1)[0].cpu().numpy()
        
        print(f"\nAdversarial predictions:")
        passed = False
        for i, c in enumerate(pred):
            class_name = ['cats', 'dogs', 'panda'][i]
            status = "✓ PASS (>=80%)" if c >= 0.8 else ""
            print(f"  Class {i} ({class_name}): {c:.4f} {status}")
            if c >= 0.8:
                passed = True
        
        print(f"\n{'='*50}")
        if passed:
            print("STATUS: READY TO SUBMIT")
            print("Expected flag: SIGMOID_ADVERSARIAL")
        else:
            print(f"STATUS: NEEDS IMPROVEMENT")
            print(f"Best confidence: {pred.max():.4f}")
            print(f"Required: 0.8000")
            print(f"Gap: {0.8 - pred.max():.4f}")
        print(f"{'='*50}\n")
        
        return passed

def main():
    print("="*50)
    print("PANDA ADVERSARIAL ATTACK")
    print("="*50)
    print()
    
    MODEL_PATH = 'pd_model.pth'
    IMAGE_PATH = 'cat_original_img.jpg'
    OUTPUT_PATH = 'perturbation.npy'
    
    if not os.path.exists(MODEL_PATH):
        print(f"Error: Model file '{MODEL_PATH}' not found!")
        print("Run train_model.py first to create the model.")
        return
    
    if not os.path.exists(IMAGE_PATH):
        print(f"Error: Image file '{IMAGE_PATH}' not found!")
        return
    
    attacker = PandaAttack(MODEL_PATH)
    attacker.generate(IMAGE_PATH, OUTPUT_PATH)
    
    print("\nDone! Submit 'perturbation.npy' to the platform.")

if __name__ == "__main__":
    main()