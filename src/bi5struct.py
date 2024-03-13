"""
struct describing a bi5 file
"""
from typing import NamedTuple

class Bi5Struct(NamedTuple):
	"""
	struct describing a bi5 file
	"""
	instrument: str
	year: int
	month: int
	day: int
	hour: int
	path: str
