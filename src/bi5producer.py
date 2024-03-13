"""script for parsing a bi5 file tree and pushing bi5 jobs on a queue
"""
# STANDARD
import asyncio
from concurrent.futures import ProcessPoolExecutor
import logging
import math
import multiprocessing
import os
import re
from typing import List
# LOCAL
from .bi5file import Bi5File
from .bi5struct import Bi5Struct

logging.basicConfig(
	format="%(asctime)s.%(msecs)03d %(levelname)-8s %(message)s",
	level=logging.INFO,
	datefmt="%Y-%m-%d %H:%M:%S"
)
log = logging.getLogger(__name__)

FILE_EXTENSION = "bi5"
_filename_regex = re.compile("^(?P<hour>\\d{2})h_ticks\\.bi5$")
_year_regex = re.compile("^\\d{4}$")
_month_regex = re.compile("^\\d{2}$")
_day_regex = re.compile("^\\d{2}$")

# PUBLIC

async def produce_bi5_data(path: str, queue: asyncio.Queue, parallel=True) -> int:
	"""find all .bi5 files in a directory and create jobs
	Keyword arguments:
	path 		-- path to the directory containing bi5 files
	queue 		-- asyncio queue object onto which the function will push data
	parallel 	-- select serial or multiprocess operation
	"""
	bi5_files: List[Bi5File] = []
	_find_files_by_extension(path, FILE_EXTENSION, bi5_files)
	bi5_structs: List[Bi5Struct] = []
	if not parallel:
		bi5_structs = _build_bi5_structs(bi5_files)
	else:
		# SPLIT ARRAY OF FILE PATHS INTO BATCHES
		count_files = len(bi5_files)						# e.g. 106,000
		count_batches = multiprocessing.cpu_count()			# e.g. 6
		batch_size = math.ceil(count_files / count_batches)	# e.g. 17,667 (rounded up)
		batches = []
		for item_batch_index in range(count_batches): 		# e.g. 0...5
			batches.append(bi5_files[						# e.g. 0...17,667 (but the end index is exclusive)
				item_batch_index * batch_size :				# e.g. all the way to 88,335...106,000
				min((item_batch_index + 1) * batch_size, count_files)
			])
		with ProcessPoolExecutor() as executor:
			for item_results in executor.map(_build_bi5_structs, batches, timeout=30):
				bi5_structs += item_results

	bi5_structs = sorted(
		bi5_structs,
		key=lambda x: [x.instrument, x.year, x.month, x.day, x.hour]
	)
	file_count = len(bi5_structs)
	log.info("PROCESSING FILES, COUNT [%s]", file_count)
	for item_bi5 in bi5_structs:
		await queue.put(item_bi5)
	return file_count

# PRIVATE

def _find_files_by_extension(path: str, extension: str, out_results: List[Bi5File]):
	for item_file in os.scandir(path):
		if item_file.is_dir():
			_find_files_by_extension(item_file.path, extension, out_results)
		elif item_file.is_file():
			if len(item_file.name) > 4 and item_file.name[-4:] == ("." + extension):
				out_results.append(Bi5File(item_file.path, item_file.name))

def _build_bi5_structs(files: List[Bi5File]) -> List[Bi5Struct]:
	results = []
	for item_file in files:
		# GET PATH CHUNKS
		norm_path = os.path.normpath(item_file.path)
		_, path_and_file = os.path.splitdrive(norm_path)
		path, folder = os.path.split(path_and_file)
		folders = []
		while True:
			path, folder = os.path.split(path)
			if folder != "":
				folders.append(folder)
			else:
				if path != "":
					folders.append(path)
				break
		# VALIDATE AND BUILD RESULT
		matches = _filename_regex.match(item_file.name)
		if (len(folders) > 3
			and matches
			and _year_regex.match(folders[2])
			and _month_regex.match(folders[1])
			and _day_regex.match(folders[0])
			and matches.group("hour")
		):
			results.append(Bi5Struct(
				instrument=folders[3],
				year=int(folders[2]),
				month=int(folders[1]),
				day=int(folders[0]),
				hour=int(matches.group("hour")),
				path=item_file.path
			))
		else:
			log.warning("FILE SKIPPED, PATH [%s]", item_file.path)
	return results
