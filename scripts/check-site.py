"""
Check generated links and automatic homepage coverage.

Copyright (C) 2026 AI4FM Research Group.
"""

import sys
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit


class Page(HTMLParser):
    """Collect generated links and main landmarks for a page."""

    def __init__(self, text: str) -> None:
        """Parse a generated HTML document."""
        super().__init__()
        self.links = []
        self.ids = set()
        self.main_count = 0
        self.main_roles = []
        self.feed(text)

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        """Record landmarks, identifiers, and asset or page references."""
        attrs = dict(attrs)
        if tag == "main":
            self.main_count += 1
            self.main_roles.append(attrs.get("role"))
        if "id" in attrs:
            self.ids.add(attrs["id"])
        for attr in ("href", "src"):
            if attrs.get(attr):
                self.links.append(attrs[attr])


root = Path(__file__).resolve().parents[1]
build = root / "build"
errors = []
if not (build / "sitemap.xml").is_file():
    errors.append("Missing sitemap")
pages = {}
# dirhtml output only; exclude the standalone demonstration app.
for path in build.rglob("index.html"):
    if "_static" in path.parts:
        continue
    page = Page(path.read_text())
    pages[path.resolve()] = page
    if page.main_count != 1 or page.main_roles != ["main"]:
        errors.append(f"{path}: expected one main landmark")
    for value in page.links:
        url = urlsplit(value)
        if url.scheme or url.netloc or not url.path:
            continue
        target = (
            (build / unquote(url.path).lstrip("/"))
            if url.path.startswith("/")
            else path.parent / unquote(url.path)
        ).resolve()
        if not target.exists():
            errors.append(f"{path.relative_to(build)}: missing {value}")

home = pages[(build / "index.html").resolve()]
home_targets = {
    (build / urlsplit(link).path).resolve()
    for link in home.links
    if not urlsplit(link).scheme
}
counts = {}
for section in ("papers", "posts"):
    sources = [p for p in (root / "src" / section).glob("*.rst") if p.stem != "index"]
    counts[section] = len(sources)
    for source in sources:
        target = (build / section / source.stem).resolve()
        if target not in home_targets:
            errors.append(f"Homepage is missing {section}/{source.stem}")
        if (target / "index.html") not in pages:
            errors.append(f"Missing dedicated page: {section}/{source.stem}")

if errors:
    sys.exit("\n".join(errors))
sys.stdout.write(
    f"Verified {len(pages)} pages, local links, sitemap, and homepage coverage: "
    f"{counts['papers']} research entries, {counts['posts']} news posts.\n"
)
