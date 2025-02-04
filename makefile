SHELL:=/bin/bash
PACKAGES := $(wildcard packages/*/)

install:
	pre-commit install -t pre-commit -t pre-push -t commit-msg --overwrite
	poetry self add poetry-bumpversion
	poetry self add poetry-plugin-mono-repo-deps

ci: install
	pre-commit run --show-diff-on-failure --color=always --all-files --hook-stage push
	@for PACKAGE in $(PACKAGES); do \
		(cd $$PACKAGE && \
			echo ">> $$PACKAGE"&& \
			poetry lock --no-update &&  \
			poetry --directory $$PACKAGE install && \
			poetry --directory $$PACKAGE run python -m pytest -n 2 -m "not skipci" -ra -q --disable-warnings --tb=long \
		); \
	done

# TODO: Implement
# build:
# 	@for PACKAGE in $(PACKAGES); do \
# 		(cd $$PACKAGE && \
# 			echo ">> $$PACKAGE"&& \
# 			poetry --directory $$PACKAGE run python -m pytest -n 2 -ra -q --disable-warnings --tb=long \
# 		); \
# 	done
# TODO: Implement
# publish:
# 	@for PACKAGE in $(PACKAGES); do \
# 		(cd $$PACKAGE && \
# 			echo ">> $$PACKAGE"&& \
# 			poetry --directory $$PACKAGE run python -m pytest -n 2 -ra -q --disable-warnings --tb=long \
# 		); \
# 	done

clean:
	rm -rf .venv || echo

.PHONY: test ci install clean
