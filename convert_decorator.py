#!/usr/bin/env python3
"""
Convert between Jupyter notebooks and clean Markdown.

Decorators:
    @startCode / @endCode       - Code cells
    @startOutput / @endOutput   - Cell outputs
    @startMD / @endMD           - Markdown cells

Images (attachments and output plots) are extracted into an
`images/` subfolder next to the output markdown file.

Usage:
    python convert_decorator.py --from notebook.ipynb --to output.md
    python convert_decorator.py --from output.md --to notebook.ipynb
"""

import argparse
import base64
import json
import os
import re
import sys
from pathlib import Path

import nbformat


class CleanMarkdownConverter:
    """Convert between notebook and clean markdown using @ decorators."""

    # ── notebook → markdown ──────────────────────────────────────────

    @staticmethod
    def notebook_to_clean_md(notebook_path: str, output_path: str) -> None:
        output_dir = Path(output_path).parent
        images_dir = output_dir / "images"
        images_dir.mkdir(parents=True, exist_ok=True)

        notebook = nbformat.read(notebook_path, as_version=4)
        lines: list[str] = []
        image_counter = 0

        for cell in notebook.cells:

            # ── markdown cell ────────────────────────────────────
            if cell.cell_type == "markdown":
                source = cell.source

                # Extract attachment images
                attachments = cell.get("attachments", {})
                for att_name, att_data in attachments.items():
                    for mime, b64 in att_data.items():
                        if mime.startswith("image/"):
                            ext = mime.split("/")[1]
                            image_counter += 1
                            filename = f"image_{image_counter}.{ext}"
                            img_path = images_dir / filename
                            img_path.write_bytes(base64.b64decode(b64))
                            # Replace the attachment reference in source
                            source = source.replace(
                                f"attachment:{att_name}",
                                f"images/{filename}",
                            )

                lines.append("@startMD")
                lines.append(source.rstrip())
                lines.append("@endMD")
                lines.append("")

            # ── code cell ────────────────────────────────────────
            elif cell.cell_type == "code":
                lines.append("@startCode")
                lines.append("```python")
                lines.append(cell.source.rstrip())
                lines.append("```")
                lines.append("@endCode")
                lines.append("")

                # ── outputs ──────────────────────────────────────
                outputs = cell.get("outputs", [])
                if outputs:
                    lines.append("@startOutput")
                    for output in outputs:
                        if output.output_type == "stream":
                            lines.append("```")
                            lines.append(output.text.rstrip())
                            lines.append("```")

                        elif output.output_type in (
                            "execute_result",
                            "display_data",
                        ):
                            data = output.get("data", {})
                            if "text/plain" in data:
                                lines.append("```")
                                lines.append(data["text/plain"].rstrip())
                                lines.append("```")
                            if "image/png" in data:
                                image_counter += 1
                                filename = f"output_{image_counter}.png"
                                img_path = images_dir / filename
                                img_path.write_bytes(
                                    base64.b64decode(data["image/png"])
                                )
                                lines.append(f"![output](images/{filename})")

                        elif output.output_type == "error":
                            lines.append("```")
                            lines.append(
                                "\n".join(output.get("traceback", [])).rstrip()
                            )
                            lines.append("```")

                    lines.append("@endOutput")
                    lines.append("")

        with open(output_path, "w") as f:
            f.write("\n".join(lines))

        print(f"Converted: {notebook_path} -> {output_path}")
        print(f"Images saved to: {images_dir}/  ({image_counter} images)")

    # ── markdown → notebook ──────────────────────────────────────────

    @staticmethod
    def clean_md_to_notebook(markdown_path: str, output_path: str) -> None:
        md_dir = Path(markdown_path).parent

        with open(markdown_path) as f:
            content = f.read()

        cells: list = []
        lines = content.split("\n")
        i = 0

        while i < len(lines):
            line = lines[i].strip()

            # ── markdown cell ────────────────────────────────────
            if line == "@startMD":
                i += 1
                block: list[str] = []
                while i < len(lines) and lines[i].strip() != "@endMD":
                    md_line = lines[i]
                    block.append(md_line)
                    i += 1
                source = "\n".join(block).rstrip()

                # Re-embed images as attachments
                md_cell = nbformat.v4.new_markdown_cell(source)
                attachments: dict = {}
                for match in re.finditer(
                    r"!\[([^\]]*)\]\((images/[^)]+)\)", source
                ):
                    img_rel = match.group(2)
                    img_path = md_dir / img_rel
                    if img_path.exists():
                        b64 = base64.b64encode(img_path.read_bytes()).decode()
                        att_name = Path(img_rel).name
                        attachments[att_name] = {"image/png": b64}
                        source = source.replace(
                            img_rel, f"attachment:{att_name}"
                        )
                if attachments:
                    md_cell.source = source
                    md_cell.attachments = attachments
                cells.append(md_cell)
                i += 1  # skip @endMD

            # ── code cell ────────────────────────────────────────
            elif line == "@startCode":
                i += 1
                # skip opening ```python
                if i < len(lines) and lines[i].strip().startswith("```"):
                    i += 1
                code_lines: list[str] = []
                while i < len(lines) and lines[i].strip() != "@endCode":
                    # skip closing ```
                    if lines[i].strip() == "```":
                        i += 1
                        continue
                    code_lines.append(lines[i])
                    i += 1
                cells.append(
                    nbformat.v4.new_code_cell("\n".join(code_lines).rstrip())
                )
                i += 1  # skip @endCode

            # ── output block (skip when building notebook) ───────
            elif line == "@startOutput":
                i += 1
                while i < len(lines) and lines[i].strip() != "@endOutput":
                    i += 1
                i += 1  # skip @endOutput

            else:
                i += 1

        notebook = nbformat.v4.new_notebook(cells=cells)
        nbformat.write(notebook, output_path)
        print(f"Converted: {markdown_path} -> {output_path}")


# ── CLI plumbing ─────────────────────────────────────────────────────


def detect_format(path: str) -> str:
    ext = Path(path).suffix.lower()
    if ext == ".ipynb":
        return "ipynb"
    if ext in {".md", ".markdown"}:
        return "markdown"
    raise ValueError(f"Unsupported format: {ext}")


def convert(from_path: str, to_path: str) -> None:
    from_fmt = detect_format(from_path)
    to_fmt = detect_format(to_path)

    if not Path(from_path).exists():
        raise FileNotFoundError(f"Source file not found: {from_path}")

    converter = CleanMarkdownConverter()

    if from_fmt == "ipynb" and to_fmt == "markdown":
        converter.notebook_to_clean_md(from_path, to_path)
    elif from_fmt == "markdown" and to_fmt == "ipynb":
        converter.clean_md_to_notebook(from_path, to_path)
    else:
        raise ValueError(f"Unsupported conversion: {from_fmt} -> {to_fmt}")


def main():
    parser = argparse.ArgumentParser(
        description="Convert between Jupyter notebooks and decorated Markdown"
    )
    parser.add_argument(
        "--from", dest="from_path", required=True,
        help="Source file path (.ipynb or .md)",
    )
    parser.add_argument(
        "--to", dest="to_path", required=True,
        help="Target file path (.ipynb or .md)",
    )
    args = parser.parse_args()

    try:
        convert(args.from_path, args.to_path)
    except (FileNotFoundError, ValueError) as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
