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
                "--enable-webgl",
                "--use-gl=swiftshader",
                "--enable-unsafe-swiftshader",
                "--ignore-gpu-blocklist",
                "--disable-blink-features=AutomationControlled"
            ]
        )
        context = await browser.new_context(
            viewport={"width": 1280, "height": 720},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36"
        )
        page = await context.new_page()
        
        await page.route(
            "**/*", 
            lambda route: route.abort() if any(ad in route.request.url for ad in [
                "googlesyndication.com", "adservice.google.com", "doubleclick.net", 
                "googletagmanager.com", "pagead", "adsbygoogle"
            ]) else route.continue_()
        )

        await page.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
            Object.defineProperty(navigator, 'languages', { get: () => ['en-US', 'en'] });
            window.chrome = { runtime: {} };
        """)

        await page.goto("https://taming.io/", wait_until="domcontentloaded")
        await page.wait_for_timeout(6000)

        # 1. Click center to focus canvas
        await page.mouse.click(640, 360)
        await page.wait_for_timeout(1000)

        # 2. Click CONTINUE to dismiss update popup
        await page.mouse.click(415, 575)
        await page.wait_for_timeout(2000)

        # 3. Press Enter to hit PLAY
        await page.keyboard.press("Enter")
        
        # Take snapshot immediately without waiting 8 seconds to avoid memory exhaustion
        await page.wait_for_timeout(2000)

        screenshot_path = "leaderboard.png"
        await page.screenshot(
            path=screenshot_path,
            type="jpeg",
            quality=80,
            clip={"x": 980, "y": 20, "width": 280, "height": 320}
        )
        
        await browser.close()
        
    await ctx.send(file=discord.File(screenshot_path))

TOKEN = os.getenv("DISCORD_TOKEN")
if not TOKEN:
    raise ValueError("No DISCORD_TOKEN found in environment variables!")

bot.run(TOKEN)
