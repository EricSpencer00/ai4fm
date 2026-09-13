"""
Check generated links and automatic homepage coverage.

Copyright (C) 2026 AI4FM Research Group.
"""

import re
import sys
from json import JSONDecodeError, loads
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit

SITE_URL = "https://ai4fm.cs.luc.edu/"
NOINDEX_PREFIXES = ("blog", "genindex", "search")
MAX_DESCRIPTION_LENGTH = 160
SITEMAP_LOC_RE = re.compile(r"<loc>([^<]+)</loc>")
IMAGE_SUFFIXES = {".gif", ".jpeg", ".jpg", ".png", ".svg", ".webp"}


class Page(HTMLParser):
    """Collect generated links, metadata, and main landmarks for a page."""

    def __init__(self, text: str) -> None:
        """Parse a generated HTML document."""
        super().__init__()
        self.links = []
        self.ids = set()
        self.main_count = 0
        self.main_roles = []
        self.canonicals = []
        self.meta = []
        self.json_ld = []
        self._json_ld_chunks = None
        self.feed(text)

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        """Record landmarks, identifiers, and asset or page references."""
        attrs = dict(attrs)
        if tag == "main":
            self.main_count += 1
            self.main_roles.append(attrs.get("role"))
        if "id" in attrs:
            self.ids.add(attrs["id"])
        if (
            tag == "link"
            and "canonical" in (attrs.get("rel") or "").split()
            and (href := attrs.get("href"))
        ):
            self.canonicals.append(href)
        if tag == "meta":
            self.meta.append(
                (
                    attrs.get("name") or attrs.get("property"),
                    attrs.get("content", ""),
                )
            )
        if tag == "script" and attrs.get("type") == "application/ld+json":
            self._json_ld_chunks = []
        for attr in ("href", "src", "data-full"):
            if attrs.get(attr):
                self.links.append(attrs[attr])

    def handle_data(self, data: str) -> None:
        """Collect JSON-LD content while its script element is open."""
        if self._json_ld_chunks is not None:
            self._json_ld_chunks.append(data)

    def handle_endtag(self, tag: str) -> None:
        """Store a complete JSON-LD script when its closing tag is reached."""
        if tag == "script" and self._json_ld_chunks is not None:
            self.json_ld.append("".join(self._json_ld_chunks))
            self._json_ld_chunks = None


root = Path(__file__).resolve().parents[1]
build = root / "build"
errors = []
if not (build / "robots.txt").is_file():
    errors.append("Missing robots.txt")
elif f"Sitemap: {SITE_URL}sitemap.xml" not in (build / "robots.txt").read_text():
    errors.append("robots.txt does not advertise the canonical sitemap")


def page_url(path: Path) -> str:
    """
    Convert a dirhtml output path to its canonical public URL.

    Returns:
        The absolute canonical URL for the output page.

    """
    relative_parent = path.parent.relative_to(build)
    suffix = "" if relative_parent == Path() else f"{relative_parent.as_posix()}/"
    return f"{SITE_URL}{suffix}"


def is_noindexable(path: Path) -> bool:
    """
    Determine whether a generated utility/archive page should stay unindexed.

    Returns:
        Whether the page should have noindex metadata.

    """
    relative_parent = path.parent.relative_to(build)
    return any(relative_parent.parts[:1] == (prefix,) for prefix in NOINDEX_PREFIXES)


pages = {}
# dirhtml output only; exclude the standalone demonstration app.
for path in build.rglob("index.html"):
    if "_static" in path.parts:
        continue
    page = Page(path.read_text())
    pages[path.resolve()] = page
    if page.main_count != 1 or page.main_roles != ["main"]:
        errors.append(f"{path}: expected one main landmark")
    if is_noindexable(path):
        if not any(
            name == "robots" and "noindex" in content.casefold()
            for name, content in page.meta
        ):
            errors.append(f"{path.relative_to(build)}: expected noindex metadata")
    else:
        descriptions = [content for name, content in page.meta if name == "description"]
        if len(descriptions) != 1:
            errors.append(f"{path.relative_to(build)}: expected one meta description")
        elif not descriptions[0] or len(descriptions[0]) > MAX_DESCRIPTION_LENGTH:
            errors.append(f"{path.relative_to(build)}: invalid meta description")
        expected_url = page_url(path)
        if page.canonicals != [expected_url]:
            errors.append(
                f"{path.relative_to(build)}: canonical URL should be {expected_url}"
            )
        og_descriptions = [
            content for name, content in page.meta if name == "og:description"
        ]
        if og_descriptions != descriptions:
            errors.append(
                f"{path.relative_to(build)}: Open Graph description should match"
            )
        og_urls = [content for name, content in page.meta if name == "og:url"]
        if og_urls != [expected_url]:
            errors.append(
                f"{path.relative_to(build)}: Open Graph URL should be {expected_url}"
            )

for path, page in pages.items():
    for value in page.links:
        url = urlsplit(value)
        if url.scheme or url.netloc or (not url.path and not url.fragment):
            continue
        target = (
            path.parent
            if not url.path
            else (
                (build / unquote(url.path).lstrip("/"))
                if url.path.startswith("/")
                else path.parent / unquote(url.path)
            )
        )
        target = target.resolve()
        if not target.exists():
            errors.append(f"{path.relative_to(build)}: missing {value}")
            continue
        target_page = target / "index.html" if target.is_dir() else target
        if (
            url.fragment
            and (target_document := pages.get(target_page))
            and unquote(url.fragment) not in target_document.ids
        ):
            errors.append(f"{path.relative_to(build)}: missing anchor {value}")

source_image_root = root / "src" / "_static" / "images"
source_images = [
    source
    for source in source_image_root.rglob("*")
    if source.is_file() and source.suffix.casefold() in IMAGE_SUFFIXES
]
for source_image in source_images:
    target_image = (
        build / "_static" / "images" / source_image.relative_to(source_image_root)
    )
    if not target_image.is_file():
        errors.append(f"Missing copied image: {source_image.relative_to(root)}")
    elif source_image.read_bytes() != target_image.read_bytes():
        errors.append(f"Changed copied image: {source_image.relative_to(root)}")

home = pages[(build / "index.html").resolve()]
if len(home.json_ld) != 1:
    errors.append("Homepage should contain one JSON-LD organization record")
else:
    try:
        organization = loads(home.json_ld[0])
    except JSONDecodeError:
        errors.append("Homepage JSON-LD is invalid")
    else:
        if organization.get("@type") != "Organization":
            errors.append("Homepage JSON-LD should describe an organization")
        if organization.get("name") != "AI4FM" or organization.get("url") != SITE_URL:
            errors.append("Homepage JSON-LD has an incorrect identity")
home_targets = set()
for link in home.links:
    url = urlsplit(link)
    if url.scheme:
        continue
    target = (build / url.path).resolve()
    home_targets.add(target / "index.html" if target.is_dir() else target)
counts = {}
for section in ("papers", "posts"):
    sources = [p for p in (root / "src" / section).glob("*.rst") if p.stem != "index"]
    counts[section] = len(sources)
    section_index = (build / section / "index.html").resolve()
    for source in sources:
        target = (build / section / source.stem).resolve()
        if target not in home_targets and section_index not in home_targets:
            errors.append(f"Homepage is missing {section}/{source.stem}")
        if (target / "index.html") not in pages:
            errors.append(f"Missing dedicated page: {section}/{source.stem}")

sitemap_path = build / "sitemap.xml"
if not sitemap_path.is_file():
    errors.append("Missing sitemap")
else:
    sitemap_urls = set(SITEMAP_LOC_RE.findall(sitemap_path.read_text()))
    source_documents = [
        source
        for source in (root / "src").rglob("*.rst")
        if source.relative_to(root / "src").parts[0] not in {"drafts", "archive"}
    ]
    expected_sitemap_urls = set()
    for source in source_documents:
        docname = source.relative_to(root / "src").with_suffix("")
        if docname.name == "index":
            docname = docname.parent
        expected_sitemap_urls.add(
            SITE_URL if docname == Path() else f"{SITE_URL}{docname.as_posix()}/"
        )
    missing_urls = expected_sitemap_urls - sitemap_urls
    unexpected_urls = sitemap_urls - expected_sitemap_urls
    if missing_urls:
        errors.append("Sitemap missing: " + ", ".join(sorted(missing_urls)))
    if unexpected_urls:
        errors.append(
            "Sitemap has unexpected URLs: " + ", ".join(sorted(unexpected_urls))
        )

if errors:
    sys.exit("\n".join(errors))
sys.stdout.write(
    f"Verified {len(pages)} pages, local links and anchors, {len(source_images)} "
    "copied images, SEO metadata, sitemap, and "
    "homepage coverage: "
    f"{counts['papers']} research entries, {counts['posts']} news posts.\n"
)
