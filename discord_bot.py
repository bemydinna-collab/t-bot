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
    await ctx.send("Fetching live in-game leaderboard data, please wait...")
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=[
                "--no-sandbox",
                "--disable-setuid-sandbox",
                "--disable-dev-shm-usage",
                "--enable-webgl",
                "--use-gl=swiftshader",
                "--disable-blink-features=AutomationControlled"
            ]
        )
        context = await browser.new_context(
            viewport={"width": 1280, "height": 720},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36"
        )
        page = await context.new_page()
        
        # Block heavy ad networks
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

        # 3. Press Enter to enter the live match
        await page.keyboard.press("Enter")
        await page.wait_for_timeout(6000)

        # 4. Extract leaderboard HTML elements or DOM text overlays directly from the active game page
        leaderboard_data = await page.evaluate("""
            () => {
                // Look for leaderboard DOM elements or overlay text boxes in the game UI
                const elements = document.querySelectorAll('.leaderboard-element, [class*="leaderboard"], [id*="leaderboard"]');
                if (elements.length > 0) {
                    return Array.from(elements).map(el => el.innerText).join('\\n');
                }
                // Fallback: grab all text within potential score overlay containers
                const hud = document.querySelectorAll('div');
                let results = [];
                for (let div of hud) {
                    if (div.innerText && div.innerText.includes('pts') || div.innerText.includes('score')) {
                        results.push(div.innerText);
                    }
                }
                return results.slice(0, 5).join('\\n---\\n') || "Could not parse live DOM leaderboard text.";
            }
        """)

        await browser.close()
        
    if leaderboard_data and len(leaderboard_data.strip()) > 0:
        await ctx.send(f"**Live In-Game Leaderboard:**\n```\n{leaderboard_data}\n```")
    else:
        await ctx.send("Joined match, but couldn't grab the DOM text elements cleanly.")

TOKEN = os.getenv("DISCORD_TOKEN")
if not TOKEN:
    raise ValueError("No DISCORD_TOKEN found in environment variables!")

bot.run(TOKEN)
