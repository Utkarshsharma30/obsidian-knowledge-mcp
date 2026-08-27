"""Pure Obsidian Markdown parsing; never writes to the vault."""
from __future__ import annotations
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any
import yaml

LINK_RE = re.compile(r"!?(\[\[([^\]|#]+)(?:#([^\]|]+))?(?:\|([^\]]+))?\]\])")
TAG_RE = re.compile(r"(?<![\w/])#([A-Za-z0-9_/-]+)")
HEADING_RE = re.compile(r"^#{1,6}\s+(.+?)\s*#*\s*$", re.MULTILINE)

@dataclass
class ParsedNote:
    path: Path
    relative_path: str
    title: str
    aliases: list[str] = field(default_factory=list)
    tags: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)
    headings: list[str] = field(default_factory=list)
    body: str = ""
    links: list[dict[str, str | None]] = field(default_factory=list)


def _as_list(value: Any) -> list[str]:
    if value is None: return []
    if isinstance(value, list): return [str(item).strip() for item in value if str(item).strip()]
    return [item.strip() for item in str(value).split(",") if item.strip()]


def parse_markdown(path: Path, vault_root: Path) -> ParsedNote:
    raw = path.read_text(encoding="utf-8-sig")
    metadata: dict[str, Any] = {}
    body = raw
    if raw.startswith("---"):
        match = re.match(r"^---\s*\n(.*?)\n---\s*(?:\n|$)", raw, re.DOTALL)
        if match:
            loaded = yaml.safe_load(match.group(1))
            metadata = loaded if isinstance(loaded, dict) else {}
            body = raw[match.end():]
    stem = path.stem
    title = str(metadata.get("title") or stem)
    aliases = _as_list(metadata.get("aliases"))
    tags = _as_list(metadata.get("tags"))
    tags.extend(TAG_RE.findall(body))
    tags = list(dict.fromkeys(tag.lstrip("#") for tag in tags))
    links = [{"target": target.strip(), "heading": heading or None, "alias": alias or None}
             for _, target, heading, alias in LINK_RE.findall(body)]
    return ParsedNote(path, path.relative_to(vault_root).as_posix(), title, aliases, tags,
                      metadata, HEADING_RE.findall(body), body, links)


def scan_vault(vault_root: Path) -> list[ParsedNote]:
    return [parse_markdown(path, vault_root) for path in sorted(vault_root.rglob("*.md")) if path.is_file()]
