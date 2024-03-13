# BEST PRACTICES

- unit tests
- do we need `setup.py` / setuptools?
	- `python_requires='>3.5.2',`
- git hooks (python package?)
- static type checker
	- http://mypy-lang.org
	- https://code.visualstudio.com/docs/python/linting#_mypy
- gitlab badges

# PERFORMANCE

- error handling
	- if the `conn.copy_records_to_table()` operation throws exception, the app freezes instead of crashing
	- i need to get better at handling errors in asynchronous functions, i guess
- adjust column `CHECK` operations to confirm bid < ask
- profiling
- use `PYTHONASYNCIODEBUG`
- db query performance is slow, may need individual indexes instead of just the composite unique
- how to gracefully kill consumers (equivalent of closing channels in go)?
	- right now, the queue must be filled before consumers are started,
	- that way, when the queue is empty, we know we're done
