"""
Five Nights at Rocket - Enumerations
Contains all enum classes used throughout the game
"""

from enum import Enum


class GameState(Enum):
    """Enumeration of possible game states"""
    MENU = 1
    PLAYING = 2
    CAMERA = 3
    PAUSED = 4
    GAME_OVER = 5
    VICTORY = 6
    TUTORIAL = 7
    SLACKING = 8
    WORKING = 9


class RoomType(Enum):
    """Enumeration of room types in the game"""
    OFFICE = "Office"
    BREAK_ROOM = "Break Room"
    MEETING_ROOM = "Meeting Room"
    CLASSROOM = "Classroom"
    HALLWAY = "Hallway"


class Direction(Enum):
    """Enumeration for movement directions (x, y)"""
    UP = (0, -1)
    DOWN = (0, 1)
    LEFT = (-1, 0)
    RIGHT = (1, 0)


class InteractableType(Enum):
    """Enumeration of interactable object types"""
    REFRIGERATOR = "refrigerator"
    CABINET = "cabinet"
    CAMERA = "camera"
    LAPTOP = "laptop"
    DESK = "desk"
    DOOR = "door"
