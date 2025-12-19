import os
import json
import time
from typing import Optional

# Load .env automatically if present
try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    # python-dotenv not installed; environment variables must be set externally
    pass

class LLMClient:
    def __init__(self, model: str = "google/flan-t5-small"):
        self.model = model
        self.hf_token = os.environ.get("HF_API_TOKEN") or os.environ.get("HUGGINGFACE_API_TOKEN")
        self._local_pipeline = None
        # Always define _transformers attribute; if HF token is not set, we may try to load transformers
        self._transformers = None
        if not self.hf_token:
            # try to load local transformers pipeline if available
            try:
                from transformers import pipeline, AutoTokenizer, AutoModelForSeq2SeqLM
                # lazy load on first generate to avoid long imports at startup
                self._transformers = {
                    "pipeline": pipeline,
                    "AutoTokenizer": AutoTokenizer,
                    "AutoModelForSeq2SeqLM": AutoModelForSeq2SeqLM,
                }
            except Exception:
                self._transformers = None

    def _init_local(self):
        if self._local_pipeline is None and self._transformers:
            pipeline = self._transformers["pipeline"]
            try:
                # load model (this will download weights)
                self._local_pipeline = pipeline("text2text-generation", model=self.model)
            except Exception:
                self._local_pipeline = None

    def generate(self, prompt: str, max_tokens: int = 256, temperature: float = 0.2) -> Optional[str]:
        """Generate text from the configured LLM. Returns None if no provider available."""
        # Hugging Face Inference API path
        if self.hf_token:
            # Prefer the newer InferenceClient if available
            try:
                try:
                    from huggingface_hub import InferenceClient
                except Exception:
                    # older versions may expose client elsewhere
                    from huggingface_hub.inference import InferenceClient
                try:
                    client = InferenceClient(api_key=self.hf_token)
                except TypeError:
                    # some versions expect token kwarg name 'token' or 'api_key'
                    try:
                        client = InferenceClient(token=self.hf_token)
                    except Exception:
                        client = InferenceClient(self.hf_token)

                # Try text-generation endpoint if available
                if hasattr(client, "text_generation"):
                    try:
                        out = client.text_generation(model=self.model, inputs=prompt, max_new_tokens=max_tokens, temperature=temperature)
                        # client.text_generation may return dict/list/str
                        if isinstance(out, str):
                            return out
                        if isinstance(out, list) and len(out) > 0 and isinstance(out[0], dict):
                            return out[0].get("generated_text") or out[0].get("text")
                        if isinstance(out, dict):
                            return out.get("generated_text") or out.get("text") or json.dumps(out)
                    except Exception:
                        pass

                # Generic client.invoke or __call__ fallback
                try:
                    if hasattr(client, "invoke"):
                        out = client.invoke(self.model, inputs=prompt, parameters={"max_new_tokens": max_tokens, "temperature": temperature})
                    else:
                        out = client(inputs=prompt, model=self.model, parameters={"max_new_tokens": max_tokens, "temperature": temperature})
                    if isinstance(out, str):
                        return out
                    if isinstance(out, list) and len(out) > 0 and isinstance(out[0], dict):
                        return out[0].get("generated_text") or out[0].get("text")
                    if isinstance(out, dict):
                        return out.get("generated_text") or out.get("text") or json.dumps(out)
                except Exception:
                    pass

            except Exception:
                # Fallback to the legacy InferenceApi path if InferenceClient isn't available
                try:
                    try:
                        from huggingface_hub import InferenceApi
                    except Exception:
                        from huggingface_hub.inference_api import InferenceApi
                    api = InferenceApi(repo_id=self.model, token=self.hf_token)
                    out = api(inputs=prompt, params={"max_new_tokens": max_tokens, "temperature": temperature})
                    if isinstance(out, str):
                        return out
                    if isinstance(out, list) and len(out) > 0 and isinstance(out[0], dict):
                        return out[0].get("generated_text")
                    if isinstance(out, dict):
                        return out.get("generated_text") or out.get("text") or json.dumps(out)
                except Exception:
                    return None
        # Local transformers path
        if self._transformers:
            try:
                self._init_local()
                if self._local_pipeline:
                    out = self._local_pipeline(prompt, max_length=max_tokens)
                    if isinstance(out, list) and len(out) > 0 and isinstance(out[0], dict):
                        return out[0].get("generated_text")
            except Exception:
                return None

        return None


if __name__ == "__main__":
    cli = LLMClient()
    print("LLM initialized. HF token:" , bool(cli.hf_token))
    res = cli.generate("నమస్తే. మీరు ఎలా ఉన్నారు?", max_tokens=50)
    print(res)
