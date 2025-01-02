# dynamics-py-actions

A Dynamics python library for decoupling forms from views.

The Actions module enables update / create behavior (form behavior) to
be be added to any view and not be coupled with that view. The behavior
is handled by the action and does not need to be implemented in the view.

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
poetry add dynpy_actions

# If using `dm`
dm poetry add dynpy_actions
```

Then add `dynpy_actions` and `dynpy_js` to your INSTALLED_APPS.

```python
INSTALLED_APPS = [
    ...
    "dynpy_actions",
    "dynpy_js",
    "dynpy_forms",
]
```

# Contributing to this repository

## Getting setup


Just open the folder in vscode and launch in the dev container
Then run a `make install` and you should be good to go!

## Committing

Must follow Conventional Commit
https://www.conventionalcommits.org/en/v1.0.0/
