"""Debug script to get full BrighterMonday job card HTML."""
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page(user_agent=(
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    ))

    page.goto("https://www.brightermonday.co.ke/jobs?q=developer&location=nairobi",
              wait_until="networkidle", timeout=60000)

    result = page.evaluate("""() => {
        const links = document.querySelectorAll('a[data-cy="listing-title-link"]');
        if (!links.length) return 'NO LINKS FOUND';

        const output = [];
        for (let i = 0; i < 3; i++) {
            // Go up exactly 2 levels: a -> div.flex -> div.w-full (the card)
            const card = links[i].parentElement?.parentElement;
            output.push('=== CARD ' + (i+1) + ' (tag: ' + card?.tagName + ' class: ' + card?.className + ') ===');
            output.push(card ? card.outerHTML.substring(0, 2000) : 'NOT FOUND');
        }
        return output.join('\\n');
    }""")
    print(result)

    browser.close()
