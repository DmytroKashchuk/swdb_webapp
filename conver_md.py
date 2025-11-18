import sys

IN_FENCE = False
block_lines = []

def block_to_markdown(block_lines, include_data_rows=True):
    """
    Convert a TSV/CSV block (list of lines) to a markdown table.
    First non-empty line is treated as header.
    """
    # Remove leading/trailing blank lines
    lines = [l.rstrip("\n") for l in block_lines]
    lines = [l for l in lines if l.strip() != ""]
    if not lines:
        return ""

    header = lines[0]

    # Decide delimiter: CSV (,) vs TSV (\t). If both exist, prefer comma.
    if "," in header and "\t" not in header:
        delim = ","
    else:
        delim = "\t"

    headers = [h.strip() for h in header.split(delim)]

    out = []
    # Header row
    out.append("| " + " | ".join(headers) + " |")
    # Separator row
    out.append("| " + " | ".join(["---"] * len(headers)) + " |")

    if include_data_rows:
        for row in lines[1:]:
            cells = [c.strip() for c in row.split(delim)]
            # Pad cells if row has fewer columns than header
            if len(cells) < len(headers):
                cells += [""] * (len(headers) - len(cells))
            # Truncate if row has more columns (shouldn't normally happen)
            cells = cells[:len(headers)]
            out.append("| " + " | ".join(cells) + " |")

    return "\n".join(out)


def main():
    global IN_FENCE, block_lines

    include_data_rows = True  # change to False if you only want schema (headers)

    for raw_line in sys.stdin:
        line = raw_line.rstrip("\n")

        if line.startswith("```"):
            # Toggle fence state
            if not IN_FENCE:
                # Opening fence: start collecting
                IN_FENCE = True
                block_lines = []
                # We DON'T print this line, because we want to replace the
                # fenced code block with a markdown table, not another block.
            else:
                # Closing fence: convert collected block
                IN_FENCE = False
                md_table = block_to_markdown(block_lines, include_data_rows)
                if md_table:
                    print(md_table)
                block_lines = []
            continue

        if IN_FENCE:
            # Accumulate lines inside code block
            block_lines.append(line)
        else:
            # Outside code block: print as-is
            print(line)

if __name__ == "__main__":
    main()
