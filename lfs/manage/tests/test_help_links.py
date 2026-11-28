"""The help links of the management interface lead to existing pages of the documentation.

Each management template names its help page in ``{% block help_link %}``; the help menu opens
``LFS_DOCS`` + that path, so a renamed or mistyped page gives the shop manager a 404.
"""

import re
from pathlib import Path

import lfs

LFS = Path(lfs.__file__).resolve().parent
DOCS = LFS.parent / "docs"
HELP_LINK = re.compile(r"{%\s*block help_link\s*%}(.*?){%\s*endblock")


def help_links() -> dict[str, str]:
    """Return the help link of every management template that has one, by template path."""
    links = {}
    for template in sorted((LFS / "manage" / "templates").rglob("*.html")):
        match = HELP_LINK.search(template.read_text())
        if match and match.group(1).strip():
            links[str(template.relative_to(LFS))] = match.group(1).strip()
    return links


def test_every_help_link_points_to_a_page_of_the_docs():
    assert help_links(), "no help links found; did the templates move?"
    missing = {
        template: link
        for template, link in help_links().items()
        if link.startswith("/") or not (DOCS / link).with_suffix(".rst").is_file()
    }
    assert missing == {}
