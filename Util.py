from zoneinfo import ZoneInfo


BASE_URL = "https://lfl.ru"


def build_player_url(person_id, player_id):
    url = f"{BASE_URL}/person{person_id}"
    if player_id is not None:
        url += f"?player_id={player_id}"
    return url


def build_club_url(club_id):
    return f"{BASE_URL}/club{club_id}"


def build_tournament_url(tournament_id):
    return f"{BASE_URL}/tournament{tournament_id}"


def build_matches_url(club_id, season_id):
    return f"{BASE_URL}/moscow8x8/calendar?club_id={club_id}&season_id={season_id}&matches=all&sort=timeasc"


def build_match_url(tournament_id, tour, match_id):
    return f"{BASE_URL}/tournament{tournament_id}/tour{tour}/match{match_id}"


LEGACY_SEASON_IDS = {
    2025: 82, 2024: 80, 2023: 45, 2022: 43, 2021: 41,
    2020: 39, 2019: 37, 2018: 35, 2017: 33, 2016: 31,
    2015: 23, 2014: 11, 2013: 8, 2012: 1, 2011: 4,
    2010: 20, 2009: 19, 2008: 18, 2007: 17, 2006: 16,
    2005: 15, 2004: 14, 2003: 13, 2002: 12
}


def season_id_by_year(year):
    return LEGACY_SEASON_IDS.get(year, (year - 1984) * 2)


DISPLAY_DATE_FORMAT = "%d %B %Y"

NEON_D_CLUB_ID = 10779
NEON_CLUB_ID = 7906

TZ = ZoneInfo("Europe/Moscow")
