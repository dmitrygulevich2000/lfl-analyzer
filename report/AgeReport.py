from datetime import date, datetime

from loader import SquadsLoader
from render import Renderer
from .Report import Report
from Util import *
from .common.Common import *


class AgeReportBase(Report):
    BIRTHDAY_DATE_FORMAT = "%Y-%m-%d"

    def __init__(self, club, build_id):
        self.club = club
        self.build_id = build_id

    def build(self):
        pass

    def render(self, renderer: Renderer, level=1):
        renderer.text(f"Средний возраст: {self.avg:.2f} года")
        renderer.text(f"Медианный возраст: {self.median:.2f} года")

    def _calc_for_matches(self, matches_json):
        today = date.today()

        ages = []
        total_turnout = 0
        for match in matches_json:
            if is_techical_defeat(match):
                continue
            protocol = ProtocolLoader(self.build_id, match["match_id"]).load_json()
            club_lineup = [p for p in protocol["lineup"] if p["club_id"] == self.club]

            turnout = len(club_lineup)
            if turnout > 15:
                # skip match with possibly wrong protocol
                continue

            total_turnout += turnout
            ages += [AgeReportBase.__calculate_age(p["birthday"], today) for p in club_lineup]

        return total_turnout, ages

    def _finalize(self, total_turnout, ages_array):
        ages_array.sort()
        self.avg = sum(ages_array) / total_turnout
        self.median = ages_array[len(ages_array) // 2]

    # deprecated in favor of match-by-match calculation
    def _load_games_ages_by_tournament(self, tournament, at_date):
        raw_json = SquadsLoader(self.club, tournament).load_json()
        games = [player["stats"][0]["games"]
                 for player in raw_json["data"]
                 if len(player["stats"]) > 0 and player["stats"][0] is not None]
        ages = [AgeReportBase.__calculate_age(player["birthday"], at_date)
                for player in raw_json["data"]
                if len(player["stats"]) > 0 and player["stats"][0] is not None]

        return games, ages

    def __calculate_age(birthday_str, at_date):
        birthday_date = datetime.strptime(birthday_str, AgeReportBase.BIRTHDAY_DATE_FORMAT).date()
        age_timedelta = at_date - birthday_date
        return age_timedelta.days / 365.25


class SeasonsAgeReport(AgeReportBase):
    def __init__(self, club, seasons, build_id):
        super().__init__(club, build_id)
        self.seasons = seasons

    def build(self):
        # return self._build_legacy()

        total_turnout = 0
        ages_array = []
        for season in self.seasons:
            matches_json = MatchesLoader(self.club, season=season).load_json()
            turnout, ages = self._calc_for_matches(matches_json)
            total_turnout += turnout
            ages_array += ages

        self._finalize(total_turnout, ages_array)

    # deprecated in favor of match-by-match calculation
    def _build_legacy(self):
        today = date.today()
        ages_array = []
        total_games = 0
        total_age = 0
        for tournament in [29582, 28320, 29486]:
            games, ages = self._load_games_ages_by_tournament(tournament, today)
            total_games += sum(games)
            total_age += sum([g * a for g, a in zip(games, ages)])
            ages_array += sum([g * [a] for g, a in zip(games, ages)], [])

        ages_array.sort()
        self.avg = total_age / total_games
        self.median = ages_array[len(ages_array) // 2]


class LastMatchesAgeReport(AgeReportBase):
    def __init__(self, club, days, build_id):
        super().__init__(club, build_id)
        self.days = days

    def build(self):
        matches_json = load_last_matches(self.club, self.days)
        total_turnout, ages_array = self._calc_for_matches(matches_json)

        self._finalize(total_turnout, ages_array)
