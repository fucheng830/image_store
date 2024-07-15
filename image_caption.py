from PIL import Image
import torch
from transformers import BlipProcessor, BlipForConditionalGeneration
from io import BytesIO
import os

image_captioning_model_path = os.environ.get("IMAGE_CAPTIONING_MODEL_PATH", "/home/ubuntu/data/model_data/blip-image-captioning-base")

class ImageCaptioning:
    def __init__(self, device):
        print(f"Initializing ImageCaptioning to {device}")
        self.device = device
        self.torch_dtype = torch.float16 if 'cuda' in device else torch.float32
        self.processor = BlipProcessor.from_pretrained(image_captioning_model_path)
        self.model = BlipForConditionalGeneration.from_pretrained(
            image_captioning_model_path, torch_dtype=self.torch_dtype).to(self.device)

    def generate_caption(self, image_bytes):
        # 打开图像文件
        image = Image.open(BytesIO(image_bytes))
        inputs = self.processor(image, return_tensors="pt").to(self.device, self.torch_dtype)
        out = self.model.generate(**inputs)
        captions = self.processor.decode(out[0], skip_special_tokens=True)
        print(f"\nProcessed ImageCaptioning, Output Text: {captions}")
        return captions

# 初始化设备
device = 'cuda' if torch.cuda.is_available() else 'cpu'
image_captioning = ImageCaptioning(device=device)

# 测试代码，假设 image_bytes 是图像的字节内容
# image_bytes = ...
# caption = image_captioning.generate_caption(image_bytes)
# print(caption)
