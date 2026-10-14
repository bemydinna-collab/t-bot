import os
import discord
from discord.ext import commands
from playwright.async_api import async_playwright
from playwright_stealth import stealth_async

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
        context = await browser.new_context(
            viewport={"width": 1280, "height": 720},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36"
        )
        page = await context.new_page()
        
        # Apply full stealth overrides
        await stealth_async(page)

        await page.goto("https://taming.io/", wait_until="domcontentloaded")
        
        # Wait up to 15s for Cloudflare Turnstile verification box to clear
        try:
            # If Cloudflare iframe exists, wait for it to detach/disappear
            await page.wait_for_selector("iframe[src*='cloudflare']", state="detached", timeout=15000)
        except Exception:
            print("Cloudflare check passed or timed out, continuing...")

        await page.wait_for_timeout(5000)

        # 1. Focus canvas
        await page.mouse.click(640, 360)
        await page.wait_for_timeout(1000)

        # 2. Click CONTINUE button
        await page.mouse.click(415, 575)
        await page.wait_for_timeout(3000)

        screenshot_path = "leaderboard.png"
        await page.screenshot(path=screenshot_path, full_page=False)
        await browser.close()
        
    await ctx.send(file=discord.File(screenshot_path))

TOKEN = os.getenv("DISCORD_TOKEN")
if not TOKEN:
    raise ValueError("No DISCORD_TOKEN found in environment variables!")

bot.run(TOKEN)
