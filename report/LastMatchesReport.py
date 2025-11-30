import pandas as pd
from datetime import datetime, timedelta

from loader import MatchesLoader
from render import Renderer
from .Report import Report
from Util import *
from .common.Common import *


class LastMatchesReport(Report):
    MATCH_DATE_FORMAT = "%d.%m.%Y - %a"
    MATCH_TIME_FORMAT = "%H:%M"

    def __init__(self, club, days):
        self.club = club
        self.days = days

    def build(self):
        last_matches_json = load_last_matches(self.club, self.days)

        self.season = last_matches_json[0]["season_id"]
        self.last_matches_json = last_matches_json

    def render(self, renderer: Renderer, level=1):
        renderer.heading("Результаты", level)

        total_points = 0
        last_matches_data = []

        for match in self.last_matches_json:
            assert (match["protocol"] == 1 or is_techical_defeat(match))

            total_points += club_points(match, self.club)

            match_date_time = datetime.fromisoformat(match["match_date_time"]).astimezone(TZ)

            home_name = match["home_club_short_name"] if match["home_club_short_name"] else match["home_club_name"]
            home = renderer.get_href(home_name, build_club_url(match["home_id"]))
            if match["home_id"] == self.club:
                home = renderer.get_bold(home)

            away_name = match["away_club_short_name"] if match["away_club_short_name"] else match["away_club_name"]
            away = renderer.get_href(away_name, build_club_url(match["away_id"]))
            if match["away_id"] == self.club:
                away = renderer.get_bold(away)
            last_matches_data.append(
                [
                    match_date_time.date().strftime(LastMatchesReport.MATCH_DATE_FORMAT),
                    match_date_time.time().strftime(LastMatchesReport.MATCH_TIME_FORMAT),
                    home,
                    renderer.get_href(
                        "{}:{}".format(match["home_score"], match["away_score"]) +
                        ("\n({})".format(match["note"]) if match["note"] else ""),
                        build_match_url(match["tournament_id"], match["tour"], match["match_id"])
                    ),
                    away,
                ]
            )

        display_df = pd.DataFrame(data=last_matches_data, columns=[
            renderer.get_href("ещё матчи", build_matches_url(self.club, self.season)), "...", "...", "...", "..."])

        renderer.pd_table(display_df)
