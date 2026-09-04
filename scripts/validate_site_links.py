#!/usr/bin/env python3
"""Validate local links and assets for the GitHub Pages site."""

from __future__ import annotations

from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urljoin, urlparse

SITE_PREFIX = "/iot-weekly-report/"
SITE_ORIGIN = "https://pages.example"


class ReferenceParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.references: list[tuple[str, str, str]] = []

    def handle_starttag(
        self, tag: str, attrs: list[tuple[str, str | None]]
    ) -> None:
        values = dict(attrs)
        for attribute in ("href", "src"):
            value = values.get(attribute)
            if value:
                self.references.append((tag, attribute, value))


def public_html_files(root: Path) -> list[Path]:
    files = [root / "index.html", root / "internal-brief" / "index.html"]
    files.extend(sorted((root / "archive").glob("*.html")))
    return [path for path in files if path.is_file()]


def local_target(root: Path, page: Path, reference: str) -> Path | None:
    if reference.startswith(("#", "data:", "mailto:", "javascript:")):
        return None

    relative_page = page.relative_to(root).as_posix()
    page_url = urljoin(f"{SITE_ORIGIN}{SITE_PREFIX}", relative_page)
    resolved = urlparse(urljoin(page_url, reference))

    if resolved.netloc != urlparse(SITE_ORIGIN).netloc:
        return None
    if not resolved.path.startswith(SITE_PREFIX):
        return None

    relative_target = resolved.path.removeprefix(SITE_PREFIX)
    target = root / relative_target
    if resolved.path.endswith("/"):
        target /= "index.html"
    return target


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    errors: list[str] = []
    checked = 0

    for page in public_html_files(root):
        parser = ReferenceParser()
        parser.feed(page.read_text(encoding="utf-8"))
        for tag, attribute, reference in parser.references:
            target = local_target(root, page, reference)
            if target is None:
                continue
            checked += 1
            if not target.is_file():
                errors.append(
                    f"{page.relative_to(root)}: <{tag} {attribute}=\"{reference}\"> "
                    f"resolves to missing {target.relative_to(root)}"
                )

    if errors:
        print(f"FAIL: {len(errors)} broken local reference(s)")
        for error in errors:
            print(error)
        return 1

    print(f"PASS: {checked} local reference(s) resolve to published files")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
