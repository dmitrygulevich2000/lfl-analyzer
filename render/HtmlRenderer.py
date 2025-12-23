import pandas as pd

from .MdRenderer import MdTag
from .Renderer import Renderer, TagContextManager


class HtmlRenderer(Renderer):
    def __init__(self, file):
        self.file = file

    def heading(self, line: str, level: int):
        assert (level <= 6)
        with self.tag(f"h{level}"):
            self.file.write(line)

    def text(self, text: str):
        with self.tag("p"):
            self.file.write(text)

    def pd_table(self, df: pd.DataFrame, *, sortable: bool = False, sticky_column: bool = False):
        self.file.write("\n")
        classes = []
        if sortable:
            classes += ["sortable"]
        if sticky_column:
            classes += ["sticky-column"]

        df.to_html(self.file,
                   index=False,
                   escape=False,
                   border=0,
                   classes=classes,
                   header=True
                   )
        self.file.write("\n")

    def tag(self, tag: str, props=dict()) -> TagContextManager:
        return HtmlTag(self.file, self, tag, props)
    
    def get_line_break(self) -> str:
        return "<br>"

    def get_href(self, text: str, url: str) -> str:
        return f"<a href=\"{url}\">{text}</a>"

    def get_bold(self, text: str) -> str:
        return f"<b>{text}</b>"


class HtmlTag(TagContextManager):
    def __init__(self, file, renderer, tag, props):
        self.file = file
        self.renderer = renderer
        self.tag = tag

        self.props = props
        assert (not any(["\"" in val for val in self.props.values()]))

    def __enter__(self) -> None:
        props_str = " ".join([f"{key}=\"{value}\"" for (key, value) in self.props.items()])
        if props_str:
            props_str = " " + props_str
        self.file.write(f"\n<{self.tag}{props_str}>\n")
        return None

    def __exit__(self, type, value, traceback):
        self.file.write(f"\n</{self.tag}>\n")
        return None
