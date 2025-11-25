from .JSONFileCache import *
import requests
from urllib.parse import urlencode


class LflDataLoader:
    BASE_LFL_API_URL = "https://api.lfl.ru/api"
    BASE_PAGE_LFL_URL = "https://page.lfl.ru/_next/data"

    def __init__(self):
        self.cache = JSONFileCache("/tmp/lfl")

    def load_json(self, use_cache=True):
        if not use_cache:
            return self._load_from_api()

        key = self._get_cache_key()
        data = self.cache.get_json(key)

        if data is None:
            data = self._load_from_api()

        self.cache.set_json(key, data)
        return data

    def _get_cache_key(self):
        pass

    def _load_from_api(self):
        pass

    def query_url(url, params):
        resp = requests.get(url, params)
        # print(url, params)
        if (resp.status_code != 200):
            raise RuntimeError(
                f"GET {url}?{urlencode(params)} returned {resp.status_code} code with body:\n\t{resp.text}")
        return resp.json()

    def page_lfl_url(build_id):
        return f"{LflDataLoader.BASE_PAGE_LFL_URL}/{build_id}/ru"
