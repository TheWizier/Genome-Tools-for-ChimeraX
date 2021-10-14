from enum import IntEnum


class BedColourMode(IntEnum):
    SINGLE, SCORE, COLOUR = range(3)


class BedSelectMode(IntEnum):
    RANGE, RANGE_STRICT, START, MIDDLE, END = range(5)