import os
from dotenv import load_dotenv
load_dotenv()
token = os.environ.get('HF_API_TOKEN')
print('HF token present:', bool(token))
import huggingface_hub as hf
print('huggingface_hub version:', hf.__version__)
try:
    # Try multiple import paths for InferenceClient
    try:
        from huggingface_hub import InferenceClient
    except Exception:
        try:
            from huggingface_hub.inference import InferenceClient
        except Exception:
            InferenceClient = None

    print('InferenceClient available:', InferenceClient is not None)
    if InferenceClient is None:
        raise ImportError('No InferenceClient available in this huggingface_hub version')

    client = None
    try:
        client = InferenceClient(api_key=token)
    except Exception as e:
        try:
            client = InferenceClient(token)
        except Exception as e2:
            print('Failed to construct InferenceClient:', e, e2)

    if client is None:
        raise RuntimeError('Could not construct InferenceClient')

    print('Client methods:', [m for m in dir(client) if not m.startswith('_')])

    models = [
        'bigscience/bloomz-560m',
        'bigscience/bloomz-1b1',
        'openai-community/gpt2',
        'gpt2',
        'google/flan-t5-small',
        'google/flan-t5-base',
        'EleutherAI/gpt-neo-2.7B',
        'facebook/opt-1.3b',
    ]
    prompt = 'తెలుగు లో ఒక చిన్న పరిచయం చెప్పండి.'

    for model in models:
        print('\n=== MODEL:', model)
        try:
            if hasattr(client, 'text_generation'):
                try:
                    out = client.text_generation(prompt=prompt, model=model, max_new_tokens=80, temperature=0.7)
                    print('text_generation success, type:', type(out))
                    print(out)
                    continue
                except Exception as e:
                    print('text_generation error:', e)

            # generic call fallback
            try:
                out = client(inputs=prompt, model=model, parameters={'max_new_tokens':80, 'temperature':0.7})
                print('generic call success, type:', type(out))
                print(out)
            except Exception as e:
                print('generic call error:', e)
        except Exception as e:
            print('unexpected error for model', model, e)

except Exception as e:
    print('Error inspecting InferenceClient:', e)
