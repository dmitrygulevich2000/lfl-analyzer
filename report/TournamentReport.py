import pandas as pd

from loader import TournamentLoader, RatingLoader
from render import Renderer
from .Report import Report
from Util import *


class TournamentReport(Report):
    def __init__(self, tournament, clubs):
        self.tournament = tournament
        self.clubs = clubs

    def build(self):
        self.name = TournamentLoader(self.tournament).load_json()["data"]["name"]

        df = self.__load_rating_df(self.tournament)
        self.clubs_count = len(df)

        df["scores_avg"] = df["scores"] / df["games"]

        df["gfor_avg"] = df["gfor"] / df["games"]
        df.sort_values("gfor", ascending=False, inplace=True)
        df["gfor_rank"] = range(1, len(df) + 1)

        df["gout_avg"] = df["gout"] / df["games"]
        df.sort_values("gout", ascending=True, inplace=True)
        df["gout_rank"] = range(1, len(df) + 1)

        df.sort_values("position", inplace=True)
        df = df[df["club_id"].isin(self.clubs)]

        self.df = df

    def render(self, renderer: Renderer, level=1):
        renderer.heading(renderer.get_href(self.name, build_tournament_url(self.tournament)), level)

        display_df = self.df
        display_df["club_title"] = display_df.apply(
            lambda r: renderer.get_href(r["club_name"], build_club_url(r["club_id"])),
            axis=1
        )
        display_df["gdiff"] = display_df["gfor"] - display_df["gout"]
        display_df["scores_avg"] = display_df["scores_avg"].apply(lambda f: f"{f:.1f}")
        display_df["gfor_avg"] = display_df["gfor_avg"].apply(lambda f: f"{f:.1f}")
        display_df["gout_avg"] = display_df["gout_avg"].apply(lambda f: f"{f:.1f}")

        display_df = display_df[["position", "club_title", "games", "scores", "scores_avg",
                                 "gfor", "gfor_avg", "gfor_rank", "gout", "gout_avg", "gout_rank", "gdiff"]]
        display_df = display_df.rename(columns={
            "position": "№",
            "club_title": "Команда",
            "games": "И",
            "scores": "O",
            "scores_avg": "O/И",
            "gfor": "З",
            "gfor_avg": "З/И",
            "gfor_rank": "#З",
            "gout": "П",
            "gout_avg": "П/И",
            "gout_rank": "#П",
            "gdiff": "Р"
        })
        renderer.pd_table(display_df)
        renderer.text(f"Всего команд: {self.clubs_count}")

    def __load_rating_df(self, tournament):
        raw_json = RatingLoader(tournament).load_json()

        index_data = [
            (
                club["club_id"],
                club["club_name"],
            )
            for club in raw_json["data"]
        ]
        data = [
            [
                club["position"],
                club["games"],
                club["scores"],
                club["gfor"],
                club["gout"]
            ]
            for club in raw_json["data"]
        ]

        index = pd.MultiIndex.from_tuples(
            index_data, names=["club_id", "club_name"])
        df = pd.DataFrame(data, index=index, columns=["position", "games", "scores", "gfor", "gout"], dtype="Int32")
        df.reset_index(inplace=True)
        return df
