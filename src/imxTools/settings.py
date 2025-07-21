from pathlib import Path

from imxInsights.utils.singleton import SingletonMeta


class Config(metaclass=SingletonMeta):
    def __init__(
        self,
        add_comments: bool = False,
        issue_list_sheet_name: str = "comments",
    ):
        self.ROOT_PATH = Path(__file__).resolve().parent.parent
        self.ISSUE_LIST_SHEET_NAME = issue_list_sheet_name
        self.ADD_COMMENTS = add_comments

    def reset(self):
        self.__init__()  # Reset to default values


config = Config()
