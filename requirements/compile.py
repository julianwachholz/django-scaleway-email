#!/usr/bin/env python
from __future__ import annotations

import os
import subprocess
import sys
from functools import partial
from pathlib import Path

if __name__ == "__main__":
    os.chdir(Path(__file__).parent)
    common_args = [
        "uv",
        "pip",
        "compile",
        "--quiet",
        "--generate-hashes",
        "--constraint",
        "-",
        "requirements.in",
        *sys.argv[1:],
    ]
    run = partial(subprocess.run, check=True)

    run(
        [
            *common_args,
            "--python",
            "3.10",
            "--output-file",
            "py310-django52.txt",
        ],
        input=b"Django>=5.2,<6.0",
    )
    run(
        [
            *common_args,
            "--python",
            "3.11",
            "--output-file",
            "py311-django52.txt",
        ],
        input=b"Django>=5.2,<6.0",
    )
    run(
        [
            *common_args,
            "--python",
            "3.12",
            "--output-file",
            "py312-django52.txt",
        ],
        input=b"Django>=5.2,<6.0",
    )
    run(
        [
            *common_args,
            "--python",
            "3.13",
            "--output-file",
            "py313-django52.txt",
        ],
        input=b"Django>=5.2,<6.0",
    )
    run(
        [
            *common_args,
            "--python",
            "3.14",
            "--output-file",
            "py314-django52.txt",
        ],
        input=b"Django>=5.2,<6.0",
    )
    run(
        [
            *common_args,
            "--python",
            "3.12",
            "--output-file",
            "py312-django60.txt",
        ],
        input=b"Django>=6.0,<6.1",
    )
    run(
        [
            *common_args,
            "--python",
            "3.13",
            "--output-file",
            "py313-django60.txt",
        ],
        input=b"Django>=6.0,<6.1",
    )
    run(
        [
            *common_args,
            "--python",
            "3.14",
            "--output-file",
            "py314-django60.txt",
        ],
        input=b"Django>=6.0,<6.1",
    )
    run(
        [
            *common_args,
            "--python",
            "3.12",
            "--output-file",
            "py312-django61.txt",
        ],
        input=b"Django>=6.1,<6.2",
    )
    run(
        [
            *common_args,
            "--python",
            "3.13",
            "--output-file",
            "py313-django61.txt",
        ],
        input=b"Django>=6.1,<6.2",
    )
    run(
        [
            *common_args,
            "--python",
            "3.14",
            "--output-file",
            "py314-django61.txt",
        ],
        input=b"Django>=6.1,<6.2",
    )
