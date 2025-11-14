#!/usr/bin/env python3
import json
import os
import sys
import re
import argparse
from typing import Optional


def normalize_identifier(name: str) -> str:
    """
    Normalize column/table names for PostgreSQL:
    - strip outer quotes and whitespace
    - replace any non-alphanumeric sequence with '_'
    - if it starts with a digit, prefix with 'c_'
    - lowercase
    """
    name = name.strip()
    if name.startswith('"') and name.endswith('"') and len(name) >= 2:
        name = name[1:-1]
    name = name.strip()
    # Replace non-alphanumeric with underscore
    name = re.sub(r'[^0-9A-Za-z]+', '_', name)
    if re.match(r'^[0-9]', name):
        name = 'c_' + name
    return name.lower()


def infer_delimiter(header_line: str, meta_delim: Optional[str] = None) -> str:
    """
    Infer delimiter from JSON metadata and/or header line.
    Tries (in order): meta_delim, then common delimiters.
    """
    # Map JSON delimiter labels to actual characters
    meta_map = {
        'tab': '\t',
        '\\t': '\t',
        'comma': ',',
        ',': ',',
        'pipe': '|',
        '|': '|',
        'semicolon': ';',
        ';': ';',
    }

    if meta_delim:
        d = meta_map.get(str(meta_delim).strip().lower())
        if d and d in header_line:
            return d

    # Fallback: pick the delimiter that yields the most fields (>1)
    candidates = ['\t', ',', '|', ';']
    best = '\t'
    best_len = 1
    for d in candidates:
        parts = header_line.split(d)
        if len(parts) > best_len:
            best_len = len(parts)
            best = d

    return best


def generate_sql_files(json_path, output_root="."):
    # Load JSON (list of records)
    with open(json_path, "r", encoding="utf-8") as f:
        records = json.load(f)

    for rec in records:
        path = rec.get("path")
        region = str(rec.get("region", "unknown"))
        year = str(rec.get("year", "unknown"))
        first_lines = rec.get("first_4_lines") or []
        meta_delim = rec.get("delimiter")

        if not path or not first_lines:
            print(f"Skipping record (missing path or first_4_lines): {path}", file=sys.stderr)
            continue

        # ------------------------
        # Lowercase region/year directory, e.g. "usa_1996"
        # ------------------------
        region_clean = region.lower()
        year_str = year.lower()
        region_year_dir = f"{region_clean}_{year_str}"
        out_dir = os.path.join(output_root, region_year_dir)
        os.makedirs(out_dir, exist_ok=True)

        # ------------------------
        # SQL filename: create_[regionyear]_[file_stem].sql (all lowercase)
        # e.g. create_usa1996_hist1996_corp.sql
        # ------------------------
        base_name = os.path.basename(path)          # e.g. Hist1996_Corp.txt or TECHNOLOGY_LooKuP.TXT
        file_stem, _ = os.path.splitext(base_name)  # e.g. Hist1996_Corp
        file_stem_lower = file_stem.lower()
        regionyear = f"{region_clean}{year_str}"
        sql_filename = f"create_{regionyear}_{file_stem_lower}.sql"
        sql_path = os.path.join(out_dir, sql_filename)

        # ------------------------
        # Header parsing with delimiter inference
        # ------------------------
        header_line = first_lines[0]
        delim_char = infer_delimiter(header_line, meta_delim)
        raw_cols = header_line.split(delim_char)

        col_names = []
        for i, raw in enumerate(raw_cols, start=1):
            col = normalize_identifier(raw)
            if not col:  # safety fallback
                col = f"col_{i}"
            col_names.append(col)

        # ------------------------
        # Table name: region_year_file_stem (lowercase)
        # e.g. usa_2022_technology_lookup
        # ------------------------
        table_name = f"{region_clean}_{year_str}_{file_stem_lower}"

        # Pretty alignment
        max_len = max(len(c) for c in col_names) if col_names else 0

        # ------------------------
        # Build SQL
        # ------------------------
        lines = []
        lines.append(f"-- source file: {path}")
        lines.append(f"-- region: {region}, year: {year}")
        lines.append("")
        lines.append(f"CREATE TABLE {table_name} (")

        for i, col in enumerate(col_names):
            comma = "," if i < len(col_names) - 1 else ""
            lines.append(f"    {col.ljust(max_len)} text{comma}")

        lines.append(");")
        sql_content = "\n".join(lines)

        # ------------------------
        # Write .sql file
        # ------------------------
        with open(sql_path, "w", encoding="utf-8") as out_f:
            out_f.write(sql_content)

        print(f"Generated: {sql_path}")


def main():
    parser = argparse.ArgumentParser(
        description="Generate PostgreSQL CREATE TABLE .sql files from SWDB JSON metadata."
    )
    parser.add_argument(
        "json_path",
        nargs="?",
        default="/Users/dmk6603/Documents/ransom/21-swdb_mapping/data/swdb_mapped_usa.json",
        help="Path to the JSON file "
             "(default: /Users/dmk6603/Documents/ransom/21-swdb_mapping/data/swdb_mapped_usa.json)",
    )
    parser.add_argument(
        "-o",
        "--output-root",
        default=".",
        help="Root folder for generated region/year directories (default: current directory)",
    )

    args = parser.parse_args()
    generate_sql_files(args.json_path, args.output_root)


if __name__ == "__main__":
    main()