import subprocess

import pytest


@pytest.fixture(scope="session")
def root_dir(tmp_path_factory):
    return tmp_path_factory.mktemp("root_dir")


@pytest.fixture(scope="session")
def origin_dir(root_dir):
    origin_dir = root_dir / "origin.git"
    origin_dir.mkdir()
    return origin_dir


@pytest.fixture(scope="session")
def work_dir(root_dir):
    work_dir = root_dir / "work"
    work_dir.mkdir()
    return work_dir


@pytest.fixture(scope="session")
def with_repos(origin_dir, work_dir):
    subprocess.run(["git", "init", "--bare"], cwd=origin_dir)
    subprocess.run(["git", "init", "--initial-branch", "master"], cwd=work_dir)
    subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=work_dir)
    subprocess.run(["git", "config", "user.name", "Test User"], cwd=work_dir)

    subprocess.run(["git", "remote", "add", "origin", str(origin_dir)], cwd=work_dir)

    subprocess.run(["touch", "README.md"], cwd=work_dir)
    subprocess.run(["git", "add", "README.md"], cwd=work_dir)
    subprocess.run(["git", "commit", "-m", "Initial commit"], cwd=work_dir)

    subprocess.run(["git", "push", "--set-upstream", "origin", "master"], cwd=work_dir)


@pytest.fixture(scope="session")
def with_packages(origin_dir, work_dir, with_repos):
    packages_dir = work_dir / "packages"
    packages_dir.mkdir()

    def create_new_package(package_name: str, dependencies: list[str] = None):
        subprocess.run(
            [
                "poetry",
                "new",
                f"--name={package_name}",
                "--src",
                "--no-interaction",
                f"packages/{package_name}",
            ],
            cwd=work_dir,
        )
        subprocess.run(
            [
                "poetry",
                "-C",
                str(packages_dir / package_name),
                "config",
                "virtualenvs.in-project",
                "true",
                "--local",
            ],
            cwd=work_dir,
        )
        subprocess.run(
            [
                "poetry",
                "-C",
                packages_dir / package_name,
                "config",
                "repositories.test-repository",
                "https://pypi.localhost/simple/",
                "--local",
            ],
            cwd=work_dir,
        )
        subprocess.run(
            [
                "poetry",
                "-C",
                packages_dir / package_name,
                "env",
                "use",
                "python3.11",
            ],
            cwd=work_dir,
        )
        subprocess.run(
            ["poetry", "-C", str(packages_dir / package_name), "install", "--quiet", "--no-interaction"],
            cwd=work_dir,
        )
        if dependencies:
            import toml

            for dep in dependencies:
                toml_file = packages_dir / package_name / "pyproject.toml"
                with open(toml_file) as f:
                    pyproject_data = toml.load(f)

                # Add the new dependency
                pyproject_data["tool"]["poetry"]["dependencies"][dep] = {
                    "path": f"../{dep}",
                    "develop": True,
                }
                # Write back to the file
                with open(toml_file, "w") as f:
                    toml.dump(pyproject_data, f)

        subprocess.run(["git", "add", "."], cwd=work_dir)
        subprocess.run(["git", "commit", "-m", f"feat: add {package_name}"], cwd=work_dir)

    create_new_package("app1")
    create_new_package("app2", ["app1"])
    subprocess.run(["cp", "-R", ".", str(packages_dir / "semantic-python-monorepo")])
    # subprocess.run(["tree", "-L", "3"], cwd=work_dir)


@pytest.fixture
def spm(work_dir):
    def spm_run(cmd: list[str]):
        result = subprocess.run(
            ["poetry", "-C", work_dir / "packages" / "semantic-python-monorepo", "run", "spm"] + cmd,
            cwd=work_dir,
            capture_output=True,
            encoding="utf-8",
        )
        import re

        # 7-bit C1 ANSI sequences
        ansi_escape = re.compile(
            r"""
            \x1B  # ESC
            (?:   # 7-bit C1 Fe (except CSI)
                [@-Z\\-_]
            |     # or [ for CSI, followed by a control sequence
                \[
                [0-?]*  # Parameter bytes
                [ -/]*  # Intermediate bytes
                [@-~]   # Final byte
            )
        """,
            re.VERBOSE,
        )
        result = ansi_escape.sub("", result.stdout)
        return result

    class SPM:
        @staticmethod
        def run(cmd: list[str]):
            return spm_run(cmd)

        @staticmethod
        def analyze():
            return spm_run(["--analyze"])

        @staticmethod
        def registry():
            return spm_run(["--registry"])

    return SPM
