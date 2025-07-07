import json
import os
COUNTER_PATH = "utils/prediction_counter.json"
THRESHOLD = 1 
def increment_and_check():
    if not os.path.exists(COUNTER_PATH):
        with open(COUNTER_PATH, "w") as f:
            json.dump({"count": 1}, f)
        return False
    with open(COUNTER_PATH, "r") as f:
        data = json.load(f)
    data["count"] += 1
    if data["count"] >= THRESHOLD:
        data["count"] = 0  
        triggered = True
    else:
        triggered = False
    with open(COUNTER_PATH, "w") as f:
        json.dump(data, f)

    return triggered
