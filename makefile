SHELL:=/bin/bash
PACKAGES := $(wildcard packages/*/)

# TODO: Add these features into SPM. This is lowest priority since it would
# complicate ci. But a fully robust monorepo tool should encompass this
# behavior. Also, it make be helpful for dev as well.

define INSTALL_PACKAGES
	@for PACKAGE in $(PACKAGES); do \
		(cd $$PACKAGE && \
			echo ">> $$PACKAGE"&& \
			poetry --directory $$PACKAGE install \
		); \
	done
endef

define PRE_COMMIT_RULE
	pre-commit run --show-diff-on-failure --color=always --all-files
endef

define TEST_RULE
	@for PACKAGE in $(PACKAGES); do \
		echo ">> $$PACKAGE"; \
		pushd $$PACKAGE; \
		poetry run python -m pytest -n 2 -m "not skipci" -ra -q --disable-warnings --tb=long; \
		popd; \
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
	$(INSTALL_PACKAGES)

install-ci:
	$(INSTALL_PACKAGES)

ci: install
	$(PRE_COMMIT_RULE)
	$(TEST_RULE)

precommit:
	git config --global --add safe.directory /app
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
#
new_package:
	copier copy ./new_package_template/ packages/

clean:
	rm -rf .venv || echo

.PHONY: test ci install lock clean
