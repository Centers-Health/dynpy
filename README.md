# Dynpy

> **Dyn**amics **Py**thon Packages

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

## Quick Start

```bash
# Install packages
make install

# Run precommit on all files
make precommit

# Run tests on all packages
make test
```

### FAQ
#### How to add a dependency to a package?

```bash
cd packages/<package>
poetry add <new_dependency>
```

#### How to add a new package to the repo?
> A helper script will be forthcoming that makes this a simple process.


## Editor Setup

### VsCode (wip)
There is a `.devcontainer` for the project, but there is not yet an easy way to work with the projects from within.

### Vim / Neovim (wip)
Add a new lua module in your lua path.

```lua
local builtin = require("telescope.builtin")
local action_state = require("telescope.actions.state")
local finders = require("telescope.finders")
local vim = vim

-- Helper function to check if path is in packages directory
local function is_in_packages_dir(file_path)
	if not file_path then
		return false
	end
	return string.match(file_path, "packages/[^/]+") ~= nil
end

-- Helper function to get current package directory
local function get_current_package_dir(file_path)
	if not file_path then
		return nil
	end
	local package_path = string.match(file_path, "packages/([^/]+)")
	return package_path
end

local is_inside_work_tree = {}

-- Function to search project files
local function project_files()
	local opts = {} -- define here if you want to define something

	local cwd = vim.fn.getcwd()
	if is_inside_work_tree[cwd] == nil then
		vim.fn.system("git rev-parse --is-inside-work-tree")
		is_inside_work_tree[cwd] = vim.v.shell_error == 0
	end

	-- NOTE: for "projects" monorepo
	local current_file = vim.fn.expand("%:p")
	local package_dir = get_current_package_dir(current_file)
	if is_in_packages_dir(current_file) then
		builtin.find_files({
			prompt_title = "Files in " .. package_dir,
			cwd = vim.fn.getcwd(),
			path_display = { "smart" },
			find_command = {
				"sh",
				"-c",
				"rg --files | rg packages/" .. package_dir .. "/", -- Keep full path for file finding
			},
		})
	elseif is_inside_work_tree[cwd] then
		require("telescope.builtin").git_files(vim.tbl_deep_extend("force", opts, {
			show_untracked = true,
			-- recurse_submodules = true,
			-- Custom command to respect .gitignore but include .env
			find_command = {
				"bash",
				"-c",
				[[
        {
          git ls-files --cached --others --exclude-standard;
          git ls-files --others --exclude-standard | grep '\.env$'
        } | sort | uniq
      ]],
			},
		}))
	else
		builtin.find_files()
	end
end

-- Function to grep project files
local function grep_project_files()
	local opts = {} -- define here if you want to define something

	local cwd = vim.fn.getcwd()
	if is_inside_work_tree[cwd] == nil then
		vim.fn.system("git rev-parse --is-inside-work-tree")
		is_inside_work_tree[cwd] = vim.v.shell_error == 0
	end

	-- NOTE: for "projects" monorepo
	local current_file = vim.fn.expand("%:p")
	local package_dir = get_current_package_dir(current_file)
	if is_in_packages_dir(current_file) then
		builtin.live_grep({
			prompt_title = "Grep in " .. package_dir,
			cwd = vim.fn.getcwd(),
			search_dirs = {
				"packages/" .. package_dir,
			},
			path_display = { "smart" },
		})
	else
		builtin.live_grep({
			hidden = true,
		})
	end
end

return {
	project_files = project_files,
	grep_project_files = grep_project_files,
}
```

There are two telescope pickers from here that will search within a package if you are currently in a file from a specific package.

The way to use these is to have different mappings for full project file + grep as well in case you want to jump to a file in another package.
