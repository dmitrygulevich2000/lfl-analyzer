from pages import GithubPages

if (__name__ == "__main__"):
    pages = GithubPages("neon-reports")
    pages.create_reserve_report(
        "Неон-Д",

        reserve_club=10779,
        reserve_tournaments=[29582],
        main_club=7906,
        main_tournaments=[27981],

        season_years=[2025],
        days=60,

        page_lfl_build_id="B20Pga0-v9f8bLmpj4GDv"
    )
    pages.create_index()
