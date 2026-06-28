import urllib.request

GTIN = "00192499276124"
URL = "https://www.nike.com/si/t/air-force-1-flyknit-2-shoes-7EHtWGRa/AV3042-100"

def main():
    req = urllib.request.Request(URL, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36", "Accept-Language": "sl-SI,sl;q=0.9,en;q=0.8"})
    html = urllib.request.urlopen(req, timeout=30).read().decode("utf-8", "replace")
    i = html.find(GTIN)
    print("Okolica GTIN-a (700 znakov):")
    print(html[i-50:i+700])

main()
