import os, urllib.request, urllib.parse, json

GTIN = "00192499276124"  # EU 45
URL = "https://www.nike.com/si/t/air-force-1-flyknit-2-shoes-7EHtWGRa/AV3042-100"
TG_TOKEN = os.environ.get("TELEGRAM_TOKEN", "")
TG_CHAT = os.environ.get("TELEGRAM_CHAT_ID", "")

def fetch():
    req = urllib.request.Request(URL, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36", "Accept-Language": "sl-SI,sl;q=0.9,en;q=0.8"})
    return urllib.request.urlopen(req, timeout=30).read().decode("utf-8", "replace")

def telegram(msg):
    if not TG_TOKEN or not TG_CHAT:
        print("Ni TG nastavitev"); return
    u = "https://api.telegram.org/bot%s/sendMessage" % TG_TOKEN
    d = urllib.parse.urlencode({"chat_id": TG_CHAT, "text": msg}).encode()
    urllib.request.urlopen(urllib.request.Request(u, data=d), timeout=20).read()
    print("Telegram poslan")

def main():
    html = fetch()
    # Izpisi vseh 13 pojavitev "available" z okolico
    start = 0
    n = 0
    while True:
        i = html.find("available", start)
        if i == -1:
            break
        n += 1
        print("--- pojavitev %d ---" % n)
        print(html
