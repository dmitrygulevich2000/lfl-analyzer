import os
import json


class JSONFileCache:
    def __init__(self, dir):
        os.makedirs(dir, exist_ok=True)
        self.dir = dir

    def get_json(self, key):
        filepath = os.path.join(self.dir, key)
        try:
            with open(filepath) as f:
                value = json.load(f)
        except FileNotFoundError:
            return None
        return value

    def set_json(self, key, value):
        filepath = os.path.join(self.dir, key)
        with open(filepath, "w") as f:
            json.dump(value, f)
