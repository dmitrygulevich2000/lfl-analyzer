from datetime import date, datetime

from loader import SquadsLoader
from render import Renderer
from .Report import Report
from Util import *


class AgeReport(Report):
    BIRTHDAY_DATE_FORMAT = "%Y-%m-%d"

    def __init__(self, club, tournaments):
        self.club = club
        self.tournaments = tournaments

    def build(self):
        today = date.today()
        ages_array = []
        total_games = 0
        total_age = 0
        for tournament in self.tournaments:
            games, ages = self.__load_games_ages(self.club, tournament, today)
            total_games += sum(games)
            total_age += sum([g * a for g, a in zip(games, ages)])
            ages_array += sum([g * [a] for g, a in zip(games, ages)], [])

        ages_array.sort()

        self.avg = total_age / total_games
        self.median = ages_array[len(ages_array) // 2]

    def render(self, renderer: Renderer, level=1):
        renderer.text(f"Средний возраст: {self.avg:.2f} года")
        renderer.text(f"Медианный возраст: {self.median:.2f} года")

    def __load_games_ages(self, club, tournament, at_date):
        raw_json = SquadsLoader(club, tournament).load_json()
        games = [player["stats"][0]["games"]
                 for player in raw_json["data"]
                 if len(player["stats"]) > 0 and player["stats"][0] is not None]
        ages = [AgeReport.__calculate_age(player["birthday"], at_date)
                for player in raw_json["data"]
                if len(player["stats"]) > 0 and player["stats"][0] is not None]

        return games, ages

    def __calculate_age(birthday_str, at_date):
        birthday_date = datetime.strptime(birthday_str, AgeReport.BIRTHDAY_DATE_FORMAT).date()
        age_timedelta = at_date - birthday_date
        return age_timedelta.days / 365.25
