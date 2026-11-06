"""Regression tests for CellGroupData handling. Offline, stdlib-only."""

import io
import os
import unittest
from contextlib import redirect_stdout

from wlcat import app_main
from wlcat.wlcat import WLcat

FIXTURES = os.path.join(os.path.dirname(__file__), 'fixtures')


def _load(name):
    with open(os.path.join(FIXTURES, name), 'r', encoding='utf-8') as fp:
        return fp.read()


class CellGroupTest(unittest.TestCase):
    def test_grouped_section_reports_header_and_children(self):
        cells = WLcat(_load('grouped.nb'), align=False).cells
        self.assertEqual([c['type'] for c in cells], ['Section', 'Input'])
        self.assertEqual([c['content'] for c in cells], ['S', '1+1'])

    def test_nested_group_terminates_and_keeps_following_cells(self):
        cells = WLcat(_load('nested_grouped.nb'), align=False).cells
        self.assertEqual(
            [(c['type'], c['content']) for c in cells],
            [('Section', 'Outer'), ('Subsection', 'Inner'),
             ('Input', 'x = 1'), ('Text', 'after'), ('Text', 'tail')])

    def test_empty_group_yields_no_cells_and_no_swallow(self):
        notebook = 'Notebook[{Cell[CellGroupData[{}, Open]],Cell["tail", "Text"]}]'
        cells = WLcat(notebook, align=False).cells
        self.assertEqual([(c['type'], c['content']) for c in cells],
                         [('Text', 'tail')])

    def test_ungrouped_cells_are_unchanged(self):
        notebook = 'Notebook[{Cell["Title", "Title"],Cell[BoxData["2+2"], "Input"]}]'
        cells = WLcat(notebook, align=False).cells
        self.assertEqual([(c['type'], c['content']) for c in cells],
                         [('Title', 'Title'), ('Input', '2+2')])

    def test_cli_renders_grouped_cells(self):
        out = io.StringIO()
        with redirect_stdout(out):
            status = app_main([os.path.join(FIXTURES, 'grouped.nb')])
        text = out.getvalue()
        self.assertEqual(status, 0)
        self.assertIn('`Section`', text)
        self.assertIn('In [2]: ', text)
        self.assertIn('1+1', text)
        self.assertNotIn('CellGroupData', text)


if __name__ == '__main__':
    unittest.main()
