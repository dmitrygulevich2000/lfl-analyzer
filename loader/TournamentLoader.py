from .LflDataLoader import LflDataLoader


class TournamentLoader(LflDataLoader):
    def __init__(self, tournament):
        super().__init__()
        self.tournament = tournament

    def _get_cache_key(self):
        return f"tournaments_{self.tournament}.json"

    def _load_from_api(self):
        url = f"{LflDataLoader.BASE_LFL_API_URL}/tournaments/{self.tournament}"

        return LflDataLoader.query_url(url, {})


class RatingLoader(LflDataLoader):
    def __init__(self, tournament):
        super().__init__()
        self.tournament = tournament

    def _get_cache_key(self):
        return f"rating_{self.tournament}.json"

    def _load_from_api(self):
        url = f"{LflDataLoader.BASE_LFL_API_URL}/tournaments/{self.tournament}/rating"
        params = {"per_page": 30}

        return LflDataLoader.query_url(url, params)
