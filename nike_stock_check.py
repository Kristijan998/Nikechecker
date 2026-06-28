import urllib.request

GTIN = "00192499276124"
URLS = [
    "https://api.nike.com/deliver/available_gtins/v3/?filter=gtins(%s)&filter=country(SI)" % GTIN,
    "https://api.nike.com/merch/availability/v1/?filter=productIds(AV3042-100)",
    "https://api.nike.com/deliver/available_skus/v3/?filter=gtins(%s)" % GTIN,
]

def get(url):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0", "Accept": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return "OK %s: %s" % (r.status, r.read().decode("utf-8", "replace")[:800])
    except Exception as e:
        return "ERR: %s" % e

def main():
    for u in URLS:
        print("URL:", u)
        print(get(u))
        print("-----")

main()
