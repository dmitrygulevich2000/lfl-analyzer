import pandas as pd

from .Renderer import Renderer, TagContextManager


class MdRenderer(Renderer):
    def __init__(self, file):
        self.file = file

    def heading(self, line: str, level: int):
        self.file.write("\n" + level*"#" + f" {line}\n")

    def text(self, text: str):
        self.file.write(f"\n{text}\n")

    def pd_table(self, df: pd.DataFrame, *, sortable: bool = False, sticky_column: bool = False):
        self.file.write("\n")
        df.to_markdown(
            self.file,
            index=False,
            tablefmt="github"
        )
        self.file.write("\n")

    def get_line_break(self) -> str:
        return " "

    def tag(self, tag: str, props=dict()) -> TagContextManager:
        return MdTag(self.file, self, tag, props)

    def get_href(self, text: str, url: str) -> str:
        return f"[{text}]({url})"

    def get_bold(self, text: str) -> str:
        return f"**{text}**"


class MdTag(TagContextManager):
    def __init__(self, file, renderer, tag, props):
        self.file = file
        self.renderer = renderer
        self.tag = tag

        self.props = props
        self.props["markdown"] = "1"
        assert (not any(["\"" in val for val in self.props.values()]))

    def __enter__(self) -> None:
        props_str = " ".join([f"{key}=\"{value}\"" for (key, value) in self.props.items()])
        self.file.write(f"\n<{self.tag} {props_str}>\n")
        return None

    def __exit__(self, type, value, traceback):
        self.file.write(f"\n</{self.tag}>\n")
        return None
