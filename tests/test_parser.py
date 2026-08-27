from pathlib import Path
from ingestion.markdown_parser import parse_markdown, scan_vault

def test_parse_frontmatter_links_and_tags(tmp_path: Path):
    note=tmp_path/'Python.md'; note.write_text('---\ntitle: Python\naliases: [Py, Python Lang]\ntags: [AI, programming]\n---\n# Overview\nSee [[Machine Learning|ML]] and [[Missing]]. #extra', encoding='utf-8')
    parsed=parse_markdown(note,tmp_path)
    assert parsed.title == 'Python'
    assert parsed.aliases == ['Py','Python Lang']
    assert set(parsed.tags) == {'AI','programming','extra'}
    assert parsed.headings == ['Overview']
    assert parsed.links == [{'target':'Machine Learning','heading':None,'alias':'ML'},{'target':'Missing','heading':None,'alias':None}]

def test_scan_is_recursive_and_preserves_relative_path(tmp_path: Path):
    (tmp_path/'folder').mkdir(); (tmp_path/'folder'/'Note.md').write_text('content', encoding='utf-8')
    notes=scan_vault(tmp_path)
    assert len(notes)==1 and notes[0].relative_path=='folder/Note.md'
