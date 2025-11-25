from .LflDataLoader import LflDataLoader


class ProtocolLoader(LflDataLoader):
    def __init__(self, build_id, match):
        super().__init__()
        self.match = match
        self.build_id = build_id

    def _get_cache_key(self):
        return f"protocol_{self.match}.json"

    def _load_from_api(self):
        url = f"{LflDataLoader.page_lfl_url(self.build_id)}/protocols/{self.match}.json"
        params = {"id": self.match}

        return LflDataLoader.query_url(url, params)["pageProps"]
