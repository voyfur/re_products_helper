from __future__ import annotations

import re
from dataclasses import dataclass
from html.parser import HTMLParser


@dataclass(frozen=True)
class Attribute:
    name: str
    value: str


@dataclass(frozen=True)
class LanguageCard:
    language: str
    name: str | None
    description: str | None
    attributes: tuple[Attribute, ...]
    stock_label: str | None


@dataclass(frozen=True)
class Product:
    product_id: int
    article: str
    model: str | None
    sku: str | None
    languages: dict[str, LanguageCard]


class _DescriptionTextParser(HTMLParser):
    _UNSAFE_TAGS = {
        "embed",
        "iframe",
        "math",
        "noscript",
        "object",
        "script",
        "style",
        "svg",
        "template",
    }
    _BLOCK_TAGS = {
        "article",
        "blockquote",
        "br",
        "dd",
        "div",
        "dl",
        "dt",
        "h1",
        "h2",
        "h3",
        "h4",
        "h5",
        "h6",
        "li",
        "ol",
        "p",
        "section",
        "ul",
    }

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.output: list[str] = []
        self.skip_depth = 0
        self.table_depth = 0
        self.headers: list[str] | None = None
        self.row: list[str] | None = None
        self.cell: list[str] | None = None
        self.row_has_header = False

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if self.skip_depth:
            if tag in self._UNSAFE_TAGS:
                self.skip_depth += 1
            return
        if tag in self._UNSAFE_TAGS:
            self.skip_depth = 1
            return
        if tag == "table":
            self.table_depth += 1
            self.headers = None
            return
        if tag == "tr":
            self.row = []
            self.row_has_header = False
            return
        if tag in {"th", "td"} and self.row is not None:
            self.cell = []
            self.row_has_header = self.row_has_header or tag == "th"
            return
        if tag == "li":
            self._newline()
            self.output.append("• ")
        elif tag in self._BLOCK_TAGS:
            self._newline()

    def handle_endtag(self, tag: str) -> None:
        if self.skip_depth:
            if tag in self._UNSAFE_TAGS:
                self.skip_depth -= 1
            return
        if tag in {"th", "td"} and self.row is not None and self.cell is not None:
            self.row.append(self._clean_cell("".join(self.cell)))
            self.cell = None
            return
        if tag == "tr" and self.row is not None:
            self._finish_row()
            self.row = None
            return
        if tag == "table" and self.table_depth:
            self.table_depth -= 1
            self.headers = None
            self._newline()
            return
        if tag in self._BLOCK_TAGS:
            self._newline()

    def handle_data(self, data: str) -> None:
        if self.skip_depth:
            return
        if self.cell is not None:
            self.cell.append(data)
        else:
            self.output.append(data)

    def text(self) -> str:
        return re.sub(r"[ \t]*\n[ \t]*", "\n", "".join(self.output)).strip()

    def _finish_row(self) -> None:
        cells = [cell for cell in self.row or [] if cell]
        if not cells:
            return
        if self.row_has_header:
            self.headers = cells
            return
        self._newline()
        if self.headers and len(self.headers) == len(cells):
            self.output.append(
                "; ".join(
                    f"{label}: {value}"
                    for label, value in zip(self.headers, cells)
                    if label or value
                )
            )
        else:
            self.output.append(" | ".join(cells))
        self._newline()

    def _newline(self) -> None:
        if not self.output:
            return
        if not self.output[-1].endswith("\n"):
            self.output.append("\n")

    @staticmethod
    def _clean_cell(value: str) -> str:
        return re.sub(r"\s+", " ", value).strip()


def html_to_safe_text(description: str | None) -> str:
    if not description:
        return ""
    parser = _DescriptionTextParser()
    parser.feed(description)
    parser.close()
    return parser.text()


def build_model_context(product: Product, language: str) -> str:
    lines = [f"Артикул: {product.article}"]
    if product.model:
        lines.append(f"Модель: {product.model}")
    if product.sku:
        lines.append(f"SKU: {product.sku}")

    localized = product.languages.get(language)
    if localized is None:
        return "\n".join(lines)

    if localized.name:
        lines.append(f"Название: {localized.name}")
    description = html_to_safe_text(localized.description)
    if description:
        lines.append(f"Описание: {description}")
    for attribute in localized.attributes:
        if attribute.name and attribute.value:
            lines.append(f"{attribute.name}: {attribute.value}")
    if localized.stock_label:
        lines.append(f"Наличие: {localized.stock_label}")
    return "\n".join(lines)
