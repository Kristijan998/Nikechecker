import os
from playwright.sync_api import sync_playwright

URL = os.environ.get("NIKE_URL", "https://www.nike.com/si/t/air-force-1-flyknit-2-shoes-7EHtWGRa/AV3042-100")

JS = r"""
() => {
  const res = [];
  const radios = document.querySelectorAll('input[type=radio]');
  radios.forEach(inp => {
    let labHtml = '';
    if (inp.id){ const l=document.querySelector('label[for="'+inp.id+'"]'); if(l) labHtml=l.outerHTML.slice(0,300); }
    res.push('RADIO: ' + inp.outerHTML.slice(0,200));
    if (labHtml) res.push('  LABEL: ' + labHtml);
  });
  return res;
}
"""

def main():
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
        rows = page.evaluate(JS)
        browser.close()
    print("Stevilo radio inputov:", len([r for r in rows if r.startswith('RADIO')]))
    for r in rows[:60]:
        print(r)

if __name__ == "__main__":
    main()
