import os, re, json, urllib.request, urllib.parse

GTIN = os.environ.get("GTIN", "00192499276124")
SIZE_LABEL = os.environ.get("SIZE_LABEL", "11")
URL = os.environ.get("NIKE_URL", "https://www.nike.com/si/t/air-force-1-flyknit-2-shoes-7EHtWGRa/AV3042-100")
TG_TOKEN = os.environ.get("TELEGRAM_TOKEN", "")
TG_CHAT = os.environ.get("TELEGRAM_CHAT_ID", "")
STATE_FILE = "state.json"

HEADERS = {
    "User-Agent": ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                   "(KHTML, like Gecko) Chrome/124.0 Safari/537.36"),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "sl-SI,sl;q=0.9,en;q=0.8",
}


def fetch():
    req = urllib.request.Request(URL, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read().decode("utf-8", "replace")


def telegram(msg):
    if not TG_TOKEN or not TG_CHAT:
        print("Ni TG nastavitev - preskakujem")
        return
    u = "https://api.telegram.org/bot%s/sendMessage" % TG_TOKEN
    d = urllib.parse.urlencode({"chat_id": TG_CHAT, "text": msg,
                                "disable_web_page_preview": "false"}).encode()
    try:
        urllib.request.urlopen(urllib.request.Request(u, data=d), timeout=20).read()
        print("Telegram poslan")
    except Exception as e:
        print("Telegram napaka:", e)


def load_state():
    try:
        with open(STATE_FILE) as f:
            return json.load(f)
    except Exception:
        return {"available": False}


def save_state(st):
    with open(STATE_FILE, "w") as f:
        json.dump(st, f)


def check_availability(html):
    idx = html.find(GTIN)
    if idx != -1:
        window = html[idx: idx + 1200]
        m = re.search(r'schema\.org/(InStock|OutOfStock|BackOrder|PreOrder|SoldOut)', window)
        if m:
            return m.group(1) in ("InStock", "BackOrder", "PreOrder")
        m = re.search(r'"availability"\s*:\s*"([^"]+)"', window)
        if m:
            return "InStock" in m.group(1) or "in_stock" in m.group(1).lower()

    m = re.search(r'<script id="__NEXT_DATA__"[^>]*>(.*?)</script>', html, re.S)
    if m:
        try:
            data = json.loads(m.group(1))
        except Exception:
            data = None
        if data is not None:
            hits = []

            def walk(n):
                if isinstance(n, dict):
                    label = None
                    for kk in ("localizedSize", "nikeSize", "sizeLabel", "label", "size"):
                        v = n.get(kk)
                        if isinstance(v, str):
                            label = v
                            break
                    avail = None
                    if isinstance(n.get("available"), bool):
                        avail = n["available"]
                    elif isinstance(n.get("level"), str):
                        avail = n["level"].upper() in ("IN_STOCK", "LOW", "HIGH", "MEDIUM")
                    elif isinstance(n.get("availability"), str):
                        avail = "instock" in n["availability"].replace("/", "").lower()
                    g = n.get("gtin") if isinstance(n.get("gtin"), str) else None
                    if avail is not None and (label == SIZE_LABEL or g == GTIN):
                        hits.append(avail)
                    for v in n.values():
                        walk(v)
                elif isinstance(n, list):
                    for v in n:
                        walk(v)

            walk(data)
            if hits:
                return any(hits)

    return None


def main():
    try:
        html = fetch()
    except Exception as e:
        print("Napaka pri prenosu:", e)
        return

    avail = check_availability(html)
    st = load_state()
    print("Velikost EU 45 (US %s, GTIN %s) -> zaloga: %s" % (SIZE_LABEL, GTIN, avail))

    if avail is True and not st.get("available"):
        telegram("\u2705 Nike AF1 Flyknit 2.0 (bela) EU 45 je NA ZALOGI!\n" + URL)
        save_state({"available": True})
    elif avail is False and st.get("available"):
        save_state({"available": False})
    elif avail is None:
        print("OPOZORILO: ne morem zaznati zaloge - format strani se je morda spremenil.")


if __name__ == "__main__":
    main()
