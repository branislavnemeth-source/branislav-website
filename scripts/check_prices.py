#!/usr/bin/env python3
"""
Cenová poistka pre branislav.website.

Porovná HTML súbory (samostatné produktové stránky + katalóg licencie.html)
proti jedinému zdroju pravdy `prices.json`. Pri akomkoľvek rozdiele alebo
chýbajúcom antivíruse vypíše ľudský report a skončí s exit kódom 1.

Použitie:
    python3 scripts/check_prices.py
    python3 scripts/check_prices.py --root /cesta/k/sajtu --prices prices.json
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import unicodedata
from pathlib import Path

CATALOG_FILE = "licencie.html"


def normalise_price(text: str) -> str:
    """Zjednotí medzery vrátane NBSP a U+202F, odstráni opakovania."""
    text = unicodedata.normalize("NFKC", text)
    text = text.replace(" ", " ").replace(" ", " ")
    return re.sub(r"\s+", " ", text).strip()


def price_variants(price: str) -> list[str]:
    """Vráti varianty toho istého ceny stringu, ktoré sa môžu nájsť v HTML
    (s/bez nedeliteľnej medzery, číselná hodnota s bodkou v JS objektoch)."""
    price = normalise_price(price)
    out = {price, price.replace(" ", " "), price.replace(" ", "")}
    m = re.match(r"^(\d+),(\d+)\s*€$", price)
    if m:
        whole, frac = m.group(1), m.group(2)
        out.add(f"{whole}.{frac}")
    return list(out)


def page_contains_price(html: str, price: str) -> bool:
    normalised = normalise_price(html)
    return any(v in normalised or v in html for v in price_variants(price))


def load_prices(path: Path) -> dict:
    with path.open(encoding="utf-8") as fh:
        return json.load(fh)


def check_product_page(root: Path, product: dict) -> list[str]:
    problems: list[str] = []
    page_path = root / product["page"]
    if not page_path.is_file():
        return [f"  ✗ chýbajúca stránka produktu: {product['page']}"]
    html = page_path.read_text(encoding="utf-8")
    if not page_contains_price(html, product["price"]):
        problems.append(
            f"  ✗ {product['page']}: očakávaná hlavná cena {product['price']} nebola nájdená"
        )
    for variant in product.get("variants", []):
        if not page_contains_price(html, variant["price"]):
            problems.append(
                f"  ✗ {product['page']}: variant „{variant['label']}\" ({variant['ref']}) – "
                f"očakávaná cena {variant['price']} nebola nájdená"
            )
    return problems


def _find_all(haystack: str, needle: str) -> list[int]:
    out, start = [], 0
    while True:
        i = haystack.find(needle, start)
        if i == -1:
            return out
        out.append(i)
        start = i + 1


def check_catalog(root: Path, products: list[dict]) -> list[str]:
    catalog = root / CATALOG_FILE
    if not catalog.is_file():
        return [f"  ✗ chýba katalóg {CATALOG_FILE}"]
    html = catalog.read_text(encoding="utf-8")
    problems: list[str] = []
    for p in products:
        # Hľadáme výskyt názvu v JS objekte produktu: `name: "..."`.
        marker = f'name: "{p["name"]}"'
        positions = _find_all(html, marker)
        if not positions:
            # fallback: surový názov, ak by sa formát zápisu menil
            positions = _find_all(html, p["name"])
            if not positions:
                problems.append(
                    f"  ✗ katalóg {CATALOG_FILE}: chýba produkt „{p['name']}\""
                )
                continue
        # Skontroluj cenu v okne 600 znakov za najbližším výskytom v PRODUCTS bloku.
        matched = False
        found_price = None
        for pos in positions:
            window = html[pos : pos + 600]
            current = re.search(r'price:\s*"?([0-9]+[,.][0-9]+ ?€?)"?', window)
            if current:
                found_price = current.group(1)
                if page_contains_price(window, p["price"]):
                    matched = True
                    break
        if not matched:
            problems.append(
                f"  ✗ katalóg {CATALOG_FILE}: „{p['name']}\" – očakávaná cena "
                f"{p['price']}, v katalógu nájdená {found_price or '?'}"
            )
    return problems


def main() -> int:
    parser = argparse.ArgumentParser(description="Cenová poistka pre branislav.website")
    parser.add_argument("--root", default=".", help="Koreňový adresár stránky (default: .)")
    parser.add_argument("--prices", default="prices.json", help="Cesta k cenníku")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    prices_path = (root / args.prices).resolve() if not Path(args.prices).is_absolute() else Path(args.prices)

    if not prices_path.is_file():
        print(f"[chyba] Nenašiel som cenník {prices_path}", file=sys.stderr)
        return 2

    data = load_prices(prices_path)
    products = data.get("products", [])

    print(f"== Cenová poistka pre branislav.website ==")
    print(f"Cenník: {prices_path}")
    print(f"Koreň:  {root}")
    print(f"Produktov v cenníku: {len(products)}")

    all_problems: list[tuple[str, list[str]]] = []

    cat_problems = []
    required = data.get("required_categories", [])
    present_cats = {p["category"] for p in products}
    for cat in required:
        if cat not in present_cats:
            cat_problems.append(
                f"  ✗ KRITICKÉ: chýba celá povinná kategória „{cat}\""
            )
    if "antivirus" in required and not any(
        p["category"] == "antivirus" for p in products
    ):
        cat_problems.append(
            "  ✗ KRITICKÉ: V cenníku nie je žiadny antivírusový produkt."
        )
    if cat_problems:
        all_problems.append(("Povinné kategórie", cat_problems))

    page_problems: list[str] = []
    for product in products:
        page_problems.extend(check_product_page(root, product))
    if page_problems:
        all_problems.append(("Produktové stránky", page_problems))

    catalog_problems = check_catalog(root, products)
    if catalog_problems:
        all_problems.append((f"Katalóg {CATALOG_FILE}", catalog_problems))

    if not all_problems:
        print()
        print("✓ Všetky ceny súhlasia s cenníkom prices.json.")
        print("✓ Všetky povinné kategórie (vrátane antivírusu) sú prítomné.")
        print("✓ Publikácia môže pokračovať.")
        return 0

    print()
    print("✗ Cenová poistka zastavila publikáciu. Nájdené rozdiely:")
    print()
    total = 0
    for section, items in all_problems:
        print(f"[{section}]")
        for line in items:
            print(line)
            total += 1
        print()
    print(f"Spolu {total} problém(ov). Oprav prices.json alebo HTML a spusti znova.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
