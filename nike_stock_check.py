import urllib.request, re

GTIN = "00192499276124"
URL = "https://www.nike.com/si/t/air-force-1-flyknit-2-shoes-7EHtWGRa/AV3042-100"

def main():
    req = urllib.request.Request(URL, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36", "Accept-Language": "sl-SI,sl;q=0.9,en;q=0.8"})
    html = urllib.request.urlopen(req, timeout=30).read().decode("utf-8", "replace")
    print("Dolzina:", len(html))
    print("Stevilo 'available':", html.count("available"))
    print("Stevilo 'AVAILABLE':", html.count("AVAILABLE"))
    print("Stevilo 'IN_STOCK':", html.count("IN_STOCK"))
    print("Stevilo 'OUT_OF_STOCK':", html.count("OUT_OF_STOCK"))
    print("GTIN najden:", GTIN in html)
    i = html.find(GTIN)
    if i != -1:
        print("Okolica GTIN-a:")
        print(html[i-300:i+300])

main()
