"""One-off probe: log JSON response URLs from Mercado Libre Eightfold careers page."""
from playwright.sync_api import sync_playwright

URL = "https://mercadolibre.eightfold.ai/careers"


def main() -> None:
    seen: set[str] = set()
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        def on_response(response) -> None:
            ct = (response.headers.get("content-type") or "").lower()
            if "json" not in ct or response.status != 200:
                return
            u = response.url
            if u in seen:
                return
            seen.add(u)
            try:
                body = response.text()
            except Exception:
                return
            if len(body) < 50 or len(body) > 2_000_000:
                return
            print(f"{len(body):8d} {u[:120]}")

        page.on("response", on_response)
        page.goto(URL, wait_until="domcontentloaded", timeout=60000)
        page.wait_for_timeout(8000)
        browser.close()


if __name__ == "__main__":
    main()
