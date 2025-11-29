from typing import List

from render import Renderer


class Report:
    def build(self):
        pass

    def render(self, renderer: Renderer, level=1):
        pass


class SequenceReport(Report):
    def __init__(self, *, header: Report = None, reports: List[Report]):
        self.header = header
        self.reports = reports

    def build(self):
        if self.header is not None:
            self.header.build()
        for r in self.reports:
            r.build()

    def render(self, renderer, level=1):
        if self.header is not None:
            self.header.render(renderer, level)
        for r in self.reports:
            r.render(renderer, level + int(self.header is not None))


class ColumnsReport(Report):
    def __init__(self, report_left: Report, report_right: Report):
        self.report_left = report_left
        self.report_right = report_right

    def build(self):
        self.report_left.build()
        self.report_right.build()

    def render(self, renderer: Renderer, level=1):
        with renderer.tag("div", {"class": "columns-report"}):
            with renderer.tag("div"):
                self.report_left.render(renderer, level)

            with renderer.tag("div"):
                self.report_right.render(renderer, level)


class HeaderReport(Report):
    def __init__(self, line):
        self.line = line

    def build(self):
        pass

    def render(self, renderer: Renderer, level=1):
        renderer.heading(self.line, level)


class TextReport(Report):
    def __init__(self, text):
        self.text = text

    def build(self):
        pass

    def render(self, renderer: Renderer, level=1):
        renderer.text(self.text)
