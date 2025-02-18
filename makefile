SHELL:=/bin/bash
PACKAGES := $(wildcard packages/*/)

define PRE_COMMIT_RULE
	pre-commit run --show-diff-on-failure --color=always --all-files
endef

define TEST_RULE
	@for PACKAGE in $(PACKAGES); do \
		(cd $$PACKAGE && \
			echo ">> $$PACKAGE"&& \
			poetry --directory $$PACKAGE run python -m pytest -n 2 -m "not skipci" -ra -q --disable-warnings --tb=long \
		); \
	done
endef

lock:
	@for PACKAGE in $(PACKAGES); do \
		(cd $$PACKAGE && \
			echo ">> $$PACKAGE"&& \
			poetry lock --no-update  \
		); \
	done

install: lock
	pre-commit install -t pre-commit -t pre-push -t commit-msg --overwrite
	poetry self add poetry-bumpversion
	poetry self add poetry-plugin-mono-repo-deps
	@for PACKAGE in $(PACKAGES); do \
		(cd $$PACKAGE && \
			echo ">> $$PACKAGE"&& \
			poetry --directory $$PACKAGE install \
		); \
	done

ci: install
	$(PRE_COMMIT_RULE)
	$(TEST_RULE)

precommit:
	$(PRE_COMMIT_RULE)

test:
	$(TEST_RULE)
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

.PHONY: test ci install lock clean
