import sys
from enum import Enum
from functools import cache

if sys.version_info >= (3, 11):
    from enum import StrEnum
else:

    class StrEnum(str, Enum):
        pass


class ColumnEnum(StrEnum):
    """
    Base Enum class for column definitions with human-readable labels.
    Provides utility methods to convert between enum names, values, and members.
    """

    def __str__(self):
        """
        Return the name of the enum member when converted to a string.

        Example:
            str(CommentColumns.comment) -> 'comment'
        """
        return self.name

    def __repr__(self):
        """
        Return a detailed representation of the enum member, showing both name and value.

        Example:
            repr(CommentColumns.comment) -> "<CommentColumns.comment: 'Comment content'>"
        """
        return f"<{self.__class__.__name__}.{self.name}: {self.value}>"

    @classmethod
    def description_to_header(cls) -> dict[str, str]:
        """
        Return a mapping from human-readable labels (enum values) to enum member names.

        Example:
            {'Full object path in IMX structure': 'object_path'}
        """
        return cls._description_to_header_cached(cls)

    @classmethod
    def header_to_description(cls) -> dict[str, str]:
        """
        Return a mapping from enum member names to human-readable labels (values).

        Example:
            {'object_path': 'Full object path in IMX structure'}
        """
        return cls._header_to_description_cached(cls)

    @classmethod
    def description_to_member(cls) -> dict[str, "ColumnEnum"]:
        """
        Return a mapping from human-readable labels (values) to enum members.

        Example:
            {'Full object path in IMX structure': CommentColumns.object_path}
        """
        return cls._description_to_member_cached(cls)

    @classmethod
    def to_dict(cls) -> dict[str, str]:
        """
        Return a mapping of enum member names to their human-readable labels.

        Useful for exporting or serializing enum definitions.

        Example:
            {'object_path': 'Full object path in IMX structure'}
        """
        return cls._to_dict_cached(cls)

    @classmethod
    def from_description(cls, label: str, ignore_case: bool = False) -> "ColumnEnum":
        """
        Return the enum member corresponding to a given human-readable label.

        Args:
            label: The human-readable label to look up.
            ignore_case: Whether to ignore case when comparing labels.

        Returns:
            The corresponding enum member.

        Raises:
            ValueError: If no matching label is found.

        Example:
            CommentColumns.from_description("Comment content") -> CommentColumns.comment
        """
        for col in cls:
            if (ignore_case and str(col.value).lower() == label.lower()) or str(
                col.value
            ) == label:
                return col
        raise ValueError(f"No column found for label: {label}")

    @classmethod
    def headers(cls) -> list[str]:
        """
        Return a list of all enum member names.

        Example:
            ['object_path', 'comment', 'value']
        """
        return [col.name for col in cls]

    @classmethod
    def names(cls) -> list[str]:
        """
        Alias for `headers()`. Returns the names of enum members.

        Example:
            ['object_path', 'comment', 'value']
        """
        return cls.headers()

    @classmethod
    def from_name(cls, name: str) -> "ColumnEnum":
        """
        Return the enum member corresponding to a given member name.

        Args:
            name: The enum member name to look up.

        Returns:
            The corresponding enum member.

        Raises:
            ValueError: If no matching name is found.

        Example:
            CommentColumns.from_name("comment") -> CommentColumns.comment
        """
        try:
            return cls[name]
        except KeyError:
            raise ValueError(f"No column found for name: {name}")

    @staticmethod
    @cache
    def _description_to_header_cached(enum_cls) -> dict[str, str]:
        return {str(col.value): col.name for col in enum_cls}

    @staticmethod
    @cache
    def _header_to_description_cached(enum_cls) -> dict[str, str]:
        return {col.name: str(col.value) for col in enum_cls}

    @staticmethod
    @cache
    def _description_to_member_cached(enum_cls) -> dict[str, "ColumnEnum"]:
        return {str(col.value): col for col in enum_cls}

    @staticmethod
    @cache
    def _to_dict_cached(enum_cls) -> dict[str, str]:
        return {col.name: str(col.value) for col in enum_cls}
