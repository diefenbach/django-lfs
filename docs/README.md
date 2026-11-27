# Django-LFS Documentation

This directory contains the Sphinx-based documentation for django-lfs.

## Quick Start

### Install Dependencies

```bash
# Install required packages
make install
# or
pip install -r requirements.txt
```

### Build Documentation

```bash
# Build HTML documentation
make html

# Or use the Python script
python3 build_docs.py
```

The built documentation will be available in `_build/html/index.html`.

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
