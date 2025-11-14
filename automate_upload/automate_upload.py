#!/usr/bin/env python3
import json
import os
import re
import argparse


def file_stem_to_snake(file_stem: str) -> str:
    """
    Convert file stem like:
      - 'SiteLevelEnterprise'
      - 'TECHNOLOGY_LooKuP'
      - 'ACCOUNT_BUSINESS_LISTS'
    into snake_case:
      - 'site_level_enterprise'
      - 'technology_loo_ku_p'
      - 'account_business_lists'
    without splitting every capital letter.
    """
    s = file_stem.strip()

    # Split on non-alphanumeric (underscores, spaces, etc.) to get logical chunks
    raw_parts = re.split(r'[^0-9A-Za-z]+', s)
    parts = []
    for p in raw_parts:
        if not p:
            continue
        if p.isupper():
            # All upper -> treat as a single word (ACCOUNT -> account, NAICS -> naics)
            parts.append(p.lower())
        else:
            # CamelCase -> insert underscore before capitals (SiteLevel -> site_level)
            p2 = re.sub(r'(?<!^)(?=[A-Z])', '_', p)
            parts.append(p2.lower())

    return "_".join(parts)


def generate_copy_sql_files(json_path: str, output_root: str = "."):
    with open(json_path, "r", encoding="utf-8") as f:
        records = json.load(f)

    for rec in records:
        path = rec.get("path")
        region = str(rec.get("region", "unknown"))
        year = str(rec.get("year", "unknown"))

        if not path:
            continue

        # --- region/year dir: e.g. "usa_2022"
        region_clean = region.lower()
        year_str = str(year).lower()
        region_year_dir = f"{region_clean}_{year_str}"
        out_dir = os.path.join(output_root, region_year_dir)
        os.makedirs(out_dir, exist_ok=True)

        # --- filename info
        base_name = os.path.basename(path)           # e.g. ACCOUNT_BUSINESS_LISTS.TXT
        file_stem, ext = os.path.splitext(base_name)  # e.g. ACCOUNT_BUSINESS_LISTS, .TXT

        file_stem_snake = file_stem_to_snake(file_stem)  # e.g. account_business_lists

        # Table name: usa_2022_account_business_lists
        table_name = f"{region_clean}_{year_str}_{file_stem_snake}"

        # Converted UTF-8 path: same dir, _utf8 before extension
        dir_name = os.path.dirname(path)
        utf8_name = f"{file_stem}_utf8{ext}"
        utf8_path = os.path.join(dir_name, utf8_name)

        # SQL filename: copy_usa2022_account_business_lists.sql
        regionyear = f"{region_clean}{year_str}"
        sql_filename = f"copy_{regionyear}_{file_stem_snake}.sql"
        sql_path = os.path.join(out_dir, sql_filename)

        lines = [
            f"-- load data for: {path}",
            "",
            f"\\copy {table_name}",
            f"FROM '{utf8_path}'",
            "WITH (FORMAT csv, HEADER true);",
        ]
        sql_content = "\n".join(lines)

        with open(sql_path, "w", encoding="utf-8") as out_f:
            out_f.write(sql_content)

        print(f"Generated: {sql_path}")


def main():
    parser = argparse.ArgumentParser(
        description="Generate psql \\copy .sql files from SWDB JSON metadata."
    )
    parser.add_argument(
        "json_path",
        nargs="?",
        default="/Users/dmk6603/Documents/ransom/21-swdb_mapping/data/swdb_mapped_usa.json",
        help="Path to the JSON file (default: /home/dima/swdb/21-swdb_mapping/data/swdb_mapped_usa.json)",
    )
    parser.add_argument(
        "-o",
        "--output-root",
        default=".",
        help="Root folder for generated region/year directories (default: current directory)",
    )

    args = parser.parse_args()
    generate_copy_sql_files(args.json_path, args.output_root)


if __name__ == "__main__":
    main()