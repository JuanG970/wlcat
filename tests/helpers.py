"""Shared helpers: in-process CLI runner, fixture and golden path lookups."""
import io
import os
from contextlib import redirect_stderr, redirect_stdout

from wlcat import app_main

HERE = os.path.dirname(os.path.abspath(__file__))
FIXTURES = os.path.join(HERE, 'fixtures')
ROOT = os.path.dirname(HERE)


def fixture(*parts):
    """Absolute path to a file under tests/fixtures."""
    return os.path.join(FIXTURES, *parts)


def golden(name):
    """Text of a golden file under tests/fixtures/golden."""
    with open(fixture('golden', name), encoding='utf-8') as fp:
        return fp.read()


def run_cli(*argv):
    """Run app_main(argv) with captured streams; return (status, stdout, stderr)."""
    out, err = io.StringIO(), io.StringIO()
    with redirect_stdout(out), redirect_stderr(err):
        status = app_main(list(argv))
    return status, out.getvalue(), err.getvalue()
