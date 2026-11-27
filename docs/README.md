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
- Sphinx 9.2+
- sphinx-rtd-theme (optional, for modern theme)
- sphinxcontrib-spelling (optional, for spell checking)

`make html` must finish without warnings; `sphinx-build -W` checks that. The site at https://docs.django-lfs.com is
built from this folder.

## Theme

The documentation uses a custom theme (`lfstheme`) with fallback to `sphinx-rtd-theme` if available. The custom theme is located in the `lfstheme/` directory.

## Structure

- `conf.py` - Sphinx configuration
- `index.rst` - Main documentation index
- `requirements.txt` - Python dependencies
- `Makefile` - Build commands
- `build_docs.py` - Python build script
- `_static/` - Static files (CSS, images)
- `lfstheme/` - Custom theme files
