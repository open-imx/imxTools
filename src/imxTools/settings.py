from pathlib import Path
from datetime import datetime

from imxInsights.utils.singleton import SingletonMeta


class Config(metaclass=SingletonMeta):
    def __init__(
        self,
        add_comments: bool = False,
        set_metadata_parents: bool = False,
        add_timestamp: bool = False,
        issue_list_sheet_name: str = "comments",
    ):
        self.ROOT_PATH = Path(__file__).resolve().parent.parent
        self.ADD_COMMENTS = add_comments
        self.SET_METADATA_PARENTS = set_metadata_parents
        self.ADD_TIMESTAMP = add_timestamp
        self.TIMESTAMP = datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")
        self.ISSUE_LIST_SHEET_NAME = issue_list_sheet_name

    def reset(self):
        self.__init__()  # Reset to default values


config = Config()
