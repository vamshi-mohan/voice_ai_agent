import os
import requests

def debug_model(model="google/flan-t5-small", prompt="తెలుగు లో ఒక చిన్న పరిచయం చెప్పండి."):
    token = os.environ.get("HF_API_TOKEN")
    if not token:
        print("No HF_API_TOKEN set")
        return
    url = f"https://api-inference.huggingface.co/models/{model}"
    headers = {"Authorization": f"Bearer {token}"}
    payload = {"inputs": prompt, "parameters": {"max_new_tokens": 80}}
    try:
        r = requests.post(url, headers=headers, json=payload, timeout=60)
        print("Status:", r.status_code)
        try:
            print(r.json())
        except Exception:
            print(r.text[:1000])
    except Exception as e:
        print("Request failed:", e)

if __name__ == '__main__':
    debug_model()
