/* 
 * ProcessSeaMetadata - Summarize relevant seal metadata in a useable format
 * Copyright (C) 2021
 * Joana Bergsiek, Leonard Geier, Lisa Ihde,
 * Tobias Markus, Dominik Meier, Paul Methfessel
 * 
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 * 
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 * 
 * You should have received a copy of the GNU General Public License
 * along with this program.  If not, see <https://www.gnu.org/licenses/>.
 */

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

