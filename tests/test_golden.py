"""Golden output for both display modes, plus the shipped examples."""
import os

import pytest

from helpers import ROOT, fixture, golden, run_cli


def _lines(text):
    return [line.rstrip() for line in text.splitlines()]


@pytest.mark.parametrize('name,flags,suffix', [
    ('readme', [], '.txt'),
    ('readme', ['-a'], '.align.txt'),
    ('edge', [], '.txt'),
    ('edge', ['-a'], '.align.txt'),
])
def test_output_matches_golden(name, flags, suffix):
    status, out, err = run_cli(fixture(name + '.nb'), *flags)
    assert (status, err) == (0, '')
    # Trailing spaces are ignored: align mode pads every '# In [n]: ' header.
    assert _lines(out) == _lines(golden(name + suffix))


@pytest.mark.parametrize('name,cells', [('example.nb', 17), ('complex.nb', 12)])
def test_shipped_examples_still_parse(name, cells):
    status, out, err = run_cli(os.path.join(ROOT, 'examples', name))
    assert (status, err) == (0, '')
    assert out.count('=' * 73) == cells + 1
