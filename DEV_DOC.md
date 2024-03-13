.venv				stores a local copy of python and all dependencies
.vscode				developer specific vscode config files
db_migrations		database "migration" scripts automatically configure the database (tables/columns/etc)
test_data			sample bi5 files
.env				developer specific environment variables (does NOT go to source control)
.env.example		lists environment variables the app will expect to exist in order to work (goes to source control)
.gitignore			lists all the files git will ignore
.style.yapf			configuration file for the autoformatter, yapf
bi5importer.py		app entry point
DEV_DOC.md			-
LICENSE				the most important file in the app
Makefile			the scripts that the `make` command will use, used to configure the app
pylintrc			configuration file for the linter, pylint
README.md			-
requirements.txt	lists all dependencies that pip will install when we call `make init`
TODO.md				-
yoyo.ini			configuration file for the database migration engine, yoyo
