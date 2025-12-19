import json
import os
from typing import List
from tools.eligibility import check_eligibility
from tools import mock_api
from llm_client import LLMClient
SCHEMES_PATH = os.path.join(os.path.dirname(__file__), "schemes", "data_te.json")

class Agent:
    def __init__(self, memory=None, llm_client=None):
        self.memory = memory
        # If a client is passed, use it; otherwise try to create a default LLMClient
        self.llm = llm_client or LLMClient()
        self.schemes = self._load_schemes()

    def _load_schemes(self):
        try:
            with open(SCHEMES_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []

    def simple_retrieve(self, query: str) -> List[dict]:
        # naive keyword match over title and summary
        q = query.lower()
        results = []
        for s in self.schemes:
            if q in s.get("title", "").lower() or q in s.get("summary", "").lower():
                results.append(s)
        # fallback: return all if nothing matches
        return results or self.schemes

    def plan(self, user_text: str, user_profile: dict) -> dict:
        # Planner in Telugu: ask clarifying Qs if missing key fields
        needed = []
        if "age" not in user_profile:
            needed.append("దయచేసి మీ వయస్సు చెప్పండి")
        if "income" not in user_profile:
            needed.append("మీ నెలవారీ ఆదాయం ఎంత ఉంది చెప్పండి")
        if needed:
            # try to use LLM to rephrase or expand clarifying questions in Telugu
            if self.llm:
                prompt = (
                    "మీరు అడిగిన ప్రశ్న ఈ కిందిది:\n" + user_text + "\n\n"
                    + "ప్రొఫైల్ లో ఈ ఫీల్డ్స్ లేవు: " + ",".join(needed)
                    + "\nతెలుగు లో క్లారిఫై చేయడానికి 2 పద్యాల (స్పష్టమైన) ప్రశ్నలను ఇవ్వండి."
                )
                gen = self.llm.generate(prompt, max_tokens=150)
                if gen:
                    # split by lines and return as questions if possible
                    qs = [l.strip() for l in gen.splitlines() if l.strip()][:2]
                    if qs:
                        return {"action": "clarify", "questions": qs}

            return {"action": "clarify", "questions": needed}

        # Otherwise search suitable schemes
        results = self.simple_retrieve(user_text)
        scored = []
        for s in results:
            ok, reasons = check_eligibility(user_profile, s)
            scored.append({"scheme": s, "eligible": ok, "reasons": reasons})

        # If LLM available, ask it to summarize recommendations in Telugu
        if self.llm:
            # create a compact prompt with top schemes and eligibility
            items = []
            for r in scored:
                items.append(f"{r['scheme']['id']}: {r['scheme']['title']} - eligible:{r['eligible']}")
            prompt = (
                "మీరు పుస్తకం వ్యవస్థలో ఈ పథకాలను పొందారు:\n" + "\n".join(items)
                + "\nచదవండి మరియు తెలుగు లో 2 వాక్యాలలో సరైన పథకాన్ని సూచించండి మరియు ఎందుకు అన్నదాన్ని చెప్పండి."
            )
            gen = self.llm.generate(prompt, max_tokens=200)
            return {"action": "recommend", "results": scored, "llm_summary": gen}

        return {"action": "recommend", "results": scored}

    def execute(self, plan: dict, user_profile: dict) -> dict:
        if plan.get("action") == "clarify":
            return {"type": "clarify", "questions": plan.get("questions", [])}

        if plan.get("action") == "recommend":
            recommendations = [r for r in plan.get("results", []) if r.get("eligible")]
            if not recommendations:
                return {"type":"no_match", "details": plan.get("results", [])}
            # pick first and attempt submission via mock_api
            chosen = recommendations[0]
            app_data = {"scheme_id": chosen["scheme"]["id"], "profile": user_profile}
            resp = mock_api.submit_application(app_data)
            return {"type":"applied", "response": resp, "scheme": chosen["scheme"]}

    def evaluate(self, exec_result: dict) -> dict:
        # simple evaluation: check success flag
        if exec_result.get("type") == "applied":
            if exec_result["response"].get("success"):
                return {"status":"success", "message":"అరుచి: దరఖాస్తు సమర్పించబడింది"}
            else:
                return {"status":"failure", "message":"సమర్పణలో లోపం, దయచేసి తిరిగి ప్రయత్నించండి"}
        if exec_result.get("type") == "no_match":
            return {"status":"nomatch", "message":"మీ అర్హతలకు సరిపడే పథకాలు అందుబాటులో లేవు"}
        if exec_result.get("type") == "clarify":
            return {"status":"clarify", "questions": exec_result.get("questions", [])}

        return {"status":"unknown", "message":"ప్రక్రియను పూర్తి చేయలేకపోయాం"}
