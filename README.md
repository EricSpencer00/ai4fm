# AI4FM Website

Source for [ai4fm.cs.luc.edu](https://ai4fm.cs.luc.edu), the AI for Formal Methods research group at Loyola University Chicago.

## Local development

Requires Python 3.13 and [uv](https://docs.astral.sh/uv/).

```sh
uv sync
make build-site
make serve
```

The preview is served at http://127.0.0.1:8000. Both local development and GitHub Pages use Sphinx's `dirhtml` builder so page URLs stay consistent.

## Content

- `src/papers/`: one source file per paper, presentation, poster, or artifact. Keep the existing title and `Status`, `Venue`, `Authors`, and `DOI / PDF` fields. Each source becomes its own page.
- `src/posts/`: one source file per news post. Use the existing `blogpost`, `date` (for example `June 5, 2026`), `author`, `category`, and `tags` fields.
- `src/pages/`: team, software, about, funding, and participation pages.

The homepage discovers every paper and news post at build time. News is sorted newest first. Research follows the order in `src/papers/index.rst`, with new unlisted papers appended automatically. The homepage lists existing titles and metadata without generating copy.

Use Sphinx `:doc:` links for internal pages and `:download:` links for downloadable files; these survive changes in page depth and news excerpts.

## Design

`src/_themes/ai4fm/` contains the shared layout and stylesheet. The theme uses the selected maroon-and-paper design, the compact `ai4fm @ luc.edu` header, Source Serif 4 and Libre Franklin, and 100 ms hover feedback. Reduced-motion preferences disable transitions. Fonts have local fallbacks.

The root `index.html` opens the generated homepage after a build. Use `make serve` to browse the complete site locally.

## Verification

```sh
make check-site
```

This builds with warnings treated as errors and checks generated internal links, shared page structure, and complete homepage coverage of papers and news.

## Deployment

The existing GitHub Actions workflow builds and deploys `build/` to GitHub Pages when changes are pushed to `main`, or when the workflow is run manually. Local previewing does not publish changes.
