# dynamics-py-pyjs
A python package containing shared JS for django projects

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
poetry add dynpy_js
```

Then add `dynpy_js` to your INSTALLED_APPS.

```python
INSTALLED_APPS = [
    ...
    "dynpy_js",
]
```

# Contributing to this repository

## Getting setup

Just open the folder in vscode and launch into dev container.
Then run `make install` and you should be good to go

# Open your editor
code . # if using vscode
```

## Committing

Must follow Conventional Commit
https://www.conventionalcommits.org/en/v1.0.0/
