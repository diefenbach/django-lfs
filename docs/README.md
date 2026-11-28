# Django-LFS Documentation

This directory contains the Sphinx-based documentation for django-lfs.

## Quick Start

```bash
bin/docs
```

Builds the documentation and shows it at http://127.0.0.1:8040/; every change in `docs/` rebuilds it and reloads
the browser. Needs [uv](https://docs.astral.sh/uv/), which installs Sphinx on the fly.

To build once without the server, as `deploy-lfs-docs.sh` does:

```bash
uv run --no-project --with-requirements docs/requirements.txt python -m sphinx -b html docs docs/_build/html
```

The built documentation is in `docs/_build/html/index.html`.

## Available Commands

- `make help` - Show all available commands
- `make install` - Install required dependencies
- `make html` - Build HTML documentation
- `make clean` - Clean build directory
- `make spelling` - Check spelling (requires enchant library)
- `make linkcheck` - Check external links

## Requirements

- Python 3.12+
- Sphinx 8.2+
- sphinx-rtd-theme 3
- sphinxcontrib-spelling (optional, for spell checking)

`make html` must finish without warnings; `sphinx-build -W` checks that. The site at https://docs.django-lfs.com is
built from this folder.

## Theme

The documentation uses `sphinx-rtd-theme`. `_templates/layout.html` (sidebar header) and `_static/custom.css` (colours, fonts) give it the look of https://django-lfs.com; the fonts are self-hosted in `_static/fonts/`.

## Structure

- `conf.py` - Sphinx configuration
- `index.rst` - Main documentation index
- `requirements.txt` - Python dependencies
- `Makefile` - Build commands
- `build_docs.py` - Python build script
- `_static/` - Static files (CSS, images)
- `_templates/` - Template overrides for the theme
