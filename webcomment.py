#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import pathlib
import re
import sys
import urllib.error
import urllib.request
from argparse import RawTextHelpFormatter
from typing import Final


# ─────────────────────────── NETWORK ────────────────────────────
def fetch_page_content(url: str) -> str:
    request = urllib.request.Request(url, method="GET")
    try:
        with urllib.request.urlopen(request) as resp:
            return resp.read().decode("utf-8", errors="ignore")
    except urllib.error.URLError:
        print(f"[!] Could not access: {url}")
        return ""


# ─────────────────────────── PARSING ────────────────────────────
def extract_html_comments(html: str) -> list[str]:
    return re.findall(r"<!--(.*?)-->", html, flags=re.DOTALL)


def is_comment_valid(comment: str, filters: set[str]) -> bool:
    return comment.strip() not in filters


# ────────────────────────── AUXILIARY ───────────────────────────
def load_filters(path: str | None) -> set[str]:
    if not path:
        return set()

    try:
        with open(path, encoding="utf-8") as fh:
            return {line.strip() for line in fh if line.strip()}
    except Exception:
        print(f"[!] Invalid filter file path: {path}")
        return set()


# ─────────────────────────── LOGIC ─────────────────────────────
def process_single_target(url: str, filters: set[str]) -> dict[str, list[str]] | None:
    html = fetch_page_content(url)
    if not html:
        return None

    html_flat = html.replace("\n", "")
    comments = [
        c.strip()
        for c in extract_html_comments(html_flat)
        if is_comment_valid(c, filters)
    ]
    return {"target": url, "content": comments} if comments else None


def process_targets_file(path: str, filters: set[str]) -> list[dict[str, list[str]]]:
    results: list[dict[str, list[str]]] = []
    try:
        with open(path, encoding="utf-8") as fh:
            for line in fh:
                url = line.strip()
                if url:
                    if data := process_single_target(url, filters):
                        results.append(data)
    except Exception:
        print(f"[!] Invalid URL file path: {path}")
    return results


# ──────────────────────────── CLI ──────────────────────────────
def parse_arguments() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="Collect HTML comments and save as JSON.",
        formatter_class=RawTextHelpFormatter,
    )
    p.add_argument("--mode", choices=["url", "urls"], required=True,
                   help="url – одиночный адрес; urls – файл с адресами")
    p.add_argument("--target", required=True,
                   help="URL (mode=url) или путь к файлу (mode=urls)")
    p.add_argument("--filter", help="Файл со строками, которые нужно игнорировать")
    p.add_argument("--output", default="comments.json",
                   help="Выходной JSON‑файл")
    return p.parse_args()


# ──────────────────────────── MAIN ─────────────────────────────
def main() -> None:
    args = parse_arguments()
    filter = args.filter
    mode = args.mode
    target = args.target
    output = args.output

    MAIN_DIR: Final[pathlib.Path] = pathlib.Path(__file__).resolve().parents[0]
    OUTPUT_JSON: Final[pathlib.Path] = MAIN_DIR / output

    filters = load_filters(filter)

    if mode == "url":
        results = [process_single_target(target, filters)]
    else:
        results = process_targets_file(target, filters)

    results = [r for r in results if r]

    if not results:
        results = {"Message": "No comments found in provided targets"}
        exit(1)

    with OUTPUT_JSON.open("w", encoding="utf-8") as jf:
        json.dump(results, jf, ensure_ascii=False, indent=2)
    print(f"[+] Saved: {OUTPUT_JSON}")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(0)
