import os
from datetime import date, datetime
from dataclasses import dataclass
from transliterate import translit

from render import HtmlRenderer, MdRenderer
from report import *


@dataclass
class ReportEntry:
    path_rel_to_index: str
    created_at: date


@dataclass
class ReportDirectory:
    name: str
    reports: list[ReportEntry]


class GithubPages:
    FILENAME_DATE_FORMAT = "%d_%m_%Y"

    def __init__(self, directory):
        self.directory = directory

    def create_reserve_report(self, name_russian, *, reserve_club, reserve_tournaments, main_club, main_tournaments, season_years, days, page_lfl_build_id):
        season_years.sort()
        seasons = [season_id_by_year(s) for s in season_years]
        seasons_header = "Сезон {}".format(season_years[0])
        if len(seasons) != 1:
            seasons_header = "Сезоны {}".format(",".join(seasons))

        report = SequenceReport(header=NameDateHeaderReport(name_russian, reserve_club),
                                reports=[
            SequenceReport(header=HeaderReport("Турнирное положение"), reports=[
                *([TournamentReport(t, {reserve_club, NEON_D_CLUB_ID}) for t in reserve_tournaments] +
                  [TournamentReport(t, {main_club, NEON_CLUB_ID})for t in main_tournaments]),
            ]),
            SequenceReport(header=HeaderReport("Последние матчи"), reports=[
                ColumnsReport(SequenceReport(reports=[
                    LastMatchesReport(reserve_club, days),
                    LastMatchesClubStatsReport(reserve_club, days, page_lfl_build_id),
                ]),
                    LastMatchesPlayerStatsReport(reserve_club, days, page_lfl_build_id)),
            ]),
            SequenceReport(header=HeaderReport(seasons_header), reports=[
                SeasonsClubStatsReport(reserve_club, seasons, page_lfl_build_id),
                SeasonsPlayerStatsReport(reserve_club, seasons, page_lfl_build_id),
            ]),
            SeasonsStatsWithMainReport(reserve_club, main_club, seasons, page_lfl_build_id),
            # ReserveCapMainReport(reserve_club, reserve_tournaments, main_club, main_tournaments, page_lfl_build_id),
            TextReport("(*) O-Имп (очковый импакт) вычисляется по формуле: (O/И игрока - О/И команды) * И игрока"),
        ]
        )

        report.build()

        report_dir = os.path.join(
            self._reports_dir(),
            translit(name_russian, 'ru', reversed=True).lower().translate(str.maketrans(" -", "__", "'"))
        )
        today = date.today().strftime(GithubPages.FILENAME_DATE_FORMAT)

        os.makedirs(report_dir, exist_ok=True)
        with open("{}/name.txt".format(report_dir), "w") as f:
            f.write(name_russian)
        with open("{}/{}.html".format(report_dir, today), "w") as f:
            f.write("---\n---\n")
            renderer = HtmlRenderer(f)
            report.render(renderer, 2)

    def create_index(self):
        report_dirs = self._scan_for_reports()

        with open(self._index_file(), "w") as f:
            self._append_to_index(f, report_dirs)

    def _scan_for_reports(self):
        report_dirs = []
        for subdir in os.scandir(self._reports_dir()):
            if subdir.name in [".", ".."] or not subdir.is_dir():
                continue
            report_entries = []
            for report_file in os.scandir(subdir.path):
                if (not report_file.name.endswith((".html", ".md"))):
                    continue
                report_date = datetime.strptime(
                    report_file.name.rstrip(".html").rstrip(".md"),
                    GithubPages.FILENAME_DATE_FORMAT
                )
                report_entries.append(ReportEntry(
                    os.path.relpath(report_file.path, self._index_dir()),
                    report_date
                ))
                report_entries.sort(reverse=True, key=lambda e: e.created_at)

            with open(subdir.path + "/name.txt", "r") as f:
                name = f.readline()
            if (report_entries):
                report_dirs.append(ReportDirectory(
                    name,
                    report_entries
                ))

        report_dirs.sort(reverse=True, key=lambda d: d.reports[0].created_at)
        return report_dirs

    def _append_to_index(self, file, report_dirs):
        file.write("## neon-reports\n\n")
        for dir in report_dirs:
            file.write(f"* {dir.name}\n")
            for rep in dir.reports:
                file.write(f"  * [{rep.created_at.strftime(DISPLAY_DATE_FORMAT)}]({rep.path_rel_to_index})\n")
            file.write("\n")

    def _reports_dir(self):
        return os.path.join(self.directory, "reports")

    def _index_dir(self):
        return self.directory

    def _index_file(self):
        return os.path.join(self.directory, "README.md")
