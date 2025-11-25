from .LflDataLoader import LflDataLoader


class PlayerMatchesLoader(LflDataLoader):
    def __init__(self, player, limit=40):
        super().__init__()
        self.player = player
        self.limit = limit

    def _get_cache_key(self):
        return f"player_matches_{self.player}.json"

    def _load_from_api(self):
        url = f"{LflDataLoader.BASE_LFL_API_URL}/persons/{self.player}/matches"
        params = {"per_page": self.limit}

        res = LflDataLoader.query_url(url, params)
        assert (res["length"] == len(res["data"]))
        return res["data"]
