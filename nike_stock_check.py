import os, re, sys, json, urllib.request, urllib.parse

NIKE_URL = os.environ.get("NIKE_URL", "https://www.nike.com/si/t/air-force-1-flyknit-2-shoes-7EHtWGRa/AV3042-100")

def fetch_html(url):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36", "Accept-Language": "sl-SI,sl;q=0.9,en;q=0.8"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read().decode("utf-8", "replace")

def main():
    html = fetch_html(NIKE_URL)
    m = re.search(r'<script id="__NEXT_DATA__"[^>]*>(.*?)</script>', html, re.S)
    if not m:
        print("Ni NEXT_DATA"); return
    data = json.loads(m.group(1))
    keys = {"localizedSize","nikeSize","sizeLabel","size","label","available","level","availability","stockLevel","inStock","value","gtin","skuId"}
    out = []
    def walk(n, p=""):
        if isinstance(n, dict):
            for k, v in n.items():
                if k in keys and not isinstance(v, (dict, list)):
                    out.append("%s.%s=%r" % (p, k, v))
                walk(v, p + "." + k)
        elif isinstance(n, list):
            for i, v in enumerate(n[:30]):
                walk(v, p + "[%d]" % i)
    walk(data)
    print("ZADETKOV:", len(out))
    for x in out[:120]:
        print(x)

main()
