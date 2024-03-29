# BI5 IMPORTER

<!-- Pytest Coverage Comment:Begin -->
<a href="https://github.com/milsanore/bi5importer/blob/master/README.md"><img alt="Coverage" src="https://img.shields.io/badge/Coverage-97%25-brightgreen.svg" /></a>
<!-- Pytest Coverage Comment:End -->

a tool for bulk importing bi5 files (tick data) into sql

## PREREQUISITES
- `python3`
- `make`
- postgresql (run `make db` to get a containerised DB)
- `pg_config`

## INIT
1. copy `.env.example` to `.env`
2. create a pg database, and configure credentials in `.env`
3. run `make init`

## RUN
`make run`

## TEST
`make lint`
`make test` (and google the "Coverage Gutters" vscode plugin for a pretty ui)

## INSTALL ADDITIONAL DEPENDENCIES
1. `pip install some_new_package`
2. `pip freeze > requirements.txt`
3. commit `requirements.txt` to source control

## ADDING A DB MIGRATION
`yoyo new ./db_migrations -m "your message"`

## CONCURRENCY
1. loop over files, place them in a queue (one instrument at a time)
2. pick off queue, using a worker pool
3. save files to DB

```mermaid
graph TB
file-reader-->queue
queue-->worker1[worker 1]
queue-->worker2[worker 2]
queue-->workerN[... worker N]
worker1-->db[(Database)]
worker2-->db
workerN-->db
```
