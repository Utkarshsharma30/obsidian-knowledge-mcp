CREATE TABLE IF NOT EXISTS documents (
  id BIGSERIAL PRIMARY KEY,
  title TEXT NOT NULL,
  file_path TEXT NOT NULL UNIQUE,
  slug TEXT NOT NULL UNIQUE,
  content TEXT NOT NULL,
  summary TEXT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
  search_vector TSVECTOR GENERATED ALWAYS AS (to_tsvector('simple', coalesce(title,'') || ' ' || coalesce(content,''))) STORED
);
CREATE TABLE IF NOT EXISTS nodes (
  id BIGSERIAL PRIMARY KEY,
  name TEXT NOT NULL UNIQUE,
  type TEXT NOT NULL DEFAULT 'concept',
  description TEXT,
  source_document_id BIGINT REFERENCES documents(id) ON DELETE SET NULL,
  metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE TABLE IF NOT EXISTS edges (
  id BIGSERIAL PRIMARY KEY,
  source_node_id BIGINT NOT NULL REFERENCES nodes(id) ON DELETE CASCADE,
  target_node_id BIGINT NOT NULL REFERENCES nodes(id) ON DELETE CASCADE,
  relationship_type TEXT NOT NULL DEFAULT 'related_to',
  weight DOUBLE PRECISION NOT NULL DEFAULT 1,
  metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  UNIQUE(source_node_id, target_node_id, relationship_type)
);
CREATE TABLE IF NOT EXISTS tags (id BIGSERIAL PRIMARY KEY, name TEXT NOT NULL UNIQUE);
CREATE TABLE IF NOT EXISTS node_tags (node_id BIGINT REFERENCES nodes(id) ON DELETE CASCADE, tag_id BIGINT REFERENCES tags(id) ON DELETE CASCADE, PRIMARY KEY(node_id, tag_id));
CREATE TABLE IF NOT EXISTS document_links (source_document_id BIGINT REFERENCES documents(id) ON DELETE CASCADE, target_document_id BIGINT REFERENCES documents(id) ON DELETE CASCADE, target_text TEXT NOT NULL, PRIMARY KEY(source_document_id, target_document_id, target_text));
CREATE INDEX IF NOT EXISTS documents_search_idx ON documents USING GIN(search_vector);
CREATE INDEX IF NOT EXISTS nodes_name_idx ON nodes(lower(name));
CREATE INDEX IF NOT EXISTS edges_source_idx ON edges(source_node_id);
CREATE INDEX IF NOT EXISTS edges_target_idx ON edges(target_node_id);
CREATE INDEX IF NOT EXISTS tags_name_idx ON tags(lower(name));
