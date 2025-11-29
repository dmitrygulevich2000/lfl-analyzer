from .LflDataLoader import LflDataLoader


class PlayerMatchesLoader(LflDataLoader):
    def __init__(self, player, tournament="", season="", limit=80):
        super().__init__()
        self.player = player
        self.tournament = tournament
        self.season = season
        self.limit = limit

    def _get_cache_key(self):
        return f"player_matches_{self.player}_{self.tournament}_{self.season}.json"

    def _load_from_api(self):
        url = f"{LflDataLoader.BASE_LFL_API_URL}/persons/{self.player}/matches"
        params = {
            "per_page": self.limit,
            "tournament": self.tournament,
            "season": self.season,
        }

        res = LflDataLoader.query_url(url, params)
        assert (res["length"] == len(res["data"]))
        assert ((not self.season and not self.tournament) or res["length"] < self.limit)
        return res["data"]
