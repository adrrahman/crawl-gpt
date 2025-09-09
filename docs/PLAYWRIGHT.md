# Playwright playground

## Link
https://try.playwright.tech/

## AMGR
```
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page()
    page.goto("https://www.amgr.org/frm_directorySearch.cfm")
    page.get_by_role("combobox").filter(has_text="Select State").select_option("Kansas")
    page.get_by_role("combobox").filter(has_text="Select Member").select_option("Dwight Elmore")
    page.get_by_role("combobox").filter(has_text="Select Breed").select_option("(AR) - American Red")
    page.get_by_role("button", name="Submit").click()
    page.screenshot(path="example.png")
    browser.close()
```

## Shorthorn
```python
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page()
    page.goto("https://shorthorn.digitalbeef.com/")
    page.locator("#ranch_search_prefix").fill("Prefix")
    page.locator("#ranch_search_id").fill("ID")
    page.locator("#ranch_search_val").fill("Name")
    page.locator("#ranch_search_city").fill("City")
    page.get_by_role("combobox").select_option("United States - Alabama")
    page.get_by_role("listitem").filter(has_text="Ranch Search Herd Prefix").get_by_role("button").click()
    page.screenshot(path="example.png")
    browser.close()
```