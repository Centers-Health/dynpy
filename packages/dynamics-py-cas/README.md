# dynamics-py-cas

A Dynamics python library for single sign on

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
poetry add dynpy_cas

# If using `dm`
dm poetry add dynpy_cas
```

Then add `dynpy_cas` to your INSTALLED_APPS.

```python
INSTALLED_APPS = [
    ...
    "dynpy_cas",
]
```


# Contributing to this repository


## Getting setup

Just open the folder in vscode and launch in the dev container.
Then run a `make install` and you should be good to go!!

## Committing

Must follow Conventional Commit
https://www.conventionalcommits.org/en/v1.0.0/
