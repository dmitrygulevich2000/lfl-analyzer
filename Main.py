from pages import GithubPages

if (__name__ == "__main__"):
    pages = GithubPages("neon-reports")

    reserve_club = 10779
    reserve_tournaments = [29582]
    main_club = 7906
    main_tournaments = [27981]

    seasons = [82]
    days = 60

    build_id = "sdJ0eSd8n8H8DK_1LfT9l"

    pages.create_reserve_report(
        "Неон-Д",
        reserve_club=reserve_club,
        reserve_tournaments=reserve_tournaments,
        main_club=main_club,
        main_tournaments=main_tournaments,
        seasons=seasons,
        days=days,
        page_lfl_build_id=build_id,
    )
    pages.create_main_report(
        "Неон",
        reserve_club=reserve_club,
        reserve_tournaments=reserve_tournaments,
        main_club=main_club,
        main_tournaments=main_tournaments,
        seasons=seasons,
        days=days,
        page_lfl_build_id=build_id,
    )

    pages.create_index()
