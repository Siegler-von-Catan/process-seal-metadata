#!/usr/bin/env python3

# ProcessSeaMetadata - Summarize relevant seal metadata in a useable format
# Copyright (C) 2021
# Joana Bergsiek, Leonard Geier, Lisa Ihde,
# Tobias Markus, Dominik Meier, Paul Methfessel
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

from argparse import ArgumentParser
from pathlib import Path
import xml.etree.ElementTree as ET
import sqlite3
import re
from tqdm import tqdm

ns = {"xml": "http://www.w3.org/XML/1998/namespace",
      "lido": "http://www.lido-schema.org"}

tag_pattern = re.compile(" <.*>")


def get_args():
    parser = ArgumentParser(description="Extracts the necessary information \
            from the seal metadata and puts it into an sqlite file.")

    parser.add_argument("metadata_dir", type=Path)
    parser.add_argument("-o", "--output_file", type=Path,
                        default=Path("db.sqlite"))

    args = parser.parse_args()
    return args.metadata_dir, args.output_file


def extract_measurements(root):
    measurements = {}

    measurement_nodes = root.findall(".//lido:objectMeasurements", ns)

    for node in measurement_nodes:
        value = float(node.find(".//lido:measurementValue", ns).text)
        unit = node.find(".//lido:measurementUnit", ns).text
        mtype = node.find(
            ".//lido:measurementType[@xml:lang='en']", ns).text

        entry = (value, unit)
        if mtype == "diameter":
            measurements["width"] = entry
            measurements["height"] = entry
        else:
            measurements[mtype] = entry

    for dimension in ["width", "height"]:
        if dimension not in measurements:
            measurements[dimension] = (-1, "N/A")

    return measurements


def extract_family(root):
    family = root.find(".//lido:appellationValue", ns).text
    return family.replace("Siegel", "").strip()


def extract_tags(root):
    tag_nodes = root.findall(".//lido:subjectSet//lido:term", ns)
    return [tag_pattern.sub("", node.text) for node in tag_nodes]


def insert_seal(family, width, height, unit, conn):
    cur = conn.execute("INSERT INTO seal (family, width, height, unit) \
            VALUES (?, ?, ?, ?)", (family, width, height, unit))
    return cur.lastrowid


def insert_tags(tags, seal_id, conn):
    for tag in tags:
        cur = conn.execute("SELECT id FROM tag WHERE name = ?", (tag,))
        result = cur.fetchone()

        if result:
            tag_id = result[0]
        else:
            cur = conn.execute("INSERT INTO tag (name) VALUES (?)", (tag,))
            tag_id = cur.lastrowid

        conn.execute("INSERT INTO seal_has_tag (seal_id, tag_id) \
                VALUES (?, ?)", (seal_id, tag_id))


def process_file(path, conn):
    if path.suffix != ".xml":
        print("%s does not end with .xml, skipping" % path)
        return

    root = ET.parse(path)

    measurements = extract_measurements(root)
    family = extract_family(root)
    tags = extract_tags(root)

    # TODO: Use the unit of height if it is N/A for width
    seal_id = insert_seal(
            family, measurements["width"][0], measurements["height"][0],
            measurements["width"][1], conn)

    insert_tags(tags, seal_id, conn)


def main():
    metadata_dir, output_file = get_args()

    output_file.parent.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(output_file)

    with open("init_script.sql", "r") as init_script_file:
        init_script = init_script_file.read()
    conn.executescript(init_script)

    metadata_files = list(metadata_dir.iterdir())
    for metadata_file in tqdm(metadata_files):
        process_file(metadata_file, conn)

    conn.commit()
    conn.close()


if __name__ == "__main__":
    main()
