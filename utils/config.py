import json

class Config(dict):
    PATH = "config.json"
    def __init__(self):
        with open(Config.PATH, 'r', encoding="utf8") as f:
            self._jObject = json.load(f)
        super().__init__(self._jObject)
