import math

from dynpy.enums import RoundingDirection


def round_to_int(num: int, nearest: int, direction: RoundingDirection = None):
    """
    Round a number to the nearest x (10, 100, etc)
    Can optionally pass a rounding direction (Up or Down)
    """
    if direction == RoundingDirection.UP:
        round_method = math.ceil
    elif direction == RoundingDirection.DOWN:
        round_method = math.floor
    else:
        round_method = round
    return int(round_method(num / nearest)) * nearest
