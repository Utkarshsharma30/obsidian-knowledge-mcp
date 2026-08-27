from __future__ import annotations
from typing import Any
from database.connection import connect

MAX_LIMIT = 100

def limit_value(value: int, default: int = 20) -> int: return max(1, min(int(value or default), MAX_LIMIT))

def search_knowledge(query: str, limit: int = 20) -> list[dict[str, Any]]:
    with connect() as c, c.cursor() as cur:
        cur.execute("""SELECT n.name,n.type,n.description,d.file_path,ts_rank(d.search_vector, plainto_tsquery('simple',%s)) rank
          FROM nodes n LEFT JOIN documents d ON d.id=n.source_document_id WHERE n.name ILIKE %s OR d.search_vector @@ plainto_tsquery('simple',%s)
          ORDER BY rank DESC NULLS LAST,n.name LIMIT %s""", (query, f"%{query}%", query, limit_value(limit)))
        return cur.fetchall()

def get_node(name: str) -> dict[str, Any] | None:
    with connect() as c, c.cursor() as cur:
        cur.execute("SELECT n.*,d.title document_title,d.file_path FROM nodes n LEFT JOIN documents d ON d.id=n.source_document_id WHERE lower(n.name)=lower(%s) LIMIT 1", (name,)); node=cur.fetchone()
        if not node: return None
        cur.execute("""SELECT other.name, e.relationship_type, e.weight FROM edges e JOIN nodes other ON other.id=e.target_node_id WHERE e.source_node_id=%s UNION ALL SELECT other.name,e.relationship_type,e.weight FROM edges e JOIN nodes other ON other.id=e.source_node_id WHERE e.target_node_id=%s""", (node["id"],node["id"])); node["related_nodes"]=cur.fetchall()
        cur.execute("SELECT t.name FROM tags t JOIN node_tags nt ON nt.tag_id=t.id WHERE nt.node_id=%s ORDER BY t.name", (node["id"],)); node["tags"]=[r["name"] for r in cur.fetchall()]
        return node

def get_document(document_id: int) -> dict[str, Any] | None:
    with connect() as c, c.cursor() as cur: cur.execute("SELECT id,title,file_path,content,metadata,created_at,updated_at FROM documents WHERE id=%s", (document_id,)); return cur.fetchone()

def related(name: str, depth: int=1, relationship_type: str|None=None, limit: int=20) -> list[dict[str,Any]]:
    depth=max(1,min(int(depth),5)); params=[name,depth]; type_clause=""
    if relationship_type: type_clause=" AND e.relationship_type=%s"; params.append(relationship_type)
    params.append(limit_value(limit))
    with connect() as c, c.cursor() as cur:
        cur.execute(f"""WITH RECURSIVE start AS (SELECT id FROM nodes WHERE lower(name)=lower(%s)), walk(id,depth) AS (SELECT id,0 FROM start UNION SELECT CASE WHEN e.source_node_id=walk.id THEN e.target_node_id ELSE e.source_node_id END,walk.depth+1 FROM walk JOIN edges e ON e.source_node_id=walk.id OR e.target_node_id=walk.id WHERE walk.depth<%s{type_clause}) SELECT DISTINCT n.name,n.type,walk.depth FROM walk JOIN nodes n ON n.id=walk.id WHERE walk.depth>0 ORDER BY walk.depth,n.name LIMIT %s""", params); return cur.fetchall()

def list_nodes(limit=20, offset=0, node_type=None, tag=None):
    clauses=[]; params=[]
    if node_type: clauses.append("n.type=%s"); params.append(node_type)
    if tag: clauses.append("EXISTS (SELECT 1 FROM node_tags nt JOIN tags t ON t.id=nt.tag_id WHERE nt.node_id=n.id AND lower(t.name)=lower(%s))"); params.append(tag)
    params += [limit_value(limit), max(0,int(offset))]
    with connect() as c, c.cursor() as cur: cur.execute(f"SELECT n.id,n.name,n.type,n.description FROM nodes n WHERE {' AND '.join(clauses) or 'TRUE'} ORDER BY n.name LIMIT %s OFFSET %s", params); return cur.fetchall()

def search_documents(query: str, limit=20):
    with connect() as c, c.cursor() as cur: cur.execute("SELECT id,title,file_path,summary,ts_rank(search_vector,plainto_tsquery('simple',%s)) rank FROM documents WHERE search_vector @@ plainto_tsquery('simple',%s) OR title ILIKE %s ORDER BY rank DESC LIMIT %s", (query,query,f"%{query}%",limit_value(limit))); return cur.fetchall()

def find_path(source: str,target: str,max_depth=5):
    with connect() as c, c.cursor() as cur:
        cur.execute("""WITH RECURSIVE walk(id,path,depth) AS (SELECT id,ARRAY[name],0 FROM nodes WHERE lower(name)=lower(%s) UNION ALL SELECT CASE WHEN e.source_node_id=w.id THEN e.target_node_id ELSE e.source_node_id END,w.path||n.name,w.depth+1 FROM walk w JOIN edges e ON e.source_node_id=w.id OR e.target_node_id=w.id JOIN nodes n ON n.id=CASE WHEN e.source_node_id=w.id THEN e.target_node_id ELSE e.source_node_id END WHERE w.depth<%s AND NOT n.name=ANY(w.path)) SELECT path FROM walk WHERE lower(path[array_length(path,1)])=lower(%s) ORDER BY depth LIMIT 1""", (source,max_depth,target)); row=cur.fetchone(); return row["path"] if row else None
