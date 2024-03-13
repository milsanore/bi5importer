#!/usr/bin/env python

"""script for importing data from dukascopy bi5 files into a postgres database;
this is the main function
"""
# STANDARD
import asyncio
import itertools
import logging
import os
# 3RD PARTY
import asyncpg
import click
import dotenv
import pyfiglet
import tqdm
# LOCAL
import src.bi5producer
import src.bi5consumer

# LOGGING
class TqdmLoggingHandler(logging.Handler):
	def __init__(self, level=logging.NOTSET):
		super().__init__(level)

	def emit(self, record):
		try:
			msg = self.format(record)
			tqdm.tqdm.write(msg)
			self.flush()
		except (KeyboardInterrupt, SystemExit):
			raise
		except:
			self.handleError(record)
logging.basicConfig(
	format="%(asctime)s.%(msecs)03d %(levelname)-8s %(message)s",
	level=logging.INFO,
	datefmt="%Y-%m-%d %H:%M:%S"
)
log = logging.getLogger(__name__)
log.addHandler(TqdmLoggingHandler())


# PROGRESS BAR
_input_file_count = 0
_progress_bar: tqdm.tqdm = None
_processed_file_count = itertools.count()
def _on_sucess(file_path: str):
	global _progress_bar, _processed_file_count, _input_file_count
	next(_processed_file_count)
	if not _progress_bar:
		_progress_bar = tqdm.tqdm(total=_input_file_count)
	_progress_bar.update(1)
	_progress_bar.set_description(file_path)


# APP HARNESS
PRODUCER_COUNT = 1
async def _init(path: str, consumer_count: int):
	# INIT APP
	global _input_file_count
	dotenv.load_dotenv()
	db_pool = await asyncpg.create_pool(
		host=os.getenv("DB_HOST"),
		port=os.getenv("DB_PORT"),
		user=os.getenv("DB_USER"),
		password=os.getenv("DB_PASSWORD"),
		database=os.getenv("DB_NAME"),
		min_size=min(consumer_count, 10),
		server_settings={
			"application_name": __file__,
		},
	)
	# BEGIN WORK
	queue: asyncio.Queue = asyncio.Queue()
	_input_file_count = await src.bi5producer.produce_bi5_data(path, queue)
	consumers = [
		asyncio.create_task(
			src.bi5consumer.consume_bi5_data(f"consumer_{i}", queue, db_pool, _on_sucess),
			name=f"consumer_{i}"
		)
		for i in range(1, consumer_count + 1)
	]
	await queue.join()
	# # CONVERT queue.join() TO A FULL-FLEDGED TASK, SO WE CAN TEST WHETHER IT'S DONE,
	# # WAIT FOR THE QUEUE TO COMPLETE OR ONE OF THE CONSUMERS TO EXIT
	# queue_complete = asyncio.create_task(queue.join())
	# await asyncio.wait([queue_complete, *consumers], return_when=asyncio.FIRST_COMPLETED)
	# if queue_complete.done():
	# 	for item_consumer in consumers:
	# 		item_consumer.cancel()
	# else:
	# 	# IF THE QUEUE HASN'T COMPLETED, IT MEANS ONE OF THE CONSUMERS HAS RAISED.
	# 	# FIND IT AND PROPAGATE THE EXCEPTION.
	# 	# YOU CAN ALSO USE item_consumer.exception() TO GET THE EXCEPTION OBJECT.
	# 	# CANCELING OTHER TASKS IS ANOTHER POSSIBILITY.
	# 	for item_consumer in consumers:
	# 		if item_consumer.done():
	# 			# THIS WILL RAISE
	# 			item_consumer.result()


# CLI
@click.command()
@click.option(
	"--path",
	required=True,
	help="path to an entire instrument directory, containing bi5 files")
@click.option(
	"--consumers",
	type=int,
	default=1,
	help="number of consumers")
@click.option(
	"--debug",
	is_flag=True,
	default=False,
	help="enable debug mode")
def _main(path: str, consumers: int, debug: bool):
	"""script for importing data from dukascopy bi5 files into a postgres database,
	"""
	print(pyfiglet.figlet_format("bi5importer"))
	log.info("PATH\t\t[%s]", path)
	log.info("CONSUMERS\t[%d]", consumers)
	log.info("debug\t\t[%r]", debug)
	# START EVENT LOOP
	logging.info(asyncio.run(_init(path, consumers), debug=debug))
	logging.info("SHUTTING DOWN")
	if _progress_bar:
		_progress_bar.close()

# NB: THE SUBPROCESSES WILL IMPORT (I.E. EXECUTE) THE MAIN MODULE AT START;
# YOU NEED TO INSERT AN `if __name__ == '__main__':` GUARD IN THE MAIN MODULE
# IN ORDER TO AVOID CREATING SUBPROCESSES RECURSIVELY
if __name__ == "__main__":
	# pylint: disable=no-value-for-parameter
	_main()
