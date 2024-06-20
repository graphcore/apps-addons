#!/usr/bin/env python3
# Copyright (c) 2023 Graphcore Ltd. All rights reserved.
import argparse
import re
import warnings

from importlib import metadata
from typing import List, Optional, Sequence

import requirements
from requirements.requirement import Requirement

GIT_URI_PATTERN = r"(?:.+ @ )?(git\+.*)"


def manual_parse_named_git(req_line: str):
    """
    Workaround for mis-handling of named git repo lines in requirements files by requirement-parser.
    Parses the repo path, removes the name if present, and creates a new requirement, which can then
    be checked as normal.

    Assumes it's receiving a git repo path from a requirements file and assumes that checks
    for non-git lines have been carried out prior to this. If it receives something that's not
    a git repo, it'll return False.
    """
    m = re.match(GIT_URI_PATTERN, req_line)

    if m is None:
        return False

    new_req = Requirement.parse(m[1])
    return is_valid_req(new_req)


def is_valid_req(r: Requirement) -> bool:
    if "req: unpinned" in r.line:
        return True

    if r.specs and r.specs[0][0] in ["==", "~="]:
        return True

    if r.uri and r.revision:
        return True

    # Requirements parser doesn't properly parse named requirements coming from git repos,
    # It'll read the name/optionals, but not the git URI, which then makes it looked like
    # otherwise fine dependencies haven't been pinned.
    # The backup plan is to identify these with regex and manually extract the git URI, then
    # use that to check for pinning.
    if r.name and not r.uri:
        return manual_parse_named_git(r.line)

    return False


def recommend_version_if_possible(package_name: str) -> Optional[str]:
    try:
        version_installed = metadata.version(package_name)
        print(f"Found version {version_installed} for '{package_name}'")
        return f"{package_name}~={version_installed}"
    except metadata.PackageNotFoundError:
        print(f"Failed to find package '{package_name}' - skipping")
        return None


def try_write_fixed_requirements(invalid: List[Requirement], filename: str):
    has_updated = False

    with open(filename) as fh:
        lines = fh.readlines()

    invalid_dict = {i.name: i for i in invalid}

    for idx, line in enumerate(lines):
        print(line)
        try:
            # Hide the error that comes from requirements parser not handing --find-links, etc.
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                r = Requirement.parse(line)
            if r.name in invalid_dict and r.name is not None:
                new_version = recommend_version_if_possible(r.name)
                if new_version:
                    print(f"    Setting {r.name} version {new_version}")
                    lines[idx] = f"{new_version}\n"
                    has_updated = True
                else:
                    print(f"    Could not get version... Skipping.")
        except ValueError:
            pass

    if has_updated:
        with open(filename, "w") as fh:
            for l in lines:
                fh.write(l)
    return has_updated


def invalid_requirements(filename: str, fix_it: bool) -> bool:
    with open(filename) as fh:
        # Hide the error that comes from requirements parser not handing --find-links, etc.
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            reqs = [r for r in requirements.parse(fh)]
        f = [r for r in reqs if not is_valid_req(r)]

    if f:
        print(f"Unpinned requirements found in file {filename}")

    if fix_it and f:
        print(f"  Attempting to fix...")
        try_write_fixed_requirements(f, filename)

    return f


def main(argv: Optional[Sequence[str]] = None, fix_issues: bool = True) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("filenames", nargs="*")
    args = parser.parse_args(argv)

    exit_code = 0
    for filename in args.filenames:
        try:
            invalid = invalid_requirements(filename, fix_issues)
            if invalid:
                exit_code = 1
        except FileNotFoundError:
            print(f"Could not find requirements file: {filename}")
            exit_code = 2
        except Exception as err:
            print(f"Could not parse requirements file: {filename}")
            print(err)
            exit_code = 3
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
