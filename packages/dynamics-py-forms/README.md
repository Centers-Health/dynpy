# dynamics-py-forms

A Dynamics python library for sharing django forms, widgets, etc...

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
poetry add dynpy_forms

# If using `dm`
dm poetry add dynpy_forms
```

Then add `dynpy_forms` to your INSTALLED_APPS.

```python
INSTALLED_APPS = [
    ...
    "dynpy",
    "dynpy_forms",
]
```

Finally add `django.__path__[0] + "/forms/templates",` to "DIRS" in  TEMPLATES

```python
TEMPLATES = (
    {
        "DIRS": [
            ...
            django.__path__[0] + "/forms/templates",
        ],
    }
)
```

# Contributing to this repository

## Getting setup

Just open the folder in vscode and launch in the dev container.
Then run a 'make install' and you should be good to go!
## Committing

Must follow Conventional Commit
https://www.conventionalcommits.org/en/v1.0.0/

WARNING: `refactor` will NOT create a package version bump.
