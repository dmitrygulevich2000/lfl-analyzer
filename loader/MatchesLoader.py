from .LflDataLoader import LflDataLoader


class MatchesLoader(LflDataLoader):
    def __init__(self, club, *, tournament="", season="", limit=50):
        super().__init__()
        assert (tournament == "" or int(tournament) > 0)

        self.club = club
        self.tournament = tournament
        self.season = season
        self.limit = limit

    def _get_cache_key(self):
        return f"matches_{self.club}_{self.tournament}_{self.season}.json"

    def _load_from_api(self):
        url = f"{LflDataLoader.BASE_LFL_API_URL}/matches"
        params = {
            "per_page": self.limit,
            "club": self.club,
            "tournament": self.tournament,
            "season": self.season,
            "currentDate": "true",
            "sort": "time"
        }

        res = LflDataLoader.query_url(url, params)
        assert (res["length"] == len(res["data"]))
        assert ((not self.season and not self.tournament) or res["length"] < self.limit)
        return list(filter(lambda m: m["home_points"] is not None, res["data"]))
