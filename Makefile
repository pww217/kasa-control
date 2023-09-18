SHELL := /bin/bash -o pipefail -o errexit

dev :
	uvicorn webhook:app --host localhost --port 8008 --reload

run :
	python server.py

build :
	docker build .

build-web:
	docker build -f Dockerfile.webhook .
