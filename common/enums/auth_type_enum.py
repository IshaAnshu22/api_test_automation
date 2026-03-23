from enum import Enum, auto


class AuthTypeEnum(Enum):

    BEARER = auto()
    API_TOKEN = auto()
    BASIC = auto()