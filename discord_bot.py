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
                "--disable-dev-shm-usage",
                "--disable-gpu"
            ]
        )
        page = await browser.new_page()
        await page.set_viewport_size({"width": 1280, "height": 720})
        
        await page.goto("https://taming.io/", wait_until="networkidle")
        await page.wait_for_timeout(4000)

        # 1. Click exact physical coordinates of "CONTINUE" button on 1280x720 canvas
        await page.mouse.click(415, 560)
        await page.wait_for_timeout(1000)

        # 2. Click top-right 'X' close button of the update modal
        await page.mouse.click(720, 275)
        await page.wait_for_timeout(1000)

        # 3. Click "NO" on the Subscribe prompt (bottom right)
        await page.mouse.click(830, 775)
        await page.wait_for_timeout(1000)

        # 4. Fallback key press
        await page.keyboard.press("Escape")
        await page.wait_for_timeout(1000)

        screenshot_path = "leaderboard.png"
        await page.screenshot(path=screenshot_path, full_page=False)
        await browser.close()
        
    await ctx.send(file=discord.File(screenshot_path))

TOKEN = os.getenv("DISCORD_TOKEN")
if not TOKEN:
    raise ValueError("No DISCORD_TOKEN found in environment variables!")

bot.run(TOKEN)
