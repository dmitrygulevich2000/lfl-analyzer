from collections import defaultdict
from typing import Dict

import pandas as pd

from loader import MatchesLoader, ProtocolLoader, SquadsLoader
from render import Renderer
from .Report import Report
from .common.Common import *
from Util import *


# deprecated in favor of SeasonsStatsReport
class ReserveCapMainReport(Report):
    def __init__(self, reserve_club, reserve_tournaments, main_club, main_tournaments, build_id):
        self.reserve_club = reserve_club
        self.reserve_tournaments = reserve_tournaments
        self.main_club = main_club
        self.main_tournaments = main_tournaments
        self.build_id = build_id

    def build(self):
        reserve_df, reserve_players = self.__load_squad_agg_df(self.reserve_club, self.reserve_tournaments)
        squad_points, total_games, total_points = self.__load_squad_points(self.reserve_club, self.reserve_tournaments)
        reserve_df["points_reserve"] = squad_points
        reserve_df["points_avg_reserve"] = reserve_df["points_reserve"] / reserve_df["games"]
        reserve_df["points_impact_reserve"] = reserve_df["points_reserve"] - \
            total_points * reserve_df["games"] / total_games

        main_df, main_players = self.__load_squad_agg_df(self.main_club, self.main_tournaments)

        self.intersection_df = self.__build_intersection_df(reserve_df, main_df)
        self.players = reserve_players | main_players
        self.total_games_reserve = total_games
        self.total_points_reserve = total_points

    def render(self, renderer: Renderer, level=1):
        renderer.heading("Общая статистика (в дубле и основе)", level)
        renderer.text(f"Дубль:  {self.total_games_reserve} игр,  {self.total_points_reserve} очков"
                      f"  ({self.total_points_reserve / self.total_games_reserve:.2f} очков за игру)")

        display_df = self.intersection_df.reset_index(names="person_id")
        display_df["player_title"] = list(map(lambda pnid: (
            pr := self.players[pnid],
            renderer.get_href(pr.name, build_player_url(pr.person_id, pr.player_id))
        )[-1], display_df["person_id"]))
        display_df["amplua"] = list(map(lambda pnid: self.players[pnid].amplua_text, display_df["person_id"]))
        display_df["points_impact_reserve"] = display_df["points_impact_reserve"].apply(lambda f: f"{f:.2f}")
        display_df["points_avg_reserve"] = display_df["points_avg_reserve"].apply(lambda f: f"{f:.2f}")
        display_df["separator"] = ""

        display_df = display_df[[
            "player_title", "amplua",
            "games_reserve", "goals_reserve", "points_reserve", "points_avg_reserve", "points_impact_reserve",
            "separator",
            "games_main", "goals_main",
        ]]

        display_df = display_df.rename(columns={
            "player_title": "Игрок",
            "amplua": "Поз.",
            "games_reserve": "[Д] И",
            "games_cum_percent_reserve": "[Д] Кум-%-И",
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

    def __load_squad_agg_df(self, club, tournaments):
        dfs = []
        agg_players = {}
        for tournament in tournaments:
            df, players = self.__load_squad_df(club, tournament)
            dfs.append(df)
            agg_players.update(players)
        return (sum_stats(*dfs), agg_players)

    def __load_squad_df(self, club, tournament):
        raw_json = SquadsLoader(club, tournament).load_json()

        squad_players = {
            player["person_id"]: PlayerInfo(
                player["person_id"],
                player["player_id"],
                player["family_name"] + " " + player["first_name"],
                amplua_text(player["amplua"]),
            )
            for player in raw_json["data"] if len(player["stats"]) > 0 and player["stats"][0] is not None
        }
        index = [
            player["person_id"]
            for player in raw_json["data"] if len(player["stats"]) > 0 and player["stats"][0] is not None
        ]
        data = [
            [
                player["stats"][0]["games"],
                player["stats"][0]["player_goals"]
            ]
            for player in raw_json["data"] if len(player["stats"]) > 0 and player["stats"][0] is not None
        ]

        df = pd.DataFrame(data, index=index, columns=["games", "goals"], dtype="Int32")
        return df, squad_players

    def __load_squad_points(self, club, tournaments) -> tuple[Dict[int, int], int, int]:
        squad_points = defaultdict(lambda: 0)
        total_games = 0
        total_points = 0

        for tournament in tournaments:
            matches_json = MatchesLoader(club, tournament=tournament).load_json()
            total_games += len(matches_json)

            for match in matches_json:
                total_points += club_points(match, club)
                protocol = ProtocolLoader(self.build_id, match["match_id"]).load_json()

                for player in protocol["lineup"]:
                    if player["club_id"] != club:
                        continue
                    squad_points[player["person_id"]] += club_points(match, club)

        return squad_points, total_games, total_points

    def __build_intersection_df(self, reserve_df, main_df):
        df = reserve_df.join(main_df, how='outer', lsuffix='_reserve', rsuffix='_main')

        df.sort_values("games_reserve", ascending=False, inplace=True)
        games_reserve_total = df["games_reserve"].sum()
        df["games_cum_percent_reserve"] = (df["games_reserve"].cumsum() /
                                           games_reserve_total).round(2).shift(periods=1, fill_value=0)
        min_games_to_take = df[df["games_cum_percent_reserve"] < 0.7]["games_reserve"].array[-1]
        df = df[df["games_reserve"] >= min_games_to_take]

        df.sort_values("games_main", ascending=False, inplace=True)
        df.fillna(0, inplace=True)
        return df
