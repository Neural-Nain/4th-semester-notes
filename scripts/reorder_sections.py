#!/usr/bin/env python3
"""Reorder <section id="..."> blocks in topic HTML files. Does not delete content."""
import re
import sys
from pathlib import Path

SECTION_RE = re.compile(
    r'(<section\s+id="([^"]+)"[^>]*>.*?</section>)',
    re.DOTALL,
)

def extract_sections(html: str) -> dict[str, str]:
    return {m.group(2): m.group(1) for m in SECTION_RE.finditer(html)}

def find_main_bounds(html: str) -> tuple[int, int]:
    start = html.find('<main class="main-content">')
    if start == -1:
        raise ValueError('No <main> found')
    footer = html.find('<footer class="page-footer">', start)
    if footer == -1:
        footer = html.find('<footer', start)
    if footer == -1:
        raise ValueError('No footer found')
    return start, footer

def reorder(html: str, order: list[str], before_footer_extra: str = '') -> str:
    main_start, footer_start = find_main_bounds(html)
    main_chunk = html[main_start:footer_start]
    sections = extract_sections(main_chunk)
    missing = [sid for sid in order if sid not in sections]
    if missing:
        raise ValueError(f'Missing section ids: {missing}')
    extra = [sid for sid in sections if sid not in order]
    if extra:
        print(f'  Note: sections not in order list (kept at end): {extra}')
    # Remove all sections from main chunk
    stripped = main_chunk
    for sid, block in sections.items():
        stripped = stripped.replace(block, '', 1)
    # Find insertion point: after header/reading-path, before footer content
    # Insert reordered sections before footer
    reordered = '\n'.join(sections[sid] for sid in order)
    if extra:
        reordered += '\n' + '\n'.join(sections[sid] for sid in extra)
    if before_footer_extra:
        reordered += '\n' + before_footer_extra
    new_main = stripped.rstrip() + '\n' + reordered + '\n'
    return html[:main_start] + new_main + html[footer_start:]

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print('Usage: reorder_sections.py <file> <id1> <id2> ...')
        sys.exit(1)
    path = Path(sys.argv[1])
    order = sys.argv[2:]
    html = path.read_text(encoding='utf-8')
    out = reorder(html, order)
    path.write_text(out, encoding='utf-8')
    print(f'Reordered {path.name}: {len(order)} sections')
