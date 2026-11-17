"""CLI contract: bad input must fail loudly (roadmap item 5)."""
import pytest

from helpers import fixture, run_cli


def test_missing_file_reports_an_error():
    status, _, err = run_cli(fixture('does-not-exist.nb'))
    assert status == 1
    assert err.strip().startswith("Error: File '")


@pytest.mark.xfail(strict=True, reason='roadmap item 5: non-notebook exits 0')
@pytest.mark.parametrize('name', ['plain.txt', 'empty.nb'])
def test_non_notebook_input_fails_loudly(name):
    status, _, err = run_cli(fixture(name))
    assert status != 0
    assert len([line for line in err.splitlines() if line.strip()]) == 1
