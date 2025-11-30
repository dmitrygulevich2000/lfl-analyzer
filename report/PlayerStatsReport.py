import pandas as pd
from datetime import datetime, timedelta

from loader import MatchesLoader, ProtocolLoader
from render import Renderer
from .Report import Report
from Util import *
from .common.Common import *


class PlayerStatsReportBase(Report):
    def __init__(self, club, build_id):
        self.club = club
        self.build_id = build_id

    def build(self):
        pass

    def _load_for_matches(self, match_ids) -> PlayerStats:
        return load_player_stats(self.club, match_ids, self.build_id).load_assists(
            self.club,
            set(match_ids),
        ).calc_points().calc_scores()

    def _finalize(self, stats: PlayerStats):
        self.stats = stats

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

        display_df = self._customize_table(display_df)

        display_df = display_df.rename(columns={
            "player_title": "Игрок",
            "amplua": "Поз.",
            "games": "И",
            "games_cum_percent": "Кум-%-И",
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

    def _customize_table(self, display_df: pd.DataFrame) -> pd.DataFrame:
        pass


class LastMatchesPlayerStatsReport(PlayerStatsReportBase):
    def __init__(self, club, days, build_id):
        super().__init__(club, build_id)
        self.days = days

    def build(self):
        last_matches_json = load_last_matches(self.club, self.days)
        last_match_ids = [match["match_id"] for match in last_matches_json]

        stats = self._load_for_matches(last_match_ids)
        self._finalize(stats)

    def _customize_table(self, display_df: pd.DataFrame) -> pd.DataFrame:
        df = display_df[display_df["games"] > 1].copy()
        df.sort_values("goals", ascending=False, inplace=True)
        df = df[[
            "player_title", "amplua", "games",
            "goals", "assists", "goals_assists", "goals_avg", "goals_assists_avg",
            "points", "points_avg", "points_impact"
        ]]
        return df


class SeasonsPlayerStatsReport(PlayerStatsReportBase):
    def __init__(self, club, seasons, build_id):
        super().__init__(club, build_id)
        self.seasons = seasons

    def build(self):
        if (not self.seasons):
            return

        matches_json = MatchesLoader(self.club, season=self.seasons[0]).load_json()
        stats = self._load_for_matches([m["match_id"] for m in matches_json])
        for season in self.seasons[1:]:
            matches_json = MatchesLoader(self.club, season=season).load_json()
            season_stats = self._load_for_matches([m["match_id"] for m in matches_json])
            stats += season_stats

        self._finalize(stats)

    def _customize_table(self, display_df: pd.DataFrame) -> pd.DataFrame:
        # dummy filter that calcs games_cum_percent
        display_df = limit_by_cum_percent_threshold(display_df, "games", 1.0)
        display_df.sort_values("games", ascending=False, inplace=True)
        display_df = display_df[[
            "player_title", "amplua", "games", "games_cum_percent",
            "goals", "assists", "goals_assists", "goals_avg", "goals_assists_avg",
            "points", "points_avg", "points_impact"
        ]]
        return display_df
