from airflow.decorators import task
@task
def preprocess_and_save_images(input_dir: str, output_dir: str, target_size=(224, 224), blur_threshold: float = 50.0):
    import cv2
    import os
    import sys
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
    from src.preprocessing.blur_detect import is_blurr
    expected_labels = ['rock', 'paper', 'scissors']

    if not os.path.exists(input_dir):
        raise FileNotFoundError(f"Input directory not found: {input_dir}")

    os.makedirs(output_dir, exist_ok=True)

    for label in expected_labels:
        input_path = os.path.join(input_dir, label)
        output_path = os.path.join(output_dir, label)

        if not os.path.exists(input_path):
            print(f"[Skip] Missing folder: {label}")
            continue

        os.makedirs(output_path, exist_ok=True)

        images = [img for img in os.listdir(input_path) if img.lower().endswith(('.png', '.jpg', '.jpeg'))]
        saved_count = 0
        skipped_blur = 0

        for img_name in images:
            img_path = os.path.join(input_path, img_name)
            output_img_path = os.path.join(output_path, img_name)

            image = cv2.imread(img_path)
            if image is None:
                print(f"[Skip] Unreadable image: {img_name}")
                continue

            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

            # if is_blurr(image, threshold=blur_threshold):
            #     print(f"[Skip] Blurry image detected: {img_name}")
            #     skipped_blur += 1
            #     continue

            image = cv2.resize(image, target_size)
            image_bgr = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
            cv2.imwrite(output_img_path, image_bgr)
            saved_count += 1

        print(f"[{label.upper()}] Saved: {saved_count}, Blurry Skipped: {skipped_blur}")

    print("Image preprocessing completed successfully.")
