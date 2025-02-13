# dynamics-py-selenium

A Dynamics python library with selenium utilities

# Installing

> Note - you need to set https://pypi.centershealthcare.org/simple as a remote python installation repository. (see the poetry docs for instructions or use the snippet below)

Put this in your project's `pyproject.toml` file

```toml
[[tool.poetry.source]]
name = "dynamics"
url = "https://pypi.centershealthcare.org/simple"
```

```bash
# In a regular python project
poetry add dynpy_selenium

# If using `dm`
dm poetry add dynpy_selenium
```

# Contributing to this repository

## Getting setup

Just open the folder in vscode and launch in the dev container. Then run a make install and you should be good to go!

## Committing

Must follow Conventional Commit. Please read [this](https://www.conventionalcommits.org/en/v1.0.0/).
