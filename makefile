install:
	pip install -r requirements.txt
	pip install black flake8 isort pytest

clean:
	black .
	isort . --profile black
	flake8 . --ignore=F401,E501,E203,W503,E402,W605

clear:
	find . -name '__pycache__' | xargs rm -r -f
	find . -name 'DS_Store' | xargs rm -f
	find . -name '.pytest_cache' | xargs rm -r -f