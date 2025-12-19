import os
from huggingface_hub import HfApi

def probe(token, models):
    api = HfApi()
    print("Running whoami() to validate token and scopes...")
    try:
        info = api.whoami(token=token)
        print("whoami:", info)
    except Exception as e:
        print("whoami error:", e)

    for m in models:
        print(f"\n--- Model: {m} ---")
        try:
            info = api.model_info(m, token=token)
            # print some key fields
            print('model_id:', info.modelId if hasattr(info, 'modelId') else getattr(info, 'id', None))
            try:
                # some ModelInfo objects have 'private' attribute
                print('private:', info.private)
            except Exception:
                pass
            try:
                # pipeline tag(s)
                print('pipeline_tag:', info.pipeline_tag)
            except Exception:
                pass
            # print last modified and siblings count if present
            try:
                print('lastModified:', info.lastModified)
            except Exception:
                pass
        except Exception as e:
            print('model_info error:', e)

if __name__ == '__main__':
    token = os.environ.get('HF_API_TOKEN')
    if not token:
        print('No HF_API_TOKEN set in environment')
    else:
        models = [
            'google/flan-t5-small',
            'bigscience/bloomz-560m',
            'bigscience/bloomz-1b1',
            'facebook/bart-large-cnn',
            'gpt2'
        ]
        probe(token, models)
