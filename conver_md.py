from pathlib import Path

from flask import Flask, render_template
import markdown

app = Flask(__name__)


# ---------- Helpers to convert fenced code blocks into tables ----------

def _block_to_vertical_table(block_lines):
    """
    Convert a TSV/CSV code block (schema + 0/1 data rows)
    into a vertical markdown table.

    - First non-empty line = header (column names).
    - Second non-empty line (if present) = example row.
    """

    # Remove empty lines and strip line endings
    lines = [l.rstrip("\n") for l in block_lines if l.strip()]
    if not lines:
        return ""

    header_line = lines[0]

    # Decide delimiter: comma vs tab (default to tab if both appear)
    if "," in header_line and "\t" not in header_line:
        delim = ","
    else:
        delim = "\t"

    headers = [h.strip() for h in header_line.split(delim)]

    # Default examples are empty
    examples = [""] * len(headers)
    if len(lines) > 1:
        row = lines[1]
        cells = [c.strip() for c in row.split(delim)]
        # pad / truncate to match header length
        if len(cells) < len(headers):
            cells += [""] * (len(headers) - len(cells))
        examples = cells[:len(headers)]

    out = []
    out.append("| Column | Example |")
    out.append("| ------ | ------- |")
    for col, val in zip(headers, examples):
        # escape pipe characters in values, just in case
        val = val.replace("|", "\\|")
        col = col.replace("|", "\\|")
        out.append(f"| {col} | {val} |")

    return "\n".join(out)


def convert_swdb_codeblocks(md_text: str) -> str:
    """
    Replace ```text (or ``` with no language) blocks that contain
    SWDB-style TSV/CSV schemas with vertical markdown tables.

    Non-`text` code blocks are left untouched.
    """
    lines = md_text.splitlines()
    output_lines = []

    in_fence = False
    fence_lang = ""
    block_lines = []

    for line in lines:
        if line.startswith("```"):
            # toggle fence
            if not in_fence:
                # opening fence
                in_fence = True
                fence_lang = line[3:].strip()  # e.g. "text", "", "python"
                block_lines = []
            else:
                # closing fence
                in_fence = False
                if fence_lang in ("", "text"):
                    # transform this block into a vertical table
                    table_md = _block_to_vertical_table(block_lines)
                    output_lines.append(table_md)
                else:
                    # keep other language blocks as-is
                    output_lines.append("```" + fence_lang)
                    output_lines.extend(block_lines)
                    output_lines.append("```")

                block_lines = []
                fence_lang = ""
            continue

        if in_fence:
            block_lines.append(line)
        else:
            output_lines.append(line)

    # If file ends while still inside a fence, dump what we have
    if in_fence and block_lines:
        output_lines.append("```" + fence_lang)
        output_lines.extend(block_lines)

    return "\n".join(output_lines)


# ---------- Route ----------

@app.route("/swdb-structure")
def swdb_structure():
    """Render the SWDB structure markdown file as an HTML page."""
    md_path = Path(__file__).with_name("swdb_structure.md")

    try:
        markdown_text = md_path.read_text(encoding="utf-8")

        # 1) Pre-process: convert SWDB code blocks into markdown tables
        markdown_text = convert_swdb_codeblocks(markdown_text)

        # 2) Convert markdown to HTML
        markdown_html = markdown.markdown(
            markdown_text,
            extensions=["fenced_code", "tables"],
        )
    except FileNotFoundError:
        markdown_html = (
            "<p><strong>swdb_structure.md</strong> file not found.</p>"
        )
    except Exception as exc:  # pragma: no cover
        markdown_html = f"<p>Error loading markdown: {exc}</p>"

    return render_template("swdb_structure.html", content=markdown_html)


if __name__ == "__main__":
    # For local testing
    app.run(debug=True)
