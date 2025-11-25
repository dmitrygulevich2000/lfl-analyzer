import pandas as pd

from loader import MatchesLoader, ProtocolLoader
from render import Renderer
from .Report import Report
from Util import *


class TurnoutReport(Report):
    def __init__(self, club, tournaments, build_id):
        self.club = club
        self.tournaments = tournaments
        self.build_id = build_id

    def build(self):
        total_matches = 0
        total_turnout = 0
        for tournament in self.tournaments:
            matches_json = MatchesLoader(self.club, tournament=tournament).load_json()
            total_matches += len(matches_json)

            for match in matches_json:
                protocol = ProtocolLoader(self.build_id, match["match_id"]).load_json()
                turnout = sum(1 for p in protocol["lineup"] if p["club_id"] == self.club)
                if turnout > 15:
                    # skip match with possibly wrong protocol
                    total_matches -= 1
                    continue

                total_turnout += turnout

        self.avg_turnout = total_turnout / total_matches

    def render(self, renderer: Renderer, level=1):
        renderer.text(f"Количество замен: {self.avg_turnout - 8:.2f} человека")
