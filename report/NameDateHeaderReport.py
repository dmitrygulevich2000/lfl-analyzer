from datetime import date

from .Report import Report
from render import Renderer
from Util import *


class NameDateHeaderReport(Report):
    def __init__(self, name, club):
        self.name = name
        self.club = club

    def build(self):
        pass

    def render(self, renderer: Renderer, level=1):
        today = date.today()
        name_href = renderer.get_href(self.name, build_club_url(self.club))
        renderer.heading(f"{name_href} {today.strftime(DISPLAY_DATE_FORMAT)}", level)
