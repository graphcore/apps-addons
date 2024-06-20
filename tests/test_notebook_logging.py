# Copyright (c) 2022 Graphcore Ltd. All rights reserved.
from pathlib import Path
import sys
import subprocess
import copy

import pytest

from examples_utils.benchmarks import notebook_utils
from examples_utils.benchmarks.run_benchmarks import process_notebook_to_command

TEST_DIRECTORY = Path(__file__).resolve().parent


def test_notebook_is_not_logged():
    notebook_path = TEST_DIRECTORY / "test_files/notebook_without_logging.ipynb"
    std_streams = notebook_utils.run_notebook(notebook_path, notebook_path.parent)
    assert "the execution of this cell is not logged" in std_streams
    assert (
        "Graphcore would like to collect information about the applications and code being run in this notebook"
        not in std_streams
    )
    assert isinstance(std_streams, str)


def test_notebook_is_logged():
    notebook_path = TEST_DIRECTORY / "test_files/notebook_with_logging.ipynb"
    std_streams = notebook_utils.run_notebook(notebook_path, notebook_path.parent)
    assert "the execution of this cell is logged" in std_streams
    assert (
        "Graphcore would like to collect information about the applications and code being run in this notebook"
        in std_streams
    )
    assert isinstance(std_streams, str)
