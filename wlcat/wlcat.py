#!/usr/bin/env python3
"""
wlcat - Terminal viewer for Wolfram Language Notebooks
Similar to nbcat but for .nb files
"""

from __future__ import print_function
import argparse
import sys
import re


def print_flush(*args, **kwargs):
    """Print with immediate flush to stdout"""
    end = kwargs.pop('end', '')
    print(*args, **kwargs, end=end)
    sys.stdout.flush()


class WLcat:
    """Parser and displayer for Wolfram Language notebooks"""
    
    COMMENT = "# "
    
    def __init__(self, notebook_content: str, align: bool, pad_width: int = 16):
        """
        Args:
            notebook_content: The raw content of the .nb file
            align: Align prompt for copy
            pad_width: Padding width for prompt, when align == false
        """
        self.content = notebook_content
        self.align = align
        self.pad_width = pad_width
        self.padding = "" if align else " " * pad_width
        self.cells = []
        self._parse_notebook()
    
    def _parse_notebook(self):
        """Parse the Wolfram notebook structure"""
        # Simple parser for Wolfram notebook Cell structures
        # Pattern to match Cell[...] structures
        cell_pattern = r'Cell\[(.*?)\](?=\s*(?:,\s*Cell\[|$|\]))'
        
        # Find all Cell[...] blocks
        # We need to handle nested brackets carefully
        cells_section = self.content
        
        # Extract cells using a more robust method
        self.cells = self._extract_cells(cells_section)
    
    def _extract_cells(self, content):
        """Extract Cell structures from notebook content"""
        cells = []
        idx = 0
        while idx < len(content):
            # Find next Cell[
            cell_start = content.find('Cell[', idx)
            if cell_start == -1:
                break
            
            # Find matching closing bracket
            bracket_count = 0
            in_string = False
            escape_next = False
            cell_end = cell_start + 5  # Start after "Cell["
            
            for i in range(cell_start + 5, len(content)):
                char = content[i]
                
                if escape_next:
                    escape_next = False
                    continue
                
                if char == '\\':
                    escape_next = True
                    continue
                
                if char == '"':
                    in_string = not in_string
                    continue
                
                if not in_string:
                    if char == '[':
                        bracket_count += 1
                    elif char == ']':
                        if bracket_count == 0:
                            cell_end = i
                            break
                        bracket_count -= 1
            
            # Extract the cell content
            if cell_end > cell_start:
                cell_content = content[cell_start:cell_end + 1]
                cells.append(self._parse_cell(cell_content))
                idx = cell_end + 1
            else:
                idx = cell_start + 1
        
        return cells
    
    def _parse_cell(self, cell_str):
        """Parse a single Cell[...] structure"""
        # Extract cell content and type
        # Basic pattern: Cell[content, "type", ...]
        
        cell_data = {
            'type': 'Unknown',
            'content': '',
            'raw': cell_str
        }
        
        # Try to extract content and type
        # Remove "Cell[" and trailing "]"
        inner = cell_str[5:-1].strip()
        
        # Try to parse the first argument (content) and second argument (type)
        # This is a simplified parser
        parts = self._split_cell_args(inner)
        
        if len(parts) >= 1:
            cell_data['content'] = self._clean_cell_content(parts[0])
        
        if len(parts) >= 2:
            # Type is usually the second argument, quoted
            type_match = re.match(r'"([^"]+)"', parts[1].strip())
            if type_match:
                cell_data['type'] = type_match.group(1)
        
        return cell_data
    
    def _split_cell_args(self, inner_content):
        """Split cell arguments respecting brackets and quotes"""
        parts = []
        current_part = []
        bracket_count = 0
        in_string = False
        escape_next = False
        
        for i, char in enumerate(inner_content):
            if escape_next:
                current_part.append(char)
                escape_next = False
                continue
            
            if char == '\\':
                current_part.append(char)
                escape_next = True
                continue
            
            if char == '"':
                current_part.append(char)
                in_string = not in_string
                continue
            
            if not in_string:
                if char in '[{(':
                    bracket_count += 1
                    current_part.append(char)
                elif char in ']})':
                    bracket_count -= 1
                    current_part.append(char)
                elif char == ',' and bracket_count == 0:
                    # This is a separator at the top level
                    parts.append(''.join(current_part))
                    current_part = []
                else:
                    current_part.append(char)
            else:
                current_part.append(char)
        
        # Add the last part
        if current_part:
            parts.append(''.join(current_part))
        
        return parts
    
    def _clean_cell_content(self, content):
        """Clean and format cell content for display"""
        content = content.strip()
        
        # Remove outer quotes if present
        if content.startswith('"') and content.endswith('"'):
            content = content[1:-1]
        
        # Handle BoxData[...] wrapper
        if content.startswith('BoxData['):
            # Extract content from BoxData[...]
            box_content = content[8:-1]  # Remove "BoxData[" and "]"
            content = box_content.strip()
            # Remove quotes if present
            if content.startswith('"') and content.endswith('"'):
                content = content[1:-1]
        
        # Unescape common escape sequences
        content = content.replace('\\n', '\n')
        content = content.replace('\\t', '\t')
        content = content.replace('\\"', '"')
        content = content.replace('\\\\', '\\')
        
        return content
    
    def display(self):
        """Display the entire notebook"""
        self.show_splitline()
        for i, cell in enumerate(self.cells):
            self.display_cell(cell, i + 1)
            self.show_splitline()
        return 0
    
    def show_header(self, hdr: str):
        """Display a header"""
        hdr = f"`{hdr}`"
        left = (self.pad_width - len(hdr)) // 2
        if self.align:
            print_flush(f"{self.COMMENT}{hdr}", end='\n')
        else:
            right = self.pad_width - left - len(hdr)
            print_flush(f"{self._pad_n(left)}{hdr}{self._pad_n(right)}")
    
    def show_splitline(self):
        """Display a separator line"""
        line = "=" * 73
        print_flush(f"{self.padding}{line}", end='\n')
    
    def show_sub_splitline(self):
        """Display a sub-separator line"""
        sub_line = "-" * 73
        print_flush(f"{self.padding}{sub_line}", end='\n')
    
    @staticmethod
    def _pad_n(n):
        """Generate n spaces"""
        return ' ' * n
    
    def display_cell(self, cell, cell_number):
        """Display a single cell"""
        cell_type = cell['type']
        
        # Show header based on cell type
        if cell_type in ['Input', 'Code']:
            self.show_count(cell_number, 'In')
        elif cell_type in ['Output']:
            self.show_count(cell_number, 'Out')
        elif cell_type in ['Text', 'Title', 'Section', 'Subsection', 'Subsubsection']:
            self.show_header(cell_type)
        else:
            self.show_header(cell_type)
        
        # Display cell content
        content = cell['content']
        if content:
            lines = content.split('\n')
            pad_flag = False
            for line in lines:
                if pad_flag:
                    print_flush(f"{self.padding}")
                else:
                    pad_flag = True
                print_flush(line)
            print_flush('\n')
    
    def show_count(self, j, leading: str):
        """Display input/output counter"""
        num_str = j if j is not None else " "
        if leading == 'In':
            out = f"{leading} [{num_str}]: "
        elif leading == 'Out':
            out = f"{leading}[{num_str}]: "
        else:
            raise ValueError(f"Unknown leading {leading}.")
        
        if self.align:
            print_flush(f"{self.COMMENT}{out}", end='\n')
        else:
            print_flush(f"{self._pad_n(self.pad_width - len(out))}{out}")


def app_main(argv=None):
    """Main entry point for the wlcat command"""
    if argv is None:
        argv = sys.argv[1:]
    
    parser = argparse.ArgumentParser(
        "wlcat",
        description="Terminal viewer for Wolfram Language Notebooks"
    )
    parser.add_argument(
        "notebook",
        type=str,
        help='A Wolfram Language notebook file (*.nb).'
    )
    parser.add_argument(
        '-a', '--align',
        action='store_true',
        default=False,
        help='Align prompt (In/Out) for copy.'
    )
    args = parser.parse_args(argv)
    
    try:
        with open(args.notebook, 'r', encoding='utf-8') as fp:
            notebook_content = fp.read()
        
        wlcat = WLcat(notebook_content, align=args.align)
        return wlcat.display()
    except FileNotFoundError:
        print(f"Error: File '{args.notebook}' not found.", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(app_main())
