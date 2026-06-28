import urllib.request

URL = "https://www.nike.com/si/t/air-force-1-flyknit-2-shoes-7EHtWGRa/AV3042-100"
HEADERS = {
    "User-Agent": ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                   "(KHTML, like Gecko) Chrome/124.0 Safari/537.36"),
    "Accept-Language": "sl-SI,sl;q=0.9,en;q=0.8",
}


def main():
    req = urllib.request.Request(URL, headers=HEADERS)
    html = urllib.request.urlopen(req, timeout=30).read().decode("utf-8", "replace")
    start = 0
    n = 0
    while True:
        i = html.find("available", start)
        if i == -1:
            break
        n += 1
        print("=== %d ===" % n)
        print(html[i - 100:i + 150])
        start = i + 1
    print("SKUPAJ:", n)


if __name__ == "__main__":
    main()
