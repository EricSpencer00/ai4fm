"""
Sphinx configuration file.

Copyright (C) 2025 George K. Thiruvathukal.
"""

# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

import datetime
import re
from operator import itemgetter
from pathlib import Path

from docutils import nodes
from sphinx.application import Sphinx

project = "AI4FM | AI for Formal Methods"
copyright = f"{datetime.datetime.now(datetime.timezone.utc).year}, AI4FM Research Group"  # ruff: ignore[builtin-variable-shadowing]
author = "AI4FM Research Group"
release = "0.0.1"

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    "ablog",
    "sphinx.ext.autosectionlabel",
    "sphinx.ext.intersphinx",
    "sphinx_copybutton",
    "sphinx_design",
    "sphinx_togglebutton",
    "sphinxcontrib.youtube",
    "sphinxext.opengraph",
    "sphinx_sitemap",
]

templates_path = ["_templates"]
exclude_patterns = ["drafts/**", "archive/**", "_themes/**"]

# Ablog configuration options
blog_authors = {
    "AI4FM": ("AI4FM Research Group", "https://github.com/LoyolaChicagoCS/ai4fm"),
    "GKT": ("George K. Thiruvathukal", "https://gkt.sh/"),
    "KL": ("Konstantin Läufer", "https://laufer.cs.luc.edu/"),
    "MA": ("Mohammed Abuhamad", "https://abuhamad.cs.luc.edu/"),
    "TNW": ("TaiNing Wang", "https://taining.github.io/"),
    "AB": ("Arslan Bisharat", "https://marslan.cs.luc.edu/"),
}
blog_default_author = "AI4FM"
blog_languages = {
    "en": ("English", None),
}
blog_default_language = "en"
post_show_prev_next = False
blog_title = "AI4FM Research Updates"
blog_feed_fulltext = True

# Sphinx auto section label settings
autosectionlabel_prefix_document = True
autosectionlabel_maxdepth = 2

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "ai4fm"
html_theme_path = ["_themes"]
html_static_path = ["_static"]
html_extra_path = ["CNAME", "favicon.ico"]
html_css_files = []
html_baseurl = "https://ai4fm.cs.luc.edu/"
html_favicon = "_static/images/logo-dark.png"

html_theme_options = {}
html_sidebars = {"**": []}
html_title = project

# Sitemap settings
sitemap_url_scheme = "{link}"

# OpenGraph / social preview tags
ogp_site_url = "https://ai4fm.cs.luc.edu/"
ogp_image = "https://ai4fm.cs.luc.edu/_static/images/logo-light.png"
ogp_description_length = 200
ogp_type = "website"
ogp_custom_meta_tags = [
    (
        '<meta name="description" content="AI4FM — AI for Formal Methods '
        "research group at Loyola University Chicago. Advancing TLA+, formal "
        'verification, and LLM evaluation for rigorous system design.">'
    ),
    (
        '<meta name="keywords" content="formal methods, TLA+, LLMs, model '
        'checking, Loyola University Chicago, AI, verification">'
    ),
    '<meta name="twitter:card" content="summary">',
    (
        '<meta name="google-site-verification" '
        'content="04K9THhTvTqHTgt9pjOMw5pqkSi5_83nQCXMMrDnFsc" />'
    ),
]


# Index the existing CMS documents at build time so new papers and posts appear
# on the homepage automatically, without duplicating titles or page content.
def homepage_context(
    app: Sphinx,
    pagename: str,
    _templatename: str,
    context: dict[str, object],
    _doctree: nodes.document | None,
) -> None:
    """Populate the homepage from existing paper and post source documents."""
    if pagename != "index":
        return
    research, news = [], []
    for docname in sorted(app.env.found_docs):
        if not docname.startswith(("papers/", "posts/")) or docname.endswith("/index"):
            continue
        source = Path(app.env.doc2path(docname)).read_text(encoding="utf-8")
        fields = dict(re.findall(r"^:([^:]+):\s*(.*)$", source, re.MULTILINE))
        item = {"docname": docname, "title": app.env.titles[docname].astext()}
        if docname.startswith("papers/"):
            item.update(
                status=fields.get("Status", ""),
                venue=fields.get("Venue", ""),
                authors=fields.get("Authors", ""),
            )
            research.append(item)
        elif fields.get("blogpost", "").lower() == "true":
            date = datetime.datetime.strptime(fields["date"], "%B %d, %Y").replace(
                tzinfo=datetime.timezone.utc
            )
            item.update(
                date=date.strftime("%B %d, %Y"), iso_date=date.date().isoformat()
            )
            news.append(item)
    # Preserve the research index's editorial order; newly added pages follow it.
    paper_index = Path(app.srcdir, "papers/index.rst").read_text(encoding="utf-8")
    ordered = re.findall(r"\.\. button-link:: ([\w-]+)/", paper_index)
    positions = {"papers/" + slug: index for index, slug in enumerate(ordered)}
    context["research_pages"] = sorted(
        research,
        key=lambda paper: (
            positions.get(paper["docname"], len(positions)),
            paper["title"],
        ),
    )
    context["news_pages"] = sorted(news, key=itemgetter("iso_date"), reverse=True)


def setup(app: Sphinx) -> None:
    """Register homepage data preparation with Sphinx."""
    app.connect("html-page-context", homepage_context)
