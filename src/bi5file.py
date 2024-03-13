"""
struct describing a bi5 file
"""
from typing import NamedTuple

class Bi5File(NamedTuple):
	"""
	struct describing the subset of a os.DirEntry object
	"""
	path: str
	name: str
