#!/usr/bin/env bash
set -euo pipefail

if [ "$#" -lt 1 ]; then
  echo "Usage: $0 FOLDER [FROM_ENCODING]"
  echo "Example: $0 /home/dima/swdb/swdb_all_data/swdb_all_data_unziped/USA_2016 WINDOWS-1252"
  exit 1
fi

FOLDER="$1"
# Default source encoding: WINDOWS-1252 (you can override as second arg)
FROM_ENCODING="${2:-WINDOWS-1252}"

if [ ! -d "$FOLDER" ]; then
  echo "Error: '$FOLDER' is not a directory"
  exit 1
fi

echo "Converting files in: $FOLDER"
echo "Source encoding     : $FROM_ENCODING"
echo "Target encoding     : UTF-8"
echo

shopt -s nullglob

for f in "$FOLDER"/*; do
  # Skip if not a regular file
  [ -f "$f" ] || continue

  filename="$(basename "$f")"
  dirname="$(dirname "$f")"

  # Skip files already converted (ending with _utf8 before extension)
  if [[ "$filename" == *_utf8.* ]]; then
    echo "Skipping already-converted file: $filename"
    continue
  fi

  # Split name + extension
  base="${filename%.*}"
  ext="${filename##*.}"

  # Handle files without extension
  if [[ "$filename" == "$ext" ]]; then
    # no dot in name
    out="${dirname}/${base}_utf8"
  else
    out="${dirname}/${base}_utf8.${ext}"
  fi

  echo "Converting: $filename -> $(basename "$out")"
  iconv -f "$FROM_ENCODING" -t UTF-8 "$f" -o "$out"
done

echo
echo "Done."