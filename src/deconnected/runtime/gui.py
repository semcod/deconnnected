from __future__ import annotations
from dataclasses import dataclass

@dataclass
class GuiResult:
    api_urls: list[str]
    pages: list[str]

def run_gui_journey(base_url: str, actions: list[dict], headless: bool = True) -> GuiResult:
    try:
        from playwright.sync_api import sync_playwright
    except ImportError as exc:
        raise RuntimeError("Install GUI support: pip install deconnected[gui]") from exc
    api_urls: list[str] = []
    pages: list[str] = []
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=headless)
        page = browser.new_page()
        page.on("request", lambda request: api_urls.append(request.url) if request.resource_type in {"xhr", "fetch"} else None)
        for action in actions:
            if "goto" in action:
                page.goto(base_url.rstrip("/") + action["goto"])
                pages.append(page.url)
            elif "click" in action:
                page.locator(action["click"]).click()
            elif "fill" in action:
                page.locator(action["fill"]["selector"]).fill(action["fill"]["value"])
            elif "wait_for" in action:
                page.wait_for_selector(action["wait_for"])
        browser.close()
    return GuiResult(api_urls=api_urls, pages=pages)
