from __future__ import annotations

import os


def repo_root() -> str:
    # src/gymchallenge/data_paths.py -> repo root is two levels up
    return os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))


def data_dir() -> str:
    return os.path.join(repo_root(), "data")


def exports_dir() -> str:
    return os.path.join(repo_root(), "exports")


def data_path(filename: str) -> str:
    return os.path.join(data_dir(), filename)


def exports_path(filename: str) -> str:
    return os.path.join(exports_dir(), filename)
