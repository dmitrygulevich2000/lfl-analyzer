from .LflDataLoader import LflDataLoader


class SquadsLoader(LflDataLoader):
    def __init__(self, club, tournament):
        super().__init__()
        self.club = club
        self.tournament = tournament

    def _get_cache_key(self):
        return f"squads_{self.club}_{self.tournament}.json"

    def _load_from_api(self):
        url = f"{LflDataLoader.BASE_LFL_API_URL}/clubs/{self.club}/squads"

        params = {"per_page": 100}
        div_or_tourn = f"{self.tournament}"
        if div_or_tourn.startswith("d"):
            params["division"] = div_or_tourn.lstrip("d")
        else:
            params["tournament"] = div_or_tourn

        return LflDataLoader.query_url(url, params)
