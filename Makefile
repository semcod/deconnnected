.PHONY: install test scan
install:
	python -m pip install -e ".[dev,gui]"
	playwright install chromium
test:
	pytest
scan:
	deconnected scan . --out .deconnected/graph.json
	deconnected report .deconnected/graph.json
