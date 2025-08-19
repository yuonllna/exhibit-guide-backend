import torch
import lpips
import cv2
import numpy as np
from PIL import Image


def compute_lpips_mask(ref_img, target_img, threshold: float = 0.1):
    loss_fn = lpips.LPIPS(net='alex')
    loss_fn.eval()

    ref = Image.fromarray(ref_img).convert('RGB').resize((256, 256))
    target = Image.fromarray(target_img).convert('RGB').resize((256, 256))

    ref_tensor = torch.tensor(np.array(ref)).permute(2, 0, 1).unsqueeze(0).float() / 127.5 - 1.0
    target_tensor = torch.tensor(np.array(target)).permute(2, 0, 1).unsqueeze(0).float() / 127.5 - 1.0

    with torch.no_grad():
        dist_map = loss_fn.forward(ref_tensor, target_tensor)

    dist_map_np = dist_map[0].mean(0).cpu().numpy()

    mask = (dist_map_np > threshold).astype(np.uint8) * 255

    return dist_map_np, mask
