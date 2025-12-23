from datetime import date
import pandas as pd

from loader import MatchesLoader, ProtocolLoader
from render import Renderer
from .Report import Report
from Util import *
from .common.Common import *


class ClubStatsReportBase(Report):
    def __init__(self, build_id):
        self.build_id = build_id

    def build(self):
        pass

    def render(self, renderer: Renderer, level=1):
        renderer.heading("Статистика команды", level)
        renderer.text(f"Игр:               {self.total_games}")
        renderer.text(f"Набрано очков:     {self.total_points} / {3 * self.total_games}")
        renderer.text(f"Очков за игру:     {self.total_points/self.total_games:.2f}")
        renderer.text(f"Средний возраст:   {self.age_avg:.2f} года")
        renderer.text(f"Медианный возраст: {self.age_median:.2f} года")
        renderer.text(f"Количество замен:  {self.avg_turnout - 8:.2f} человека")

    def _finalize(self, club_stats: ClubStats) -> Self:
        club_stats.ages_array.sort()
        self.total_games = club_stats.total_games
        self.total_points = club_stats.total_points
        self.age_avg = sum(club_stats.ages_array) / club_stats.total_turnout
        self.age_median = club_stats.ages_array[len(club_stats.ages_array) // 2]
        self.avg_turnout = club_stats.total_turnout / club_stats.total_protocols

    def _load_for_matches(self, club, matches_json) -> ClubStats:
        today = date.today()

        total_protocols = 0
        total_turnout = 0
        total_games = 0
        total_points = 0
        ages_array = []
        for match in matches_json:
            total_games += 1
            total_points += club_points(match, club)
            if is_techical_defeat(match):
                continue

            protocol = ProtocolLoader(self.build_id, match["match_id"]).load_json()
            club_lineup = [p for p in protocol["lineup"] if p["club_id"] == club]

            turnout = len(club_lineup)
            if turnout > 15:
                # skip match with possibly wrong protocol
                continue

            total_protocols += 1
            total_turnout += turnout
            ages_array += [calculate_age(p["birthday"], today) for p in club_lineup]

        return ClubStats(
            total_protocols=total_protocols,
            total_games=total_games,
            total_points=total_points,
            total_turnout=total_turnout,
            ages_array=ages_array,
        )


class LastMatchesClubStatsReport(ClubStatsReportBase):
    def __init__(self, club, days, build_id):
        super().__init__(build_id)
        self.club = club
        self.days = days

    def build(self):
        matches_json = load_last_matches(self.club, self.days)
        stats = self._load_for_matches(self.club, matches_json)

        self._finalize(stats)


class SeasonsClubStatsReport(ClubStatsReportBase):
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
        stats = self._load_for_matches(self.club, matches_json)
        for season in self.seasons[1:]:
            matches_json = MatchesLoader(self.club, season=season).load_json()
            if self.tournaments_filter is not None:
                matches_json = [m for m in matches_json if m["tournament_id"] in self.tournaments_filter]
            season_stats = self._load_for_matches(self.club, matches_json)
            stats += season_stats

        self._finalize(stats)


class SeasonsClubsClubStatsReport(ClubStatsReportBase):
    def __init__(self, clubs, seasons, build_id, tournaments_filter=None):
        super().__init__(build_id)
        self.clubs = clubs
        self.seasons = seasons
        self.tournaments_filter = tournaments_filter

    def build(self):
        if (not self.seasons):
            return

        total_stats = None
        for club in self.clubs:

            matches_json = MatchesLoader(club, season=self.seasons[0]).load_json()
            stats = self._load_for_matches(club, matches_json)

            for season in self.seasons[1:]:
                matches_json = MatchesLoader(club, season=season).load_json()
                season_stats = self._load_for_matches(club, [m["match_id"] for m in matches_json])

                stats += season_stats

            if total_stats is None:
                total_stats = stats
            else:
                total_stats += stats

        self._finalize(total_stats)
