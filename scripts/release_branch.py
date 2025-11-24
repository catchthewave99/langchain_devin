"""
python scripts/release_branch.py anthropic bagatur
"""

import glob
import subprocess
import sys

# Ignoring errors since this script is run in a controlled environment
import toml  # type: ignore # pyright: ignore[reportMissingModuleSource]
import tomllib  # type: ignore # pyright: ignore[reportMissingImports]


def main(*args):
    pkg = args[1]
    if len(args) >= 2:
        user = args[2]
    else:
        user = "auto"
    for path in glob.glob("./libs/**/pyproject.toml", recursive=True):
        if pkg in path:
            break

    try:
        with open(path, "rb") as f:
            pyproject = tomllib.load(f)
    except (FileNotFoundError, IOError, OSError, tomllib.TOMLDecodeError) as e:
        print(f"Error: Could not read pyproject.toml from {path}: {e}")
        return
    major, minor, patch = pyproject["tool"]["poetry"]["version"].split(".")
    patch = str(int(patch) + 1)
    bumped = ".".join((major, minor, patch))
    pyproject["tool"]["poetry"]["version"] = bumped
    try:
        with open(path, "w") as f:
            toml.dump(pyproject, f)
    except (IOError, OSError) as e:
        print(f"Error: Could not write to {path}: {e}")
        return

    branch = f"{user}/{pkg}_{bumped.replace('.', '_')}"
    try:
        subprocess.run(
            ["git", "checkout", "-b", branch],
            capture_output=True,
            text=True,
            check=True,
        )
        subprocess.run(
            ["git", "commit", "-am", f"{pkg}[patch]: Release {bumped}"],
            capture_output=True,
            text=True,
            check=True,
        )
        result = subprocess.run(
            ["git", "push", "-u", "origin", branch],
            capture_output=True,
            text=True,
            check=True,
        )
        print(result)
    except subprocess.CalledProcessError as e:
        print(f"Error running git commands: {e}")
        if e.stderr:
            print(f"Git error output: {e.stderr}")
        return


if __name__ == "__main__":
    main(*sys.argv)
