from setuptools import setup

with open('requirements.txt') as f:
	requirements = f.read().splitlines()

# WHAT ABOUT PYTHON MIN VERSION?

setup(
	name='dataloader',
	version='0.1',
	py_modules=['dataloader'],
	install_requires=requirements,
	entry_points='''
		[console_scripts]
		dataloader=dataloader:cli
	''',
)
