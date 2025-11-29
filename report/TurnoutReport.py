import pandas as pd

from loader import MatchesLoader, ProtocolLoader
from render import Renderer
from .Report import Report
from Util import *
from .common.Common import *


class TurnoutReportBase(Report):
    def __init__(self, club, build_id):
        self.club = club
        self.build_id = build_id

    def build(self):
        pass

    def render(self, renderer: Renderer, level=1):
        renderer.text(f"Количество замен: {self.avg_turnout - 8:.2f} человека")

    def _calc_for_matches(self, matches_json):
        total_matches = 0
        total_turnout = 0
        for match in matches_json:
            if is_techical_defeat(match):
                continue
            protocol = ProtocolLoader(self.build_id, match["match_id"]).load_json()
            turnout = sum(1 for p in protocol["lineup"] if p["club_id"] == self.club)
            if turnout > 15:
                # skip match with possibly wrong protocol
                continue

            total_turnout += turnout
            total_matches += 1

        return total_turnout, total_matches


class SeasonsTurnoutReport(TurnoutReportBase):
    def __init__(self, club, seasons, build_id):
        super().__init__(club, build_id)
        self.seasons = seasons

    def build(self):
        total_turnout = 0
        total_matches = 0
        for season in self.seasons:
            matches_json = MatchesLoader(self.club, season=season).load_json()
            turnout, matches = self._calc_for_matches(matches_json)
            total_turnout += turnout
            total_matches += matches

        self.avg_turnout = total_turnout / total_matches


class LastMatchesTurnoutReport(TurnoutReportBase):
    def __init__(self, club, days, build_id):
        super().__init__(club, build_id)
        self.days = days

    def build(self):
        matches_json = load_last_matches(self.club, self.days)
        total_turnout, total_matches = self._calc_for_matches(matches_json)

        self.avg_turnout = total_turnout / total_matches
