.PHONY: run check imports tree clean

run:
	python main.py

check:
	python main.py

imports:
	grep -R "from android_agent\." -n android_agent

tree:
	tree -I "__pycache__|.git|.venv"

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

ingest:
	python ingest_knowledge.py knowledge/android11
venv:
	source .venv/bin/activate && python --version
