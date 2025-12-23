import pandas as pd
from datetime import datetime, timedelta

from loader import MatchesLoader, ProtocolLoader
from render import Renderer
from .Report import Report
from Util import *
from .common.Common import *


class PlayerStatsReportBase(Report):
    def __init__(self, build_id):
        self.build_id = build_id

    def build(self):
        pass

    def _load_for_matches(self, club, match_ids) -> PlayerStats:
        return load_player_stats(club, match_ids, self.build_id).load_assists(
            club,
            set(match_ids),
        )

    def _finalize(self, stats: PlayerStats):
        self.stats = stats.calc_points().calc_scores()

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
            "points_avg": "О/И",
            "points_impact": "О-Имп(*)"
        })
        renderer.pd_table(display_df, sortable=True, sticky_column=True)
        if "О-Имп(*)" in display_df:
            renderer.text("(*) O-Имп (очковый импакт) вычисляется по формуле: (O/И игрока - О/И команды) * И игрока")

    def _customize_table(self, display_df: pd.DataFrame) -> pd.DataFrame:
        pass


class LastMatchesPlayerStatsReport(PlayerStatsReportBase):
    def __init__(self, club, days, build_id):
        super().__init__(build_id)
        self.club = club
        self.days = days

    def build(self):
        last_matches_json = load_last_matches(self.club, self.days)
        last_match_ids = [match["match_id"] for match in last_matches_json]

        stats = self._load_for_matches(self.club, last_match_ids)
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
    def __init__(self, club, seasons, build_id, tournaments_filter=None):
        super().__init__(build_id)
        self.club = club
        self.seasons = seasons
        self.tournaments_filter = tournaments_filter

    def build(self):
        if (not self.seasons):
            return

        matches_json = MatchesLoader(self.club, season=self.seasons[0]).load_json()
        if self.tournaments_filter is not None:
            matches_json = [m for m in matches_json if m["tournament_id"] in self.tournaments_filter]
        stats = self._load_for_matches(self.club, [m["match_id"] for m in matches_json])
        for season in self.seasons[1:]:
            matches_json = MatchesLoader(self.club, season=season).load_json()
            if self.tournaments_filter is not None:
                matches_json = [m for m in matches_json if m["tournament_id"] in self.tournaments_filter]
            season_stats = self._load_for_matches(self.club, [m["match_id"] for m in matches_json])
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


class SeasonsClubsPlayerStatsReport(PlayerStatsReportBase):
    def __init__(self, clubs, seasons, build_id):
        super().__init__(build_id)
        self.clubs = clubs
        self.seasons = seasons

    def build(self):
        if (not self.seasons):
            return

        total_stats = None
        for club in self.clubs:

            matches_json = MatchesLoader(club, season=self.seasons[0]).load_json()
            stats = self._load_for_matches(club, [m["match_id"] for m in matches_json])

            for season in self.seasons[1:]:
                matches_json = MatchesLoader(club, season=season).load_json()
                season_stats = self._load_for_matches(club, [m["match_id"] for m in matches_json])

                stats += season_stats

            if total_stats is None:
                total_stats = stats
            else:
                total_stats += stats

        self._finalize(total_stats)

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
