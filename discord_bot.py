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
                "--disable-blink-features=AutomationControlled"
            ]
        )
        page = await browser.new_page()
        await page.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        await page.set_viewport_size({"width": 1280, "height": 720})
        await page.goto("https://taming.io/", wait_until="domcontentloaded")
        await page.wait_for_timeout(8000)

        # 1. Click center to focus canvas
        await page.mouse.click(640, 360)
        await page.wait_for_timeout(1000)

        # 2. Click CONTINUE to dismiss update popup
        await page.mouse.click(415, 575)
        await page.wait_for_timeout(2000)

        # 3. Click the leaderboard/clipboard icon on the right side menu
        await page.mouse.click(868, 395)
        await page.wait_for_timeout(2000)

        screenshot_path = "leaderboard.png"
        await page.screenshot(path=screenshot_path, full_page=False)
        await browser.close()
        
    await ctx.send(file=discord.File(screenshot_path))

TOKEN = os.getenv("DISCORD_TOKEN")
if not TOKEN:
    raise ValueError("No DISCORD_TOKEN found in environment variables!")

bot.run(TOKEN)
