.PHONY: build
.PHONY: run

build:
  BUILDKIT=1 docker build . 

run:
  uvicorn webhook:app --reload
