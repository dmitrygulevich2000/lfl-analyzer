from .LflDataLoader import LflDataLoader


class MatchesLoader(LflDataLoader):
    def __init__(self, club, *, tournament="", season=""):
        super().__init__()
        assert (tournament == "" or int(tournament) > 0)

        self.club = club
        self.tournament = tournament
        self.season = season

    def _get_cache_key(self):
        return f"matches_{self.club}_{self.tournament}_{self.season}.json"

    def _load_from_api(self):
        url = f"{LflDataLoader.BASE_LFL_API_URL}/matches"
        params = {
            "club": self.club,
            "tournament": self.tournament,
            "season": self.season,
            "per_page": 50,
            "currentDate": "true",
            "sort": "time"
        }

        res = LflDataLoader.query_url(url, params)
        assert (res["length"] == len(res["data"]))
        return list(filter(lambda m: m["home_points"] is not None, res["data"]))
