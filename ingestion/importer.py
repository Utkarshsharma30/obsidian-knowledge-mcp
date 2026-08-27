from __future__ import annotations
import argparse, hashlib, json, logging, os, re
from pathlib import Path
from dotenv import load_dotenv
from psycopg.types.json import Jsonb
from database.connection import connect
from ingestion.markdown_parser import scan_vault

logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"), format="%(levelname)s %(message)s")
log = logging.getLogger(__name__)

def slug(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-") or "untitled"

def jsonb(value: object) -> Jsonb:
    return Jsonb(value, dumps=lambda item: json.dumps(item, default=str))

def import_vault(vault_root: Path) -> int:
    if not vault_root.is_dir(): raise ValueError(f"Vault path is not a directory: {vault_root}")
    notes = scan_vault(vault_root)
    with connect() as conn:
        with conn.cursor() as cur:
            cur.execute("TRUNCATE document_links")
            for note in notes:
                summary = re.sub(r"\s+", " ", note.body).strip()[:500]
                cur.execute("""INSERT INTO documents(title,file_path,slug,content,summary,metadata,updated_at)
                    VALUES (%s,%s,%s,%s,%s,%s,now())
                    ON CONFLICT(file_path) DO UPDATE SET title=EXCLUDED.title,slug=EXCLUDED.slug,content=EXCLUDED.content,summary=EXCLUDED.summary,metadata=EXCLUDED.metadata,updated_at=now()
                    RETURNING id""", (note.title, note.relative_path, slug(note.relative_path), note.body, summary, jsonb(note.metadata)))
                document_id = cur.fetchone()["id"]
                cur.execute("""INSERT INTO nodes(name,type,description,source_document_id,metadata,updated_at)
                    VALUES (%s,'document',%s,%s,%s,now()) ON CONFLICT(name) DO UPDATE SET description=EXCLUDED.description,source_document_id=EXCLUDED.source_document_id,metadata=EXCLUDED.metadata,updated_at=now()
                    RETURNING id""", (note.title, summary, document_id, jsonb({"aliases": note.aliases, "headings": note.headings, "file_path": note.relative_path})))
                node_id = cur.fetchone()["id"]
                for tag in note.tags:
                    cur.execute("INSERT INTO tags(name) VALUES (%s) ON CONFLICT(name) DO UPDATE SET name=EXCLUDED.name RETURNING id", (tag,))
                    tag_id = cur.fetchone()["id"]
                    cur.execute("INSERT INTO node_tags(node_id,tag_id) VALUES (%s,%s) ON CONFLICT DO NOTHING", (node_id, tag_id))
            # Resolve links after all document nodes exist. Missing targets are intentionally ignored.
            for note in notes:
                cur.execute("SELECT id FROM documents WHERE file_path=%s", (note.relative_path,)); source_doc = cur.fetchone()
                cur.execute("SELECT id FROM nodes WHERE name=%s", (note.title,)); source_node = cur.fetchone()
                for link in note.links:
                    target = link["target"]
                    target_name = next((n.title for n in notes if n.path.stem == target or n.title == target or target in n.aliases), None)
                    if not target_name: log.warning("Unresolved link in %s: %s", note.relative_path, target); continue
                    cur.execute("SELECT id FROM documents WHERE title=%s", (target_name,)); target_doc = cur.fetchone()
                    cur.execute("SELECT id FROM nodes WHERE name=%s", (target_name,)); target_node = cur.fetchone()
                    if source_doc and target_doc:
                        cur.execute("INSERT INTO document_links VALUES (%s,%s,%s) ON CONFLICT DO NOTHING", (source_doc["id"], target_doc["id"], target))
                    if source_node and target_node and source_node["id"] != target_node["id"]:
                        cur.execute("INSERT INTO edges(source_node_id,target_node_id,relationship_type,metadata) VALUES (%s,%s,'related_to',%s) ON CONFLICT DO NOTHING", (source_node["id"], target_node["id"], jsonb({"source": note.relative_path})))
    log.info("Imported %d Markdown documents from %s", len(notes), vault_root)
    return len(notes)

def main() -> None:
    load_dotenv(); parser = argparse.ArgumentParser(); parser.add_argument("vault", nargs="?", default=os.getenv("OBSIDIAN_VAULT_PATH")); args = parser.parse_args()
    if not args.vault: parser.error("provide VAULT or set OBSIDIAN_VAULT_PATH")
    import_vault(Path(args.vault).expanduser().resolve())

if __name__ == "__main__": main()
