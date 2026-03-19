# ipnb2md

Convert Jupyter notebooks to markdown for version control. Keeps notebooks clean in git.

## Install

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Quick Start

```bash
# notebook to markdown
python convert_decorator.py --from notebook.ipynb --to output.md

# markdown back to notebook
python convert_decorator.py --from output.md --to notebook.ipynb
```

Images go into an `images/` folder next to the markdown file.

## What It Looks Like

```
@startMD
# Section Title
![](images/img_1.png)
@endMD

@startCode
```python
x = 1 + 1
```
@endCode

@startOutput
```
2
```
@endOutput
```

## Why Not Just Use Jupytext?

Jupytext is great if you want to edit markdown in Jupyter. But for git, it's messy:

- Adds YAML headers and metadata to every markdown file
- Embeds images as base64 in the file (huge diffs)
- Keeps execution counts and output state (causes merge conflicts)

This tool strips all that out. Notebooks in git are smaller, diffs are readable, and you don't fight over execution counts.

The trade-off is it doesn't integrate with Jupyter—it's purely for storing notebooks cleanly in version control.

## How It Works

**Notebook → Markdown:**
- Code cells become `@startCode...@endCode` blocks
- Markdown cells become `@startMD...@endMD`
- Output goes in `@startOutput...@endOutput`
- Images extract to `images/` folder

**Markdown → Notebook:**
- Reverse the process. Images get re-embedded as attachments.
