import os
import argparse
from stt import record_audio, transcribe
from tts import speak
from agent import Agent
from memory import Memory

def main():
    mem = Memory()
    agent = Agent(memory=mem)

    speak("నమస్తే! మీరు ఏ పథకం కొరకు దరఖాస్తు చేయాలని అనుకుంటున్నారు? మిమ్మల్ని ఎలా సహాయం చేయగలను?")

    while True:
        # record
        try:
            tmp = os.path.join(os.path.dirname(__file__), "tmp_input.wav")
            record_audio(tmp, duration=6)
            res = transcribe(tmp, language="te")
            user_text = res.get("text", "").strip()
        except Exception:
            # fallback to typed input
            user_text = input("స్పీచ్ రికార్డు విఫలం. టెక్స్ట్ ఎంటర్ చేయండి (తెలుగులో): ")

        mem.add_turn({"role":"user","text":user_text})

        # simple user profile gather from memory or ask
        last = mem.last_user() or {}
        user_profile = {}

        # run planner
        plan = agent.plan(user_text, user_profile)
        exec_result = agent.execute(plan, user_profile)
        eval_result = agent.evaluate(exec_result)

        if eval_result.get("status") == "clarify":
            for q in eval_result.get("questions", []):
                speak(q)
                ans = input(f"{q} (type in Telugu): ")
                # naive parse: store numeric if possible
                try:
                    if "వయస్సు" in q or "వయస్సు" in q:
                        user_profile["age"] = int(ans)
                    elif "ఆదాయం" in q:
                        user_profile["income"] = int(ans)
                    else:
                        pass
                except Exception:
                    pass
                mem.add_turn({"role":"user","text":ans})
            # re-plan after clarifications
            plan = agent.plan(user_text, user_profile)
            exec_result = agent.execute(plan, user_profile)
            eval_result = agent.evaluate(exec_result)

        # respond in Telugu
        if eval_result.get("status") == "success":
            speak("మీ దరఖాస్తు విజయవంతంగా సమర్పించబడింది. ధన్యవాదాలు.")
        elif eval_result.get("status") == "failure":
            speak("సమర్పించడంలో ఒక సమస్య వచ్చింది. దయచేసి మళ్ళీ ప్రయత్నించండి.")
        elif eval_result.get("status") == "nomatch":
            speak("మీకు సరిపడే పథకాలు కనిపించలేదు. మీరు మరిన్ని వివరాలు ఇవ్వగలరా?")
        else:
            speak(eval_result.get("message", "సరైన సమాచారం అందలేదు"))

        cont = input("మరొకటి చేయాలా? (y/n): ")
        if cont.strip().lower() not in ("y", "yes", "ఉందు"):
            break

if __name__ == "__main__":
    main()
