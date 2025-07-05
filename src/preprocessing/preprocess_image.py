import cv2
import os
import shutil
def preprocess_images(input_dir,output_dir,target_size=(224,224)):
    expected_labels = ['rock', 'paper', 'scissors']
    if not os.path.exists(input_dir):
        raise FileNotFoundError(f"Input directory not Found: {input_dir}")
    os.makedirs(output_dir,exist_ok=True)
    for label in expected_labels:
        input_path=os.path.join(input_dir,label)
        output_path=os.path.join(output_dir,label)

        if not os.path.exists(input_path):
            print(f"Skipping missing label folder: {label}")
            continue
        os.makedirs(output_path,exist_ok=True)
        images=[img for img in os.listdir(input_path) if img.lower().endswith(('.png','.jpg','.jpeg'))]
        count=0

        for img_name in images:
            img_path=os.path.join(input_path,img_name)
            output_img_path=os.path.join(output_path,img_name)

            image=cv2.imread(img_path)
            if image is None:
                print(f"Unreadable image skippend {img_name}")
                continue
            image=cv2.cvtColor(image,cv2.COLOR_BGR2RGB)
            image=cv2.resize(image,target_size)

            image_bgr=cv2.cvtColor(image,cv2.COLOR_RGB2BGR)
            cv2.imwrite(output_img_path,image_bgr)
            count+=1
        print(f"{count} preprocessed images saved for label : {label}")
    print("Preprocessing completed and saved")        
