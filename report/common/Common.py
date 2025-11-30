from dataclasses import dataclass
from datetime import datetime, timedelta
import sys
from typing import Dict, List, Self, Set

import pandas as pd

from Util import *
from loader import MatchesLoader, PlayerMatchesLoader, ProtocolLoader

# parsing helpers

BIRTHDAY_DATE_FORMAT = "%Y-%m-%d"


def calculate_age(birthday_str, at_date):
    birthday_date = datetime.strptime(birthday_str, BIRTHDAY_DATE_FORMAT).date()
    age_timedelta = at_date - birthday_date
    return age_timedelta.days / 365.25


def club_points(match_json, club_id):
    if club_id == match_json["home_id"]:
        return match_json["home_points"]
    assert (match_json["away_id"] == club_id)
    return match_json["away_points"]


AMPLUA_TEXTS = ["вр", "защ", "п/з", "нап"]


def amplua_text(amplua):
    return AMPLUA_TEXTS[amplua - 1]


def is_techical_defeat(match_json):
    return match_json["technical_defeat"]["data"][0] == ord('1')


def load_last_matches(club, days):
    date_threshold = datetime.today().astimezone(TZ) - timedelta(days=days)
    matches_json = MatchesLoader(club).load_json()

    last_matches_json = [match for match in matches_json if
                         datetime.fromisoformat(match["match_date_time"]) > date_threshold]
    return sorted(last_matches_json, key=lambda m: datetime.fromisoformat(m["match_date_time"]))


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
    if any([len(df) == 0 for df in dfs]):
        print("damn")
    return pd.concat(dfs).groupby(level=0).sum()


def df_floats_round2(df: pd.DataFrame, label: str | List[str]) -> pd.DataFrame:
    if isinstance(label, str):
        df[label] = df[label].apply(lambda f: f"{f:.2f}")
        return df
    assert (isinstance(label, list))
    for l in label:
        df[l] = df[l].apply(lambda f: f"{f:.2f}")


def limit_by_cum_percent_threshold(df: pd.DataFrame, label: str, threshold: float) -> pd.DataFrame:
    assert (threshold >= 0 and threshold <= 1.0)

    df.sort_values(label, ascending=False, inplace=True)
    total = df[label].sum()
    cum_percent_label = label + "_cum_percent"
    df[cum_percent_label] = (df[label].cumsum() / total).round(2)
    # .shift(periods=1, fill_value=0)
    min_value_to_take = df[df[cum_percent_label] >= threshold][label].array[0]
    return df[df[label] >= min_value_to_take]


@dataclass
class PlayerStats:
    total_games: int
    total_points: int
    player_info: Dict[int, PlayerInfo]
    player_df: pd.DataFrame

    def __iadd__(self, other):
        assert (isinstance(other, PlayerStats))

        self.total_games += other.total_games
        self.total_points += other.total_points
        self.player_info.update(other.player_info)
        self.player_df = sum_stats(self.player_df, other.player_df)
        return self

    def calc_points(self) -> Self:
        self.player_df["points_avg"] = self.player_df["points"] / self.player_df["games"]
        self.player_df["points_impact"] = self.player_df["points"] - \
            self.total_points * self.player_df["games"] / self.total_games
        return self

    def calc_scores(self) -> Self:
        self.player_df["goals_avg"] = self.player_df["goals"] / self.player_df["games"]
        self.player_df["goals_assists"] = self.player_df["goals"] + self.player_df["assists"]
        self.player_df["goals_assists_avg"] = self.player_df["goals_assists"] / self.player_df["games"]
        return self

    def load_assists(self, club_id: int, match_ids: Set[int], season_hint: int = None):
        player_assists = {}
        for player in self.player_info.values():
            player_assists[player.person_id] = 0

            all_matches_json = PlayerMatchesLoader(
                player.player_id, season=season_hint if season_hint is not None else "").load_json()
            matches_json = [m for m in all_matches_json if
                            m["match_id"] in match_ids and
                            not is_techical_defeat(m) and
                            m["player_club"] == club_id]

            # ensure all matches was loaded
            assert (len(matches_json) == self.player_df["games"][player.person_id])

            for m in matches_json:
                player_assists[player.person_id] += m["player_assists"]

        self.player_df["assists"] = player_assists
        return self

    def load(club: int, match_ids: List[int], build_id: str) -> Self:
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

            if (not is_techical_defeat(protocol["info"])):
                if len(df) == 0:
                    print(f"Empty statistics for match {mid}", file=sys.stderr)
                else:
                    stats_dfs.append(df)
                    all_players.update(match_players)
            total_club_points += club_points(protocol["info"], club)

        total_games = len(match_ids)
        stats_df = sum_stats(*stats_dfs)

        return PlayerStats(
            total_games=total_games,
            total_points=total_club_points,
            player_info=all_players,
            player_df=stats_df,
        )


def load_player_stats(club: int, match_ids: List[int], build_id: str) -> PlayerStats:
    return PlayerStats.load(club, match_ids, build_id)


@dataclass
class ClubStats:
    total_games: int
    total_points: int
    total_turnout: int
    ages_array: int

    def __iadd__(self, other):
        assert (isinstance(other, ClubStats))

        self.total_games += other.total_games
        self.total_points += other.total_points
        self.total_turnout += other.total_turnout
        self.ages_array += other.ages_array
        return self
