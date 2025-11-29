from pages import GithubPages

if (__name__ == "__main__"):
    pages = GithubPages("neon-reports")
    pages.create_reserve_report(
        "Булат-Д",
        reserve_club=1963,
        reserve_tournaments=[29582],
        main_club=135,
        main_tournaments=[27980],
        seasons=[82],
        days=60,
        page_lfl_build_id="B20Pga0-v9f8bLmpj4GDv"
    )
    pages.create_index()
