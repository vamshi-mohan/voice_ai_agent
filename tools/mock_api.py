import time
import random

def submit_application(app_data: dict) -> dict:
    # Simulate network latency and possible failure
    time.sleep(1)
    if random.random() < 0.05:
        return {"success": False, "error": "server_error"}
    app_id = f"APP-{int(time.time())}-{random.randint(100,999)}"
    return {"success": True, "application_id": app_id}
