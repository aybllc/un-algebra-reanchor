PY?=python3

setup:
	$(PY) -m pip install --upgrade pip
	$(PY) -m pip install -e . -r requirements.txt

test:
	$(PY) -m pytest

demo:
	$(PY) scripts/make_synthetic.py --out data/demo.csv
	unreanchor run --data data/demo.csv --config configs/config.sample.yaml --out reports

run:
	unreanchor run --data $(DATA) --config $(CONFIG) --out $(OUT)

docker-build:
	docker build -t un-algebra-reanchor:0.1.0 .

docker-run:
	docker run --rm -v $$PWD:/work -w /work un-algebra-reanchor:0.1.0 \
		unreanchor run --data data/demo.csv --config configs/config.sample.yaml --out /work/reports

lint:
	$(PY) -m pip install ruff || true
	ruff check src || true
