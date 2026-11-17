"""Cell content decoding: string escapes (roadmap item 4) and box rendering
(roadmap item 3).

The strict xfail rows encode intended behaviour that the current parser does not
deliver. They are expected failures today; once item 3 or 4 lands each one turns
into XPASS and fails loudly, which is the signal to drop its marker.
"""
import pytest

from wlcat.wlcat import WLcat


def cell_content(cell_source):
    """Content of the first cell in a one-cell notebook."""
    return WLcat('Notebook[{' + cell_source + '}]', align=False).cells[0]['content']


def wl_string(text):
    return cell_content('Cell[BoxData["%s"], "Input"]' % text)


@pytest.mark.parametrize('source,expected', [
    ('abc', 'abc'),
    ('a\\nb', 'a\nb'),
    ('a\\tb', 'a\tb'),
    ('say \\"hi\\"', 'say "hi"'),
    ('a\\\\b', 'a\\b'),
    ('a\\\\', 'a\\'),
])
def test_escapes_decode_once(source, expected):
    assert wl_string(source) == expected


@pytest.mark.xfail(strict=True, reason='roadmap item 4: \\\\n decoded twice')
@pytest.mark.parametrize('source,expected', [
    ('a\\\\nb', 'a\\nb'),
    ('a\\\\tb', 'a\\tb'),
])
def test_literal_backslash_before_letter(source, expected):
    assert wl_string(source) == expected


@pytest.mark.xfail(strict=True, reason='roadmap item 3: boxes not rendered')
@pytest.mark.parametrize('boxes,readable', [
    ('RowBox[{"f", "[", RowBox[{"x", ",", "y"}], "]"}]', 'f[x,y]'),
    ('RowBox[{"Map", "[", RowBox[{"f", ",", RowBox[{"{", RowBox[{"1", ",", "2",'
     ' ",", "3"}], "}"}]}], "]"}]', 'Map[f,{1,2,3}]'),
])
def test_rowbox_renders_as_readable_source(boxes, readable):
    rendered = cell_content('Cell[BoxData[%s], "Input"]' % boxes)
    assert 'RowBox' not in rendered
    assert rendered.replace(' ', '') == readable
