# wlcat

`wlcat` is a command-line tool for viewing Wolfram Language notebook files (`.nb`) in the terminal. It parses the notebook's underlying structure and displays it in a readable format without requiring Wolfram Mathematica or wolframscript to be installed.

Inspired by [nbcat](https://github.com/zhifanzhu/nbcat) for Jupyter notebooks.

## Features

- 📖 View Wolfram Language notebooks directly in the terminal
- 🚀 No Wolfram Mathematica or wolframscript required
- 🎨 Clean, formatted output with cell type indicators
- 📋 Aligned mode for easy copy-pasting
- 🔍 Parse various cell types (Input, Output, Text, Section, etc.)

## Installation

```bash
pip install git+https://github.com/JuanG970/wlcat.git
```

Or install from source:

```bash
git clone https://github.com/JuanG970/wlcat.git
cd wlcat
pip install -e .
```

## Usage

Basic usage:

```bash
wlcat notebook.nb
```

With aligned prompt for easy copying:

```bash
wlcat notebook.nb -a
```

### Command-line Options

- `notebook`: Path to the Wolfram Language notebook file (`.nb`)
- `-a, --align`: Align prompt (In/Out) for easy copy-pasting

## Example

Given a Wolfram Language notebook `example.nb`:

```wolfram
Notebook[{
Cell["Example Notebook", "Title"],
Cell["Calculate 2 + 2", "Text"],
Cell[BoxData["2 + 2"], "Input"],
Cell[BoxData["4"], "Output"]
}]
```

Running `wlcat example.nb` will output:

```
=========================================================================
    `Title`     Example Notebook
                =========================================================================
     `Text`     Calculate 2 + 2
                =========================================================================
        In [3]: 2 + 2
                =========================================================================
        Out[4]: 4
                =========================================================================
```

Running `wlcat example.nb -a` will output:

```
=========================================================================
# `Title`
Example Notebook
=========================================================================
# `Text`
Calculate 2 + 2
=========================================================================
# In [3]: 
2 + 2
=========================================================================
# Out[4]: 
4
=========================================================================
```

## Supported Cell Types

- **Input/Code**: Wolfram Language code cells
- **Output**: Result cells
- **Text**: Plain text cells
- **Title**: Title cells
- **Section/Subsection/Subsubsection**: Section headers
- And other Wolfram notebook cell types

## How It Works

`wlcat` parses the Wolfram Language expression structure of `.nb` files:

1. Reads the notebook file as plain text
2. Parses the `Notebook[{Cell[...], ...}]` structure
3. Extracts cell content and type information
4. Formats and displays cells in the terminal

Unlike tools that require Wolfram software, `wlcat` works by directly parsing the notebook file format, making it lightweight and fast.

## Examples

See the `examples/` directory for sample notebooks to try with `wlcat`.

## Limitations

- Complex cell structures with heavy nesting may not parse perfectly
- Binary data and special formatting may not display correctly
- Graphics and images are shown as code/references, not rendered visually

## Uninstall

```bash
pip uninstall wlcat
```

## License

Distributed under the MIT License. See `LICENSE` file for more information.

## Acknowledgments

- Inspired by [nbcat](https://github.com/zhifanzhu/nbcat) by zhifanzhu
- Built for the Wolfram Language community
