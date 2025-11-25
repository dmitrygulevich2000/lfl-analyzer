from collections import defaultdict
from typing import Dict

import pandas as pd

from loader import MatchesLoader, ProtocolLoader, SquadsLoader
from render import Renderer
from .Report import Report
from .common.Common import *
from Util import *


class SeasonsStatsReport(Report):
    def __init__(self, reserve_club: int, main_club: int, seasons: List[int], build_id: str):
        self.reserve_club = reserve_club
        self.main_club = main_club
        self.seasons = seasons
        self.build_id = build_id

    def build(self):
        reserve_stats = self.__load_seasons_agg_stats(self.reserve_club, self.seasons, self.build_id)
        add_points_stats(reserve_stats.player_df, total_games=reserve_stats.total_games,
                         total_points=reserve_stats.total_points)
        self.reserve_stats = reserve_stats

        main_stats = self.__load_seasons_agg_stats(self.main_club, self.seasons, self.build_id)
        add_points_stats(main_stats.player_df, total_games=main_stats.total_games,
                         total_points=main_stats.total_points)
        self.main_stats = main_stats

        combined_df = reserve_stats.player_df.join(
            main_stats.player_df, how='outer', lsuffix='_reserve', rsuffix='_main'
        )
        combined_df.fillna(0, inplace=True)
        self.combined_df = combined_df

        self.players = reserve_stats.player_info | main_stats.player_info

    def render(self, renderer: Renderer, level=1):
        renderer.heading("Общая статистика (в дубле и основе)", level)
        renderer.text(f"Дубль:  {self.reserve_stats.total_games} игр,  {self.reserve_stats.total_points} очков"
                      f"  ({self.reserve_stats.total_points / self.reserve_stats.total_games:.2f} очков за игру)")
        renderer.text(f"Основа:  {self.main_stats.total_games} игр,  {self.main_stats.total_points} очков"
                      f"  ({self.main_stats.total_points / self.main_stats.total_games:.2f} очков за игру)")

        display_df = self.combined_df.reset_index(names="person_id")
        display_df["player_title"] = display_df["person_id"].apply(lambda pnid: (
            pr := self.players[pnid],
            renderer.get_href(pr.name, build_player_url(pr.person_id, pr.player_id))
        )[-1])
        display_df["amplua"] = display_df["person_id"].apply(lambda pnid: self.players[pnid].amplua_text)
        display_df["points_impact_reserve"] = display_df["points_impact_reserve"].apply(lambda f: f"{f:.2f}")
        display_df["points_avg_reserve"] = display_df["points_avg_reserve"].apply(lambda f: f"{f:.2f}")
        display_df["points_impact_main"] = display_df["points_impact_main"].apply(lambda f: f"{f:.2f}")
        display_df["points_avg_main"] = display_df["points_avg_main"].apply(lambda f: f"{f:.2f}")
        display_df["separator"] = ""

        display_df = limit_by_cum_percent_threshold(display_df, "games_reserve", 0.7)
        display_df.sort_values("games_main", ascending=False, inplace=True)
        display_df = display_df[[
            "player_title", "amplua",
            "games_reserve", "goals_reserve", "points_reserve", "points_avg_reserve", "points_impact_reserve",
            "separator",
            "games_main", "goals_main", "points_main", "points_avg_main", "points_impact_main",
        ]]

        display_df = display_df.rename(columns={
            "player_title": "Игрок",
            "amplua": "Поз.",
            "games_reserve": "[Д] И",
            "games_reserve_cum_percent": "[Д] Кум-%-И",
            "goals_reserve": "[Д] Г",
            "points_reserve": "[Д] O",
            "points_avg_reserve": "[Д] O/И",
            "points_impact_reserve": "[Д] O-Имп",
            "separator": "",
            "games_main": "[O] И",
            "goals_main": "[O] Г",
            "points_main": "[O] O",
            "points_avg_main": "[O] O/И",
            "points_impact_main": "[O] O-Имп",
        })
        renderer.pd_table(display_df, sortable=True)

    def __load_season_stats(self, club: int, season: int, build_id: str) -> Stats:
        matches_json = MatchesLoader(club, season=season).load_json()
        match_ids = [match["match_id"] for match in matches_json]
        return load_stats(club, match_ids, build_id)

    def __load_seasons_agg_stats(self, club: int, seasons: List[int], build_id: str) -> Stats:
        if (not seasons):
            return

        agg_stats = self.__load_season_stats(club, seasons[0], build_id)
        for season in seasons[1:]:
            stats = self.__load_season_stats(club, season, build_id)
            agg_stats += stats

        return agg_stats
