# wlcat roadmap and backlog

Planning-only document. It records prioritized, evidence-backed work candidates for
`wlcat`; nothing here is approved implementation, and no candidate carries an
`overnight-approved` label. Evidence was collected on 2026-10-21 against `main`
at commit `e31288a`, using Python 3.11 and only the repository's own examples plus
one local real-world notebook.

Current shape of the project: one 316-line module (`wlcat/wlcat.py`), a legacy
`setup.py`, three example notebooks, and no test suite or CI. The parser is a
hand-rolled scanner over the notebook text. The candidates below are ordered by
user-visible impact per unit of work.

## 1. Parse `CellGroupData` cells instead of collapsing them (highest priority)

**Evidence.** Grouped cells are the standard structure for section cells that own
children. The minimal input
`Notebook[{Cell[CellGroupData[{Cell["S","Section"],Cell["1+1","Input"]},Open]]}]`
is parsed as a single `Unknown` cell whose content is the raw `CellGroupData[...]`
expression; the `Section` type and the inner `Input` cell are both lost. The same
failure scales up: a 37 KB real notebook with 22 `Cell[` occurrences and 8
`Cell[CellGroupData` groups parsed as 2 cells, both type `Unknown`. The current
`_extract_cells` scan counts only square brackets from the outer `Cell[`, so the
inner cell list is treated as one unbalanced argument.

**Proposed change.** Teach the extractor about `CellGroupData[{...}, state]`:
either descend into the group and emit its child cells, or emit one cell that
keeps the group's own type. Pick one behavior, document it in the README.

**Acceptance criteria.**
- A fixture with a grouped `Section` cell reports the section header and each
  child cell with correct type and content.
- A nested group (group inside group) terminates and does not swallow the rest
  of the notebook.
- A notebook with no groups produces byte-identical output to today's version
  for the three existing examples.
- New tests run offline in under 5 seconds.

## 2. Add a regression test suite and fixtures (enables every other item)

**Evidence.** `git ls-files` shows no `tests/`, no `pytest` configuration, no
`.github/workflows`, and `setup.py` declares no test dependencies. All current
behavior, including the defects in items 1, 4 and 5, is unguarded. The README
documents exact expected output for one small notebook, which is a usable
starting golden file.

**Proposed change.** Add `tests/` with `pytest`, fixtures under `tests/fixtures/`
copying the shipped examples plus focused edge-case notebooks, and one golden
output file per fixture for `--align` off and on. Keep it dependency-light and
offline.

**Acceptance criteria.**
- `python -m pytest -q` passes from a clean checkout with only the project plus
  `pytest` installed.
- Each defect fixed in items 1, 3, 4 and 5 has a test that fails before the fix.
- The suite runs in CI-agnostic form (no network, no Wolfram installation).

## 3. Render box expressions as readable source

**Evidence.** `examples/complex.nb` is the repository's own edge-case notebook,
and its `Input`/`Output` cells display raw box trees, for example
`RowBox[{"f", "[", RowBox[{"x", ",", "y"}], "]"}]`. The README promises a
"readable format" and an "aligned mode for easy copy-pasting"; pasting a `RowBox`
tree is neither. `examples/example.nb` only looks correct because its boxes are
plain strings.

**Proposed change.** Add a documented, deliberately small box-to-text renderer
covering `RowBox`, `BoxData`, `StringJoin`-style flat lists, and quoted strings;
fall back to the raw expression for anything unrecognized rather than guessing.

**Acceptance criteria.**
- The `complex.nb` fixture renders `f[x, y]` and `Map[f, {1, 2, 3}]` as readable
  single-line expressions.
- Unsupported box forms are emitted verbatim, and the README lists the supported
  subset and the fallback rule.
- Golden tests cover at least one nested `RowBox`, one quoted string containing
  a comma, and one unsupported form.

## 4. Decode Wolfram string escapes correctly

**Evidence.** `_clean_cell_content` unescapes by sequential `str.replace` calls in
the order `\n`, `\t`, `\"`, then `\\`. Because `\n` runs before `\\` is collapsed,
a notebook string containing a literal backslash followed by `n` is corrupted.
Reproduction: the cell text `a\\nb` (two backslashes then `n` in the notebook
source) becomes the characters `a`, backslash, newline, `b` instead of
`a`, backslash, `n`, `b`. The same path mangles the shipped `complex.nb`, where
`StringLength["Hello\nWorld"]` is displayed across two lines.

**Proposed change.** Replace the ordered `replace` chain with a single
left-to-right unescaper that consumes one escape at a time, or move unescaping to
a small helper with a truth table in tests.

**Acceptance criteria.**
- A table-driven test covers `\n`, `\t`, `\"`, `\\`, `\\n`, `\\t`, and a trailing
  escaped backslash.
- `complex.nb` shows `StringLength["Hello\nWorld"]` on one line.
- No double-unescaping: input that contains no backslash is unchanged.

## 5. Fail loudly on input that is not a notebook

**Evidence.** Running the CLI on a plain text file exits 0 and prints a single
separator line with no cells (90 bytes of output, empty stderr apart from a
`runpy` warning caused by `python -m wlcat.wlcat`). A user or script cannot tell
a malformed `.nb` from an empty notebook.

**Proposed change.** Validate that the file contains a `Notebook[` expression
before parsing; on failure print a one-line error to stderr and return a nonzero
exit status. Keep `FileNotFoundError` behavior as is.

**Acceptance criteria.**
- A non-notebook file and an empty file each produce a nonzero exit status and a
  single actionable stderr line.
- Well-formed notebooks, including the three examples, are unaffected.
- Tests assert exit status and stderr content, not full prose.

## Non-goals for this roadmap

- No new CLI surface beyond what items 3-5 require; stdin, paging, and notebook
  rendering to HTML are out of scope.
- No dependency on Wolfram Engine or `wolframscript`; the tool's value is
  parsing without them.
- No packaging modernization (`pyproject.toml`, version single-sourcing) is
  proposed here. It is worth doing, but it does not change user-visible output
  and should follow the test suite in item 2.
