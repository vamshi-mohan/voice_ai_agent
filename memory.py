import json
import os

class Memory:
    def __init__(self, path=None):
        self.path = path or os.path.join(os.path.dirname(__file__), "memory.json")
        self._data = {"conversations": []}
        self._load()

    def _load(self):
        try:
            with open(self.path, "r", encoding="utf-8") as f:
                self._data = json.load(f)
        except Exception:
            self._data = {"conversations": []}

    def add_turn(self, turn: dict):
        self._data.setdefault("conversations", []).append(turn)
        self._save()

    def _save(self):
        try:
            with open(self.path, "w", encoding="utf-8") as f:
                json.dump(self._data, f, ensure_ascii=False, indent=2)
        except Exception:
            pass

    def last_user(self):
        for t in reversed(self._data.get("conversations", [])):
            if t.get("role") == "user":
                return t
        return None
