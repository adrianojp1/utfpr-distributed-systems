all: up clean install run

run: activate
	python -m gunicorn app:app --worker-class gevent --bind localhost:8000

clean:
	rm -rf __pycache__

up:
	docker compose up -d

install: venv activate
	python -m pip install -r requirements.txt

venv:
	python -m pip install virtualenv
	python -m venv .venv

activate:
	. .venv/bin/activate
