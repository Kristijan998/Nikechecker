import urllib.request, json

GTIN = "00192499276124"
URL = "https://api.nike.com/deliver/available_gtins/v3/?filter=gtins(%s)" % GTIN

def main():
    req = urllib.request.Request(URL, headers={"User-Agent": "Mozilla/5.0", "Accept": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            print("STATUS:", r.status)
            print(r.read().decode("utf-8", "replace")[:2000])
    except Exception as e:
        print("NAPAKA:", e)

main()
