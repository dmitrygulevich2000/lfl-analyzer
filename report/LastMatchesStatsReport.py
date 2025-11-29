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
        last_matches_json = load_last_matches(self.club, self.days)
        last_match_ids = [match["match_id"] for match in last_matches_json]

        self.stats = load_stats(self.club, last_match_ids, self.build_id).load_assists(
            set(last_match_ids),
            self.club,
        ).calc_points().calc_scores()

    def render(self, renderer: Renderer, level=1):
        renderer.heading("Статистика игроков", level)

        display_df = self.stats.player_df.reset_index(names="person_id")
        display_df["player_title"] = display_df["person_id"].apply(lambda pnid: (
            pr := self.stats.player_info[pnid],
            renderer.get_href(pr.name, build_player_url(pr.person_id, pr.player_id))
        )[-1])
        display_df["amplua"] = display_df["person_id"].apply(lambda pnid: self.stats.player_info[pnid].amplua_text)
        df_floats_round2(display_df, [
            "goals_avg",
            "goals_assists_avg",
            "points_avg",
            "points_impact"
        ])

        display_df = display_df[display_df["games"] > 1]
        display_df.sort_values("goals", ascending=False, inplace=True)
        display_df = display_df[[
            "player_title", "amplua", "games",
            "goals", "assists", "goals_assists", "goals_avg", "goals_assists_avg",
            "points", "points_avg", "points_impact"
        ]]

        display_df = display_df.rename(columns={
            "player_title": "Игрок",
            "amplua": "Поз.",
            "games": "И",
            "goals": "Г",
            "assists": "П",
            "goals_assists": "Г+П",
            "goals_avg": "Г/И",
            "goals_assists_avg": "(Г+П)/И",
            "points": "О",
            "points_avg": "O/И",
            "points_impact": "O-Имп(*)"
        })
        renderer.pd_table(display_df, sortable=True, sticky_column=True)
