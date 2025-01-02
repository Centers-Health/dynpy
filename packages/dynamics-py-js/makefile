SHELL:=/bin/bash

install:
	pre-commit install -t pre-commit -t pre-push -t commit-msg --overwrite
	poetry install

ci: install
	pre-commit run --show-diff-on-failure --color=always --all-files --hook-stage push

test: install
	poetry run pytest -n 2 -ra -q --disable-warnings --tb=long

clean:
	rm -rf .venv || echo

.PHONY: test ci install clean
