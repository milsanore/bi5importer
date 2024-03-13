# STANDARD
from typing import List
# 3RD PARTY
import asyncio
import pytest
# LOCAL
from . import bi5producer
from .bi5struct import Bi5Struct

@pytest.mark.asyncio
@pytest.mark.timeout(60)
async def test_producer_parallel():
	await producer(parallel=True)

@pytest.mark.asyncio
@pytest.mark.timeout(60)
async def test_producer_serial():
	await producer(parallel=False)

async def producer(parallel: bool):
	"""integration test for publishing to the queue in parallel
	"""
	queue = asyncio.Queue()
	file_count = await bi5producer.produce_bi5_data("./test_data/AUDSGD", queue, parallel=parallel)

	# ASSSERT CONTENTS OF THE QUEUE
	bi5_structs: List[Bi5Struct] = []
	for _ in range(file_count):
		item_bi5: Bi5Struct = await queue.get()
		bi5_structs.append(item_bi5)
		queue.task_done()
	await queue.join()

	assert bi5_structs == [
		Bi5Struct("AUDSGD", 2007, 2, 14, 4, "./test_data/AUDSGD/2007/02/14/04h_ticks.bi5"),
		Bi5Struct("AUDSGD", 2007, 2, 14, 5, "./test_data/AUDSGD/2007/02/14/05h_ticks.bi5"),
		Bi5Struct("AUDSGD", 2007, 2, 14, 6, "./test_data/AUDSGD/2007/02/14/06h_ticks.bi5"),
	]
