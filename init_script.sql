CREATE TABLE IF NOT EXISTS seal (
  id INTEGER PRIMARY KEY,
  family TEXT,
  width FLOAT,
  height FLOAT,
  unit TEXT
);

CREATE TABLE IF NOT EXISTS tag (
  id INTEGER PRIMARY KEY,
  name
);

CREATE TABLE IF NOT EXISTS seal_has_tag (
  id INTEGER PRIMARY KEY,
  seal_id INTEGER,
  tag_id INTEGER,
  FOREIGN KEY(seal_id) REFERENCES seal(id),
  FOREIGN KEY(tag_id) REFERENCES tag(id)
);

DELETE FROM seal_has_tag;
DELETE FROM tag;
DELETE FROM seal;

