from airflow.decorators import task

@task
def extraction_image(db_name: str, table_name: str, folder_extracted: str) -> dict:
    import pandas as pd
    from sqlalchemy import create_engine, text
    import os
    import io
    from PIL import Image

    try:
        DATABASE_URL = f"postgresql://postgres:admin@postgres:5432/{db_name}"
        engine = create_engine(DATABASE_URL)
        query = f"SELECT * FROM {table_name};"
        df = pd.read_sql(query, con=engine)

        if df.empty:
            return {"rock": 0, "paper": 0, "scissors": 0}

        label_counts = {"rock": 0, "paper": 0, "scissors": 0}

        for label in label_counts.keys():
            os.makedirs(os.path.join(folder_extracted, label), exist_ok=True)

        for idx, row in df.iterrows():
            label = row['label'].lower().strip()
            if label not in label_counts:
                continue

            image_bytes = row['image']
            img = Image.open(io.BytesIO(image_bytes)).convert('RGB')

            image_path = os.path.join(folder_extracted, label, f"{label}_{row['id']}.jpg")
            img.save(image_path)
            label_counts[label] += 1
        with engine.begin() as conn:
            conn.execute(text(f"TRUNCATE TABLE {table_name};"))

        return label_counts

    except Exception as e:
        raise RuntimeError(f"Image extraction failed: {e}")
