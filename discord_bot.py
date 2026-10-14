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
async def leaderboard(ctx):
    await ctx.send("Capturing leaderboard, please wait...")
    
    async with async_playwright() as p:
        # Launch browser in headless mode optimized for containers
        browser = await p.chromium.launch(
            headless=True,
            args=["--no-sandbox", "--disable-setuid-sandbox"]
        )
        page = await browser.new_page()
        
        # Go to Taming.io (adjust URL/query parameters as needed)
        await page.goto("https://taming.io/")
        
        # Wait for the game/leaderboard elements to load
        await page.wait_for_timeout(5000)
        
        # Take a screenshot of the page or specific element
        screenshot_path = "leaderboard.png"
        await page.screenshot(path=screenshot_path, full_page=False)
        
        await browser.close()
        
    # Send the screenshot back to Discord
    await ctx.send(file=discord.File(screenshot_path))

# Run the bot using the environment variable
TOKEN = os.getenv("DISCORD_TOKEN")
if not TOKEN:
    raise ValueError("No DISCORD_TOKEN found in environment variables!")

bot.run(TOKEN)
