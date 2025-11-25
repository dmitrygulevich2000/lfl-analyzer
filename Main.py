from pages import GithubPages

if (__name__ == "__main__"):
    pages = GithubPages("neon-reports")
    pages.create_reserve_report(
        "Рапид-Д",
        reserve_club=12138,
        reserve_tournaments=[29582, 28285, 29486],
        main_club=2282,
        main_tournaments=[28286, "d1086"],
        seasons=[82],
        days=60,
        page_lfl_build_id="k4Aw4_M9-mhlvkoBZY96z"
    )
    pages.create_index()
