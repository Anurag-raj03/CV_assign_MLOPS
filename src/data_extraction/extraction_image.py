import os
import shutil
import random
source_base = r"C:\Users\dell\Downloads\archive (1)"
destination_base = r"src\main_dataset\main_raw_data"
num_samples = 100
os.makedirs(destination_base, exist_ok=True)
for label in ['rock', 'paper', 'scissors']:
    src_class = os.path.join(source_base, label)
    dest_class = os.path.join(destination_base, label)
    os.makedirs(dest_class, exist_ok=True)
    all_images = [img for img in os.listdir(src_class) if img.lower().endswith(('.png', '.jpg', '.jpeg'))]
    selected = random.sample(all_images, min(num_samples, len(all_images)))
    for img in selected:
        shutil.copy(os.path.join(src_class, img), os.path.join(dest_class, img))

print("100 images from each class copied successfully!")
