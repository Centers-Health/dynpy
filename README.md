# Dynpy (Dynamics Py[thon Packages])

## Naming

Originally called this because we were a separate company called "Dynamic Healthcare Solutions" (DHS). A lot of things around here are therefore called after the dynamic name. The alternative is "CHC" (Centers Health Care).

## About

Dynpy is a python mono-repo of python packages. It allows for more easily maintaining our packages.

## History

Originally, we had a single packages called `dynamics-py`. This was a way to share code between our three code bases at the time (AR, Talent, Mentor). However, we were using semver and since there were so many python modules in one package, we had many breaking changes. It was not clear how to upgrade new projects, and the upgrade process became very harrowing, since it was not clear what needed to be upgraded.

To remedy this, we split the packages up, keeping core util packages and random stuff together in `dynamics-py-core`, while splitting out the rest of the packages. This makes it easier to understand how to upgrade breaking changes. However, there is a lot of coupling between the packages still and upgrading involved juggling a lot of PRs in one go. Using `gita` can make this more maneagable, but refactoring these packages to have reduced coupling has too much of maintenance burden of keeping all of the configuration in sync.

This mono-repo is the next step in the evolution of creating shareable code that can be used between current projects and future ones in a maintainable way. In order for this to work we created a tool `semantic-python-monorepo` which is a package inside this repo. This package has a cli program, `spm`, which is where the magic happens. Borrowing ideas from the `monodock` cli in the `docker-files` repo, we can manage our monorepo, commit to multiple packages in the same release, have downstream packages release new versions automatically when a dependency of theirs changes. This is using two poetry plugins; `poetry-bumpversion` and `poetry-plugin-mono-repo-deps`. We also handle git tagging and separate changelogs.


# Using Packages from this Repo

> Note - you need to set https://pypi.centershealthcare.org/simple as a remote python installation repository. (see the poetry docs for instructions or use the snippet below)

Put this in your project's `pyproject.toml` file

```toml
[[tool.poetry.source]]
name = "dynamics"
url = "https://pypi.centershealthcare.org/simple"
```

```bash
# In a regular python project
poetry add <package_name>
```


# Development

## Requirements

- Python 3.11
- Poetry `1.8.3`
- Pre-Commit

## Committing

Must follow Conventional Commit

https://www.conventionalcommits.org/en/v1.0.0/

Note: you do not need to use conventional commits "modules" to scope which package each commit is relevant to, `spm` will look at files changed in the commit, not the "module" (e.g. "fix(spm): a commit" and "fix: a commit" are the same)

## Editor Setup
### VsCode
### Vim
