import numpy as np
import torch
import torch.nn as nn
from torchvision import models
from PIL import Image

class UniversalPandaAttack:
    def __init__(self, model_path='pd_model.pth'):
        self.device = torch.device('cpu')
        self.model = models.mobilenet_v2(weights=None)
        self.model.classifier[1] = nn.Linear(self.model.last_channel, 3)
        self.model.load_state_dict(torch.load(model_path, map_location=self.device))
        self.model.to(self.device)
        self.model.eval()
        
        for module in self.model.modules():
            if hasattr(module, 'inplace'):
                module.inplace = False
        
    def load_image(self, path):
        img = Image.open(path).convert('RGB').resize((224, 224))
        return np.array(img, dtype=np.float32) / 255.0
    
    def ensemble_attack(self, image, target_class, max_iter=1000, lr=0.02, eps=0.2):
        img_t = torch.from_numpy(image).permute(2, 0, 1).unsqueeze(0).to(self.device).contiguous()
        pert = torch.zeros_like(img_t, requires_grad=True, device=self.device)
        opt = torch.optim.SGD([pert], lr=lr, momentum=0.9)
        
        best_pert = None
        best_conf = 0.0
        
        for i in range(max_iter):
            opt.zero_grad()
            adv = torch.clamp(img_t + pert, 0, 1).contiguous()
            out = self.model(adv)
            logits = out[0]
            
            target_logit = logits[target_class]
            other_logits = torch.cat([logits[:target_class], logits[target_class+1:]])
            max_other = torch.max(other_logits)
            
            margin_loss = torch.clamp(max_other - target_logit + 10.0, min=0.0)
            l2_loss = 0.0001 * torch.sum(pert ** 2)
            total_loss = margin_loss + l2_loss
            
            total_loss.backward()
            opt.step()
            
            with torch.no_grad():
                pert.data.clamp_(-eps, eps)
            
            if i % 200 == 0:
                with torch.no_grad():
                    prob = torch.softmax(out, dim=1)[0]
                    conf = prob[target_class].item()
                    if conf > best_conf:
                        best_conf = conf
                        best_pert = pert.detach().cpu().numpy()[0].copy()
                    if conf >= 0.85:
                        break
        
        final = best_pert if best_pert is not None else pert.detach().cpu().numpy()[0]
        return np.transpose(final, (1, 2, 0)), best_conf
    
    def multi_start_attack(self, image, target_class):
        best_overall_pert = None
        best_overall_conf = 0.0
        
        pert1, conf1 = self.ensemble_attack(image, target_class, max_iter=1000, lr=0.02, eps=0.2)
        if conf1 > best_overall_conf:
            best_overall_conf = conf1
            best_overall_pert = pert1
        
        pert2, conf2 = self.ensemble_attack(image, target_class, max_iter=1200, lr=0.03, eps=0.2)
        if conf2 > best_overall_conf:
            best_overall_conf = conf2
            best_overall_pert = pert2
        
        if best_overall_conf < 0.8:
            pert3, conf3 = self.ensemble_attack(image, target_class, max_iter=1500, lr=0.025, eps=0.3)
            if conf3 > best_overall_conf:
                best_overall_conf = conf3
                best_overall_pert = pert3
        
        return best_overall_pert, best_overall_conf
    
    def generate(self, img_path, out_path='perturbation.npy'):
        image = self.load_image(img_path)
        panda_class = 2
        best_pert, best_conf = self.multi_start_attack(image, panda_class)
        best_pert = best_pert.astype(np.float32)
        best_pert = np.clip(best_pert, -0.2, 0.2)
        np.save(out_path, best_pert)
        return best_pert

def main():
    MODEL_PATH = 'pd_model.pth'
    IMAGE_PATH = 'cat_original_img.jpg'
    OUTPUT_PATH = 'perturbation.npy'
    
    attacker = UniversalPandaAttack(MODEL_PATH)
    attacker.generate(IMAGE_PATH, OUTPUT_PATH)

if __name__ == "__main__":
    main()