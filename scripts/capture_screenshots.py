"""One-off helper to capture demo screenshots for the manuscript. Not part of the app."""
import asyncio
from pathlib import Path

from playwright.async_api import async_playwright

SCREENSHOTS_DIR = Path(__file__).resolve().parent.parent / "screenshots"


async def main():
    SCREENSHOTS_DIR.mkdir(exist_ok=True)
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page(viewport={"width": 1400, "height": 1000})

        await page.goto("http://localhost:8501", wait_until="networkidle")
        await page.wait_for_timeout(2000)
        await page.screenshot(path=str(SCREENSHOTS_DIR / "01_initial_state.png"))
        print("Saved 01_initial_state.png")

        button = page.get_by_role("button", name="Simulate Data")
        await button.click()
        await page.wait_for_timeout(1500)

        async def resize_to_content():
            await page.set_viewport_size({"width": 1400, "height": 3200})
            await page.wait_for_timeout(600)
            height = await page.evaluate("document.documentElement.scrollHeight")
            await page.set_viewport_size({"width": 1400, "height": min(int(height) + 60, 6000)})
            await page.wait_for_timeout(400)

        await resize_to_content()
        await page.screenshot(path=str(SCREENSHOTS_DIR / "02_simulated_results.png"))
        print("Saved 02_simulated_results.png")

        for _ in range(2):
            await button.click()
            await page.wait_for_timeout(1200)
        await page.wait_for_timeout(500)
        await resize_to_content()
        await page.screenshot(path=str(SCREENSHOTS_DIR / "03_session_history.png"))
        print("Saved 03_session_history.png")

        await browser.close()


if __name__ == "__main__":
    asyncio.run(main())
