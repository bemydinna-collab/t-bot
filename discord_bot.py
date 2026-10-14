import os
import discord
from discord.ext import commands
from playwright.async_api import async_playwright

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}!")

@bot.command(name="leaderboard")
async def leaderboard(ctx, *, server_name: str = None):
    await ctx.send("Fetching leaderboard, please wait...")
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=[
                "--no-sandbox",
                "--disable-setuid-sandbox",
                "--disable-dev-shm-usage",
                "--disable-gpu",
                "--disable-software-rasterizer",
                "--disable-dev-shm-usage",
                "--disable-blink-features=AutomationControlled",
                "--js-flags=--max-old-space-size=256"
            ]
        )
        context = await browser.new_context(
            viewport={"width": 960, "height": 540},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36"
        )
        page = await context.new_page()
        
        await page.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
            Object.defineProperty(navigator, 'languages', { get: () => ['en-US', 'en'] });
            window.chrome = { runtime: {} };
        """)

        await page.goto("https://taming.io/", wait_until="domcontentloaded")
        await page.wait_for_timeout(6000)

        # 1. Click center to focus canvas
        await page.mouse.click(480, 270)
        await page.wait_for_timeout(1000)

        # 2. Click CONTINUE to dismiss update popup
        await page.mouse.click(310, 430)
        await page.wait_for_timeout(3000)

        screenshot_path = "leaderboard.png"
        
        # Extract canvas frame data directly via JavaScript to bypass font-rasterization crash
        screenshot_bytes = await page.evaluate("""
            async () => {
                const canvas = document.querySelector('canvas');
                if (!canvas) return null;
                return canvas.toDataURL('image/jpeg', 0.7);
            }
        """)

        if screenshot_bytes:
            import base64
            header, encoded = screenshot_bytes.split(",", 1)
            with open(screenshot_path, "wb") as fh:
                fh.write(base64.b64decode(encoded))
        else:
            # Fallback to clip screenshot if canvas grab is empty
            await page.screenshot(path=screenshot_path, type="jpeg", quality=70, clip={"x": 0, "y": 0, "width": 960, "height": 540})

        await browser.close()
        
    await ctx.send(file=discord.File(screenshot_path))

TOKEN = os.getenv("DISCORD_TOKEN")
if not TOKEN:
    raise ValueError("No DISCORD_TOKEN found in environment variables!")

bot.run(TOKEN)
