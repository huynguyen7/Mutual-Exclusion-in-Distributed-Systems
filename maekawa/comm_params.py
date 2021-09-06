from enum import Enum


''' COMMUNICATION PARAMS '''


# Voting states.
class State(Enum):
    RELEASED = 0
    HELD = 1
    WANTED = 2


# Message types.
class Message(Enum):
    REQUEST = 0
    REPLY = 1
    RELEASE = 2
