import os, json, urllib.request, urllib.parse
from playwright.sync_api import sync_playwright

URL = os.environ.get("NIKE_URL", "https://www.nike.com/si/t/air-force-1-flyknit-2-shoes-7EHtWGRa/AV3042-100")
TARGET = os.environ.get("TARGET_SIZE", "45")
TG_TOKEN = os.environ.get("TELEGRAM_TOKEN", "")
TG_CHAT = os.environ.get("TELEGRAM_CHAT_ID", "")
STATE_FILE = "state.json"

ALT = {"45": {"45", "11"}, "44": {"44", "10"}, "46": {"46", "12"}}
ACCEPT = ALT.get(TARGET, {TARGET})

JS = r"""
() => {
  const out = [];
  const norm = t => (t||'').replace(/\s+/g,' ').trim();
  document.querySelectorAll('input[type=radio]').forEach(inp => {
    let label='';
    if (inp.id){ const l=document.querySelector('label[for="'+inp.id+'"]'); if(l) label=l.textContent; }
    if(!label) label=inp.getAttribute('aria-label')||inp.value||'';
    out.push({label:norm(label), disabled: inp.disabled || inp.getAttribute('aria-disabled')==='true'});
  });
  document.querySelectorAll('button, [role=radio], li, label').forEach(b => {
    const t = norm(b.textContent);
    if(/^(EU\s*)?\d{1,2}(\.5)?$/.test(t)){
      const dis = b.disabled || b.getAttribute('aria-disabled')==='true' || /disabled|soldout|sold-out|unavailable/i.test(b.className||'');
      out.push({label:t, disabled: dis});
    }
  });
  document.querySelectorAll('option').forEach(o => {
    out.push({label:norm(o.textContent), disabled:o.disabled});
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

def norm_label(label):
    return label.upper().replace("EU", "").replace("M", "").strip()

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
                btn = page.query_selector(sel)
                if btn:
                    btn.click(timeout=3000)
                    break
            except Exception:
                pass
        page.wait_for_timeout(5000)
        try:
            sizes = page.evaluate(JS)
        except Exception as e:
            print("Evaluate napaka:", e)
        browser.close()

    seen = {}
    for s in sizes:
        lab = s.get("label", "")
        if not lab:
            continue
        ok = not s.get("disabled")
        seen[lab] = seen.get(lab, False) or ok

    print("Najdene velikosti (label -> na zalogi):")
    for lab in sorted(seen):
        print("  %r -> %s" % (lab, seen[lab]))

    avail = None
    for lab, ok in seen.items():
        if norm_label(lab) in ACCEPT:
            avail = ok if avail is None else (avail or ok)
    print("CILJ EU %s -> %s" % (TARGET, avail))

    if avail is True and not state.get("available"):
        telegram("\u2705 Nike AF1 Flyknit 2.0 (bela) EU %s je NA ZALOGI!\n%s" % (TARGET, URL))
        save_state({"available": True})
    elif avail is False and state.get("available"):
        save_state({"available": False})

if __name__ == "__main__":
    main()
