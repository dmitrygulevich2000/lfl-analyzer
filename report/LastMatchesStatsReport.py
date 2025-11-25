import pandas as pd
from datetime import datetime, timedelta

from loader import MatchesLoader, ProtocolLoader
from render import Renderer
from .Report import Report
from Util import *
from .common.Common import *


class LastMatchesStatsReport(Report):
    def __init__(self, club, days, build_id):
        self.club = club
        self.days = days
        self.build_id = build_id

    def build(self):
        date_threshold = datetime.today().astimezone(TZ) - timedelta(days=self.days)
        matches_json = MatchesLoader(self.club).load_json()

        last_match_ids = [match["match_id"] for match in matches_json if
                          datetime.fromisoformat(match["match_date_time"]) > date_threshold]

        stats = load_stats(self.club, last_match_ids, self.build_id)
        add_points_stats(stats.player_df, total_games=stats.total_games, total_points=stats.total_points)

        self.stats = stats

    def render(self, renderer: Renderer, level=1):
        renderer.heading("Статистика игроков", level)

        display_df = self.stats.player_df.reset_index(names="person_id")
        display_df["player_title"] = display_df["person_id"].apply(lambda pnid: (
            pr := self.stats.player_info[pnid],
            renderer.get_href(pr.name, build_player_url(pr.person_id, pr.player_id))
        )[-1])
        display_df["amplua"] = display_df["person_id"].apply(lambda pnid: self.stats.player_info[pnid].amplua_text)
        display_df["points_avg"] = display_df["points_avg"].apply(lambda f: f"{f:.2f}")
        display_df["points_impact"] = display_df["points_impact"].apply(lambda f: f"{f:.2f}")

        display_df = display_df[display_df["games"] > 1]
        display_df.sort_values("goals", ascending=False, inplace=True)
        display_df = display_df[[
            "player_title", "amplua", "games", "goals", "points", "points_avg", "points_impact"
        ]]

        display_df = display_df.rename(columns={
            "player_title": "Игрок",
            "amplua": "Поз.",
            "games": "И",
            "goals": "Г",
            "points": "О",
            "points_avg": "O/И",
            "points_impact": "O-Имп"
        })
        renderer.pd_table(display_df, sortable=True)
