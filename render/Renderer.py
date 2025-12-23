import pandas as pd


class TagContextManager:
    def __enter__(self) -> None:
        pass

    def __exit__(self, type, value, traceback):
        pass


class Renderer:
    def heading(self, line: str, level: int):
        pass

    def text(self, text: str):
        pass

    def pd_table(self, df: pd.DataFrame, *, sortable: bool = False, sticky_column: bool = False):
        pass

    def tag(self, tag: str, props=dict()) -> TagContextManager:
        pass

    def get_line_break(self) -> str:
        pass

    def get_href(self, text: str, url: str) -> str:
        pass

    def get_bold(self, text: str) -> str:
        pass
