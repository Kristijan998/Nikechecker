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
STATE_FILE = os.environ.get("STATE_FILE", "state.json")
DEBUG = os.environ.get("DEBUG", "") == "1"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "sl-SI,sl;q=0.9,en;q=0.8",
}

SIZE_KEYS = ("localizedSize", "nikeSize", "sizeLabel", "size")


def fetch_html(url):
    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read().decode("utf-8", "replace")


def extract_next_data(html_text):
    m = re.search(
        r'<script id="__NEXT_DATA__"[^>]*>(.*?)</script>', html_text, re.S
    )
    if m:
        try:
            return json.loads(m.group(1))
        except Exception:
            return None
    return None


def normalize(s):
    return (
        str(s).upper().replace("EU", "").replace("M ", "").replace("W ", "").strip()
    )


def walk(node, found):
    if isinstance(node, dict):
        size = None
        for k in SIZE_KEYS:
            if isinstance(node.get(k), str) and node.get(k).strip():
                size = node[k]
                break
        avail = None
        if isinstance(node.get("available"), bool):
            avail = node["available"]
        elif isinstance(node.get("level"), str):
            avail = node["level"].upper() in ("IN_STOCK", "LOW")
        if size is not None and avail is not None:
            found[normalize(size)] = avail
        for v in node.values():
            walk(v, found)
    elif isinstance(node, list):
        for v in node:
            walk(v, found)


def get_availability(url):
    data = extract_next_data(fetch_html(url))
    found = {}
    if data:
        walk(data, found)
    return found


def load_state():
    try:
        with open(STATE_FILE) as f:
            return json.load(f)
    except Exception:
        return {"available": False}


def save_state(st):
    with open(STATE_FILE, "w") as f:
        json.dump(st, f)


def telegram(msg):
    if not TG_TOKEN or not TG_CHAT:
        print("[telegram] manjka token/chat_id - preskakujem obvestilo")
        return
    url = "https://api.telegram.org/bot%s/sendMessage" % TG_TOKEN
    payload = urllib.parse.urlencode(
        {"chat_id": TG_CHAT, "text": msg, "disable_web_page_preview": "false"}
    ).encode()
    try:
        urllib.request.urlopen(
            urllib.request.Request(url, data=payload), timeout=20
        ).read()
        print("[telegram] obvestilo poslano")
    except Exception as e:
        print("[telegram] napaka:", e)


def main():
    try:
        html_text = fetch_html(NIKE_URL)
        print("Dolzina odgovora:", len(html_text))
        print("Ima __NEXT_DATA__:", "__NEXT_DATA__" in html_text)
        print("Prvih 600 znakov:")
        print(html_text[:600])
        print("--- konec diagnostike ---")
        data = extract_next_data(html_text)
        found = {}
        if data:
            walk(data, found)
    except Exception as e:
        print("Napaka pri prenosu strani (mozna blokada):", e)
        sys.exit(0)

    if DEBUG:
        print("Najdene velikosti -> na zalogi:")
        for k in sorted(found):
            print("  EU %s: %s" % (k, found[k]))

    if not found:
        print("OPOZORILO: nisem nasel podatkov o velikostih.")
        sys.exit(0)

    if not TARGET_SIZE:
        print("Nastavi TARGET_SIZE. Razpolozljive velikosti:")
        print("  " + ", ".join(sorted(found)))
        sys.exit(0)

    avail = found.get(TARGET_SIZE)
    if avail is None:
        print("Velikost EU %s ni na seznamu. Najdene: %s"
              % (TARGET_SIZE, ", ".join(sorted(found))))
        sys.exit(0)

    st = load_state()
    print("Velikost EU %s: %s" % (TARGET_SIZE, "NA ZALOGI" if avail else "ni na zalogi"))

    if avail and not st.get("available"):
        telegram(
            "\u2705 Nike AF1 Flyknit 2.0 (bela) EU %s je NA ZALOGI!\n%s"
            % (TARGET_SIZE, NIKE_URL)
        )
        save_state({"available": True})
    elif not avail and st.get("available"):
        save_state({"available": False})


if __name__ == "__main__":
    main()
