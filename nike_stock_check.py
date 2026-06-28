import os, json, urllib.request, urllib.parse
from playwright.sync_api import sync_playwright

URL = os.environ.get("NIKE_URL", "https://www.nike.com/si/t/air-force-1-flyknit-2-shoes-7EHtWGRa/AV3042-100")
TARGET_LABEL = os.environ.get("TARGET_LABEL", "EU 45")
TARGET_VALUE = os.environ.get("TARGET_VALUE", "11")
TG_TOKEN = os.environ.get("TELEGRAM_TOKEN", "")
TG_CHAT = os.environ.get("TELEGRAM_CHAT_ID", "")
STATE_FILE = "state.json"

JS = r"""
() => {
  const out = [];
  document.querySelectorAll('input[type=radio][name="grid-selector-input"]').forEach(inp => {
    let label = '';
    if (inp.id){ const l=document.querySelector('label[for="'+inp.id+'"]'); if(l) label=(l.textContent||'').replace(/\s+/g,' ').trim(); }
    out.push({label: label, value: inp.value, disabled: inp.getAttribute('aria-disabled')==='true'});
  });
  return out;
}
"""

def telegram(msg):
    if not TG_TOKEN or not TG_CHAT:
        print("Ni TG nastavitev")
        return
    u = "https://api.telegram.org/bot%s/sendMessage" % TG_TOKEN
    d = urllib.parse.urlencode({"chat_id": TG_CHAT, "text": msg}).encode()
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

def main():
    state = load_state()
    sizes = []
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, args=["--no-sandbox"])
        ctx = browser.new_context(
            locale="sl-SI",
            user_agent=("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                        "(KHTML, like Gecko) Chrome/124.0 Safari/537.36"),
            viewport={"width": 1280, "height": 900},
        )
        page = ctx.new_page()
        page.goto(URL, wait_until="domcontentloaded", timeout=60000)
        for sel in ["#onetrust-reject-all-handler", "#onetrust-accept-btn-handler"]:
            try:
                b = page.query_selector(sel)
                if b:
                    b.click(timeout=3000)
                    break
            except Exception:
                pass
        page.wait_for_timeout(5000)
        try:
            sizes = page.evaluate(JS)
        except Exception as e:
            print("Evaluate napaka:", e)
        browser.close()

    if not sizes:
        print("Ni velikosti (stran se ni nalozila) - nic ne posljem.")
        return

    print("Velikosti:")
    for s in sizes:
        print("  %-10s (US %-4s) -> %s" % (s.get("label") or "?", s.get("value"),
              "NA ZALOGI" if not s.get("disabled") else "razprodano"))

    tnorm = TARGET_LABEL.upper().replace(" ", "")
    target = None
    for s in sizes:
        lab = (s.get("label") or "").upper().replace(" ", "")
        if lab == tnorm or s.get("value") == TARGET_VALUE:
            target = s
            break

    if target is None:
        print("Ciljne velikosti %s ni na seznamu - nic ne posljem." % TARGET_LABEL)
        return

    avail = not target.get("disabled")
    print("CILJ %s -> %s" % (TARGET_LABEL, "NA ZALOGI" if avail else "razprodano"))

    if avail and not state.get("available"):
        telegram("\u2705 Nike AF1 Flyknit 2.0 (bela) %s je NA ZALOGI!\n%s" % (TARGET_LABEL, URL))
        save_state({"available": True})
    elif not avail and state.get("available"):
        save_state({"available": False})

if __name__ == "__main__":
    main()
