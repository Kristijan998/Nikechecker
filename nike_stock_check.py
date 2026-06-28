#!/usr/bin/env python3
import os
import re
import sys
import json
import urllib.request
import urllib.parse

NIKE_URL = os.environ.get(
    "NIKE_URL",
    "https://www.nike.com/si/t/air-force-1-flyknit-2-shoes-7EHtWGRa/AV3042-100",
)
TARGET_SIZE = os.environ.get("TARGET_SIZE", "45").strip().upper().replace("EU", "").strip()
TG_TOKEN = os.environ.get("TELEGRAM_TOKEN", "")
TG_CHAT = os.environ.get("TELEGRAM_CHAT_ID", "")

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "sl-SI,sl;q=0.9,en;q=0.8",
}


def fetch_html(url):
    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read().decode("utf-8", "replace")


def extract_next_data(html_text):
    m = re.search(r'<script id="__NEXT_DATA__"[^>]*>(.*?)</script>', html_text, re.S)
    if m:
        try:
            return json.loads(m.group(1))
        except Exception as e:
            print("JSON parse napaka:", e)
            return None
    return None


def find_keys(node, target_keys, results, path=""):
    if isinstance(node, dict):
        for k, v in node.items():
            if k in target_keys and not isinstance(v, (dict, list)):
                results.append("%s.%s = %r" % (path, k, v))
            find_keys(v, target_keys, results, path + "." + k)
    elif isinstance(node, list):
        for i, v in enumerate(node[:30]):
            find_keys(v, target_keys, results, path + "[%d]" % i)


def main():
    html_text = fetch_html(NIKE_URL)
    data = extract_next_data(html_text)
    if not data:
        print("Ni __NEXT_DATA__ JSON.")
        sys.exit(0)

    keys_to_find = {
        "localizedSize", "nikeSize", "sizeLabel", "size", "label",
        "available", "level", "availability", "stockLevel", "inStock",
        "value", "gtin", "skuId",
    }
