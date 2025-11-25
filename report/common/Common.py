from dataclasses import dataclass
from typing import Dict, List

import pandas as pd

from loader import ProtocolLoader

# parsing helpers


def club_points(match_json, club_id):
    if club_id == match_json["home_id"]:
        return match_json["home_points"]
    assert (match_json["away_id"] == club_id)
    return match_json["away_points"]


AMPLUA_TEXTS = ["вр", "защ", "п/з", "нап"]


def amplua_text(amplua):
    return AMPLUA_TEXTS[amplua - 1]


@dataclass
class PlayerInfo:
    person_id: int
    player_id: int
    name: str
    amplua_text: str

# data science helpers


def sum_stats_with_multiindex(*dfs):
    return pd.concat(dfs).groupby(dfs[0].index.names).sum()


def sum_stats(*dfs):
    return pd.concat(dfs).groupby(level=0).sum()


def limit_by_cum_percent_threshold(df, label, threshold):
    df.sort_values(label, ascending=False, inplace=True)
    total = df[label].sum()
    cum_percent_label = label + "_cum_percent"
    df[cum_percent_label] = (df[label].cumsum() / total).round(2).shift(periods=1, fill_value=0)
    min_value_to_take = df[df[cum_percent_label] < threshold][label].array[-1]
    return df[df[label] >= min_value_to_take]


@dataclass
class Stats:
    total_games: int
    total_points: int
    player_info: Dict[int, PlayerInfo]
    player_df: pd.DataFrame

    def __iadd__(self, other):
        assert (isinstance(other, Stats))

        self.total_games += other.total_games
        self.total_points += other.total_points
        self.player_info.update(other.player_info)
        self.player_df = sum_stats(self.player_df, other.player_df)


def load_stats(club: int, match_ids: List[int], build_id: str) -> Stats:
    stats_dfs = []
    all_players = {}
    total_club_points = 0

    for mid in match_ids:
        protocol = ProtocolLoader(build_id, mid).load_json()

        match_players = {
            player["person_id"]: PlayerInfo(
                player["person_id"],
                player["player_id"],
                player["player_name"],
                amplua_text(player["amplua"]),
            )
            for player in protocol["lineup"] if player["club_id"] == club
        }
        index = [player["person_id"] for player in protocol["lineup"] if player["club_id"] == club]
        data = [
            [
                1,  # games
                0,  # goals for future count
                club_points(protocol["info"], club)
            ]
            for player in protocol["lineup"] if player["club_id"] == club
        ]

        df = pd.DataFrame(data, index=index, columns=["games", "goals", "points"], dtype="Int32")
        for goal in protocol["goals"]:
            if (goal["club_id"] != club or goal["goal_person_id"] not in match_players):
                continue
            df.loc[goal["goal_person_id"], "goals"] += 1

        if (protocol["info"]["technical_defeat"]["data"][0] != ord('1')):
            stats_dfs.append(df)
            all_players.update(match_players)
        total_club_points += club_points(protocol["info"], club)

    total_games = len(match_ids)
    stats_df = sum_stats(*stats_dfs)

    return Stats(
        total_games=total_games,
        total_points=total_club_points,
        player_info=all_players,
        player_df=stats_df,
    )


def add_points_stats(df: pd.DataFrame, *, total_games: int, total_points: int):
    df["points_avg"] = df["points"] / df["games"]
    df["points_impact"] = df["points"] - total_points * df["games"] / total_games
