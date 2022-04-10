import enum


class ReplyType(enum.Enum):
    none = 0
    reaction = 1
    reactionTemp = 2
    message = 3
