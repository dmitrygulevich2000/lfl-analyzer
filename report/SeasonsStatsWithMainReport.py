from typing import Dict

import pandas as pd

from loader import MatchesLoader, ProtocolLoader, SquadsLoader
from render import Renderer
from .Report import Report
from .common.Common import *
from Util import *


class SeasonsStatsWithMainReport(Report):
    def __init__(self, reserve_club: int, main_club: int, seasons: List[int], build_id: str):
        self.reserve_club = reserve_club
        self.main_club = main_club
        self.seasons = seasons
        self.build_id = build_id

    def build(self):
        self.reserve_stats = self.__load_seasons_agg_stats(
            self.reserve_club, self.seasons, self.build_id).calc_points().calc_scores()
        self.main_stats = self.__load_seasons_agg_stats(
            self.main_club, self.seasons, self.build_id).calc_points().calc_scores()

        self.combined_df = self.reserve_stats.player_df.join(
            self.main_stats.player_df, how='outer', lsuffix='_reserve', rsuffix='_main'
        ).fillna(0).convert_dtypes()
        self.players = self.reserve_stats.player_info | self.main_stats.player_info

    def render(self, renderer: Renderer, level=1):
        renderer.heading("Дубль || Основа", level)
        renderer.text(f"Дубль:  {self.reserve_stats.total_games} игр,  {self.reserve_stats.total_points} очков"
                      f"  ({self.reserve_stats.total_points / self.reserve_stats.total_games:.2f} очков за игру)")
        renderer.text(f"Основа:  {self.main_stats.total_games} игр,  {self.main_stats.total_points} очков"
                      f"  ({self.main_stats.total_points / self.main_stats.total_games:.2f} очков за игру)")
        renderer.text("В таблице ниже выбраны игроки, покрывающие 70% всех \"явок\" на игры дубля")

        display_df = self.combined_df.reset_index(names="person_id")
        display_df["player_title"] = display_df["person_id"].apply(lambda pnid: (
            pr := self.players[pnid],
            renderer.get_href(pr.name, build_player_url(pr.person_id, pr.player_id))
        )[-1])
        display_df["amplua"] = display_df["person_id"].apply(lambda pnid: self.players[pnid].amplua_text)
        df_floats_round2(display_df, [
            "goals_avg_reserve",
            "goals_assists_avg_reserve",
            "points_avg_reserve",
            "points_impact_reserve",
            "goals_avg_main",
            "goals_assists_avg_main",
            "points_avg_main",
            "points_impact_main",
        ])
        display_df["separator"] = ""

        display_df = limit_by_cum_percent_threshold(display_df, "games_reserve", 0.7)
        display_df.sort_values("games_main", ascending=False, inplace=True)
        display_df = display_df[[
            "player_title", "amplua",
            "games_reserve", "goals_reserve", "assists_reserve", "goals_assists_reserve", "goals_avg_reserve", "goals_assists_avg_reserve",
            "points_reserve", "points_avg_reserve", "points_impact_reserve",
            "separator",
            "games_main", "goals_main", "assists_main", "goals_assists_main", "goals_avg_main", "goals_assists_avg_main",
            "points_main", "points_avg_main", "points_impact_main",
        ]]

        display_df = display_df.rename(columns={
            "player_title": "Игрок",
            "amplua": "Поз.",
            "games_reserve": "[Д] И",
            "games_reserve_cum_percent": "[Д] Кум-%-И",
            "goals_reserve": "[Д] Г",
            "assists_reserve": "[Д] П",
            "goals_assists_reserve": "[Д] Г+П",
            "goals_avg_reserve": "[Д] Г/И",
            "goals_assists_avg_reserve": "[Д] (Г+П)/И",
            "points_reserve": "[Д] О",
            "points_avg_reserve": "[Д] О/И",
            "points_impact_reserve": "[Д] О-Имп(*)",
            "separator": "",
            "games_main": "[О] И",
            "goals_main": "[О] Г",
            "assists_main": "[О] П",
            "goals_assists_main": "[О] Г+П",
            "goals_avg_main": "[О] Г/И",
            "goals_assists_avg_main": "[О] (Г+П)/И",
            "points_main": "[О] О",
            "points_avg_main": "[О] О/И",
            "points_impact_main": "[О] О-Имп(*)",
        })
        renderer.pd_table(display_df, sortable=True, sticky_column=True)
        if any(map(lambda s: "О-Имп" in s, display_df.columns.tolist())):
            renderer.text("(*) O-Имп (очковый импакт) вычисляется по формуле: (O/И игрока - О/И команды) * И игрока")

    def __load_season_stats(self, club: int, season: int, build_id: str) -> PlayerStats:
        matches_json = MatchesLoader(club, season=season).load_json()
        match_ids = [match["match_id"] for match in matches_json]
        return load_player_stats(club, match_ids, build_id).load_assists(club, set(match_ids))

    def __load_seasons_agg_stats(self, club: int, seasons: List[int], build_id: str) -> PlayerStats:
        if (not seasons):
            return

        agg_stats = self.__load_season_stats(club, seasons[0], build_id)
        for season in seasons[1:]:
            stats = self.__load_season_stats(club, season, build_id)
            agg_stats += stats

        return agg_stats
