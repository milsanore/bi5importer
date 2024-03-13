# STANDARD
from unittest import mock
from typing import List
# 3RD PART
import asyncio
import asyncpg
import pytest
# LOCAL
from . import bi5consumer
from .bi5struct import Bi5Struct

@pytest.mark.asyncio
@pytest.mark.timeout(60)
async def test_consumer():
	"""integration test for consuming from the queue
	"""
	# CONCRETE QUEUE
	queue = asyncio.Queue()
	await queue.put(Bi5Struct("AUDSGD", 2020, 1, 1, 1, "./test_data/AUDSGD/2007/02/14/04h_ticks.bi5"))
	await queue.put(Bi5Struct("AUDSGD", 2020, 1, 1, 1, "./test_data/AUDSGD/2007/02/14/05h_ticks.bi5"))
	await queue.put(Bi5Struct("AUDSGD", 2020, 1, 1, 1, "./test_data/AUDSGD/2007/02/14/06h_ticks.bi5"))
	# MOCK DB - RECORD
	mock_record = mock.create_autospec(asyncpg.Record)
	mock_record.get.side_effect = [
		# [instrument id, point value]
		999, 1,
		999, 1,
		999, 1,
	]
	# MOCK DB - CONNECTION
	mock_db_conn = mock.create_autospec(asyncpg.Connection)
	mock_db_conn.fetchrow.return_value = mock_record
	# MOCK DB - CONNECTION POOL
	mock_db_conn_pool = mock.create_autospec(asyncpg.pool.Pool)
	mock_db_conn_pool.acquire.return_value.__aenter__.return_value = mock_db_conn

	processed_file_paths: List[str] = []
	def on_file_processed(file_path: str):
		nonlocal processed_file_paths
		processed_file_paths.append(file_path)

	asyncio.create_task(
		bi5consumer.consume_bi5_data(
			"test_consumer",
			queue,
			mock_db_conn_pool,
			on_file_processed
		),
		name="test_consumer"
	)

	await queue.join()
	assert processed_file_paths == [
		"./test_data/AUDSGD/2007/02/14/04h_ticks.bi5",
		"./test_data/AUDSGD/2007/02/14/05h_ticks.bi5",
		"./test_data/AUDSGD/2007/02/14/06h_ticks.bi5",
	]

# TODO: ASSERT DB CALL PAYLOAD
