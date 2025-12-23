from datetime import date

from .Report import Report, SequenceReport
from loader import TournamentLoader
from render import Renderer
from Util import *


class HeaderReport(Report):
    def __init__(self, line):
        self.line = line

    def build(self):
        pass

    def render(self, renderer: Renderer, level=1):
        renderer.heading(self.line, level)


class NameDateHeaderReport(Report):
    def __init__(self, name, club):
        self.name = name
        self.club = club

    def build(self):
        pass

    def render(self, renderer: Renderer, level=1):
        today = date.today()
        name_href = renderer.get_href(self.name, build_club_url(self.club))
        renderer.heading(f"{name_href} {today.strftime(DISPLAY_DATE_FORMAT)}", level)


class SeasonsHeaderReport(Report):
    def __init__(self, seasons: list[int]):
        self.seasons = seasons

    def build(self):
        self.season_years = sorted([year_by_season_id(s) for s in self.seasons])

    def render(self, renderer: Renderer, level=1):
        header = "Сезон {}".format(self.season_years[0])
        if len(self.seasons) != 1:
            header = "Сезоны {}".format(",".join(self.seasons))
        renderer.heading(header, level)


class TournamentsHeaderReport(Report):
    def __init__(self, tournaments: list[int]):
        self.touranments = tournaments

    def build(self):
        self.tournament_names = [TournamentLoader(t).load_json()["data"]["name"] for t in self.touranments]

    def render(self, renderer: Renderer, level=1):
        header = self.tournament_names[0]
        if len(self.tournament_names) != 1:
            header = ",".join(self.tournament_names)
        renderer.heading(header, level)
