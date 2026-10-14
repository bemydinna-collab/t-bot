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
    await ctx.send("Capturing leaderboard, please wait...")
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=[
                "--no-sandbox",
                "--disable-setuid-sandbox",
                "--disable-dev-shm-usage", # Fixes the Docker crash!
                "--disable-gpu"
            ]
        )
        page = await browser.new_page()
        await page.set_viewport_size({"width": 1280, "height": 720})
        
        await page.goto("https://taming.io/", wait_until="domcontentloaded")
        await page.wait_for_timeout(5000)
        
        # Try to safely click the CONTINUE button on the update popup
        try:
            continue_btn = page.locator("text=CONTINUE")
            if await continue_btn.is_visible(timeout=3000):
                await continue_btn.click()
                await page.wait_for_timeout(2000)
        except Exception as e:
            print(f"Popup handling note: {e}")

        screenshot_path = "leaderboard.png"
        await page.screenshot(path=screenshot_path, full_page=False)
        await browser.close()
        
    await ctx.send(file=discord.File(screenshot_path))

TOKEN = os.getenv("DISCORD_TOKEN")
if not TOKEN:
    raise ValueError("No DISCORD_TOKEN found in environment variables!")

bot.run(TOKEN)
