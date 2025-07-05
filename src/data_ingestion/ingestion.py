import os
import shutil
def validate_and_ingest_image(src_dir,dest_dir):
    expected_labels = ['rock', 'paper', 'scissors']
    if not  os.path.exists(src_dir):
        raise FileNotFoundError(f"Source directory not found: {src_dir}")
    os.makedirs(dest_dir,exist_ok=True)
    for label in expected_labels:
        src_label_path=os.path.join(src_dir,label)
        dest_label_path=os.path.join(dest_dir,label)
        if not os.path.exists(src_label_path):
            raise FileNotFoundError(f"Missing label Folder: {label}")

        os.makedirs(dest_label_path,exist_ok=True)

        files=[f for f in os.listdir(src_label_path) if f.lower().endswith(('.png','.jpg','.jpeg'))]

        for f in files:
            src_path=os.path.join(src_label_path,f)
            dest_path=os.path.join(dest_label_path,f)
            shutil.copy(src_path,dest_path)
        print(f"Copied {len(files)} images to '{label}' in raw data.")
    print(f"Data ingestion Done.")

