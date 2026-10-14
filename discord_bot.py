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
                "--disable-blink-features=AutomationControlled",
                "--js-flags=--max-old-space-size=256"
            ]
        )
        # Use a smaller resolution to minimize WebGL canvas memory usage
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

        # 2. Click CONTINUE button (adjusted for 960x540 viewport)
        await page.mouse.click(310, 430)
        await page.wait_for_timeout(2000)

        # 3. Press Enter to trigger Play safely
        await page.keyboard.press("Enter")
        await page.wait_for_timeout(4000)

        screenshot_path = "leaderboard.png"
        await page.screenshot(
            path=screenshot_path, 
            type="jpeg", 
            quality=75, 
            animations="disabled"
        )
        await browser.close()
        
    await ctx.send(file=discord.File(screenshot_path))

TOKEN = os.getenv("DISCORD_TOKEN")
if not TOKEN:
    raise ValueError("No DISCORD_TOKEN found in environment variables!")

bot.run(TOKEN)
