"""script for importing data from dukascopy bi5 files into a postgres database
"""
# STANDARD
import asyncio
import datetime
import decimal
import logging
import lzma
import os
import struct
from typing import Callable
# 3RD PARTY
import asyncpg
# LOCAL
from .bi5struct import Bi5Struct

logging.basicConfig(
	format="%(asctime)s.%(msecs)03d %(levelname)-8s %(message)s",
	level=logging.INFO,
	datefmt="%Y-%m-%d %H:%M:%S"
)
log = logging.getLogger(__name__)

DATA_FORMAT = ">3I2f"

# PUBLIC

async def consume_bi5_data(
		consumer_name: str,
		queue: asyncio.Queue,
		db_pool: asyncpg.pool.Pool,
		on_file_processed: Callable[[str], None],
	) -> None:
	"""pick jobs off a queue, and push data to a database
	Keyword arguments:
	consumer_name 	-- the name of an individual consumer instance
	queue 			-- asyncio queue object from which the consumer will retrieve data
	db_pool			-- database connection pool
	"""
	log.info("STARTING CONSUMER, NAME [%s]", consumer_name)
	while True:
		item_bi5: Bi5Struct = await queue.get()
		# VALIDATION
		if os.path.getsize(item_bi5.path) <= 0:
			queue.task_done()
			on_file_processed(item_bi5.path)
			continue
		# GET THE INSTRUMENT ID FROM THE DATABASE
		async with db_pool.acquire() as db_conn:
			instrument_query = (await db_conn.fetchrow(
				"SELECT id, point_value FROM instruments WHERE instrument_name = $1",
				item_bi5.instrument,
				timeout=60,
			))
			instrument_id = instrument_query.get("id")
			point_value = decimal.Decimal(instrument_query.get("point_value"))
		# BUILD ARRAY OF TUPLES FROM FILE
		chunk_size = struct.calcsize(DATA_FORMAT)
		records = []
		with lzma.open(item_bi5.path) as bi5_file:
			while True:
				chunk = bi5_file.read(chunk_size)
				if chunk:
					bi5_row = struct.unpack(DATA_FORMAT, chunk)
					records.append((
						instrument_id,
						datetime.datetime(
							item_bi5.year,
							item_bi5.month,
							item_bi5.day,
							item_bi5.hour,
						) + datetime.timedelta(milliseconds=bi5_row[0]),
						decimal.Decimal(bi5_row[1]) * point_value,
						decimal.Decimal(bi5_row[2]) * point_value,
						decimal.Decimal(bi5_row[3]),
						decimal.Decimal(bi5_row[4]),
					))
				else:
					break
		# PUSH TO DB
		async with db_pool.acquire() as db_conn:
			await db_conn.copy_records_to_table(
				table_name="price_history",
				records=records,
				columns=("id_instrument", "date", "ask", "bid", "ask_volume", "bid_volume"),
				timeout=60,
			)
		queue.task_done()
		on_file_processed(item_bi5.path)
		# "GRACEFULLY" KILL THE CONSUMER
		if queue.empty():
			break
