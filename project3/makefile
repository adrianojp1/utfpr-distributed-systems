PYTHON=python3
VENV=../.venv

all: up clean install run

run: activate
	$(PYTHON) -m gunicorn app:app --worker-class gevent --bind localhost:8000

clean:
	rm -rf __pycache__

up:
	docker compose up -d

install: venv activate
	$(PYTHON) -m pip install -r requirements.txt

venv:
	$(PYTHON) -m pip install virtualenv
	$(PYTHON) -m venv $(VENV)

activate:
	. $(VENV)/bin/activate
