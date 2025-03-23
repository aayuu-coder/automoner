import discord
from discord.ext import commands, tasks
from collections import defaultdict
import asyncio
from textblob import TextBlob

# Set up bot with prefix '.'
intents = discord.Intents.all()
bot = commands.Bot(command_prefix=".", intents=intents)

# User data storage
user_data = defaultdict(lambda: {"messages": 0, "words": 0, "reputation": 0, "activity_score": 0, "sentiment": 0})

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user} FROM NOW I WILL HANDLE THE WHOLE PROMOTION AND THE DEMOTION KF THE STAFF')
    calculate_activity_scores.start()

@bot.event
async def on_message(message):
    if message.author.bot:
        return

    user = message.author.id
    user_data[user]["messages"] += 1
    user_data[user]["words"] += len(message.content.split())
    sentiment_score = TextBlob(message.content).sentiment.polarity
    user_data[user]["sentiment"] += sentiment_score

    # Process commands
    await bot.process_commands(message)

@tasks.loop(hours=24)
async def calculate_activity_scores():
    for user, data in user_data.items():
        data["activity_score"] = (data["messages"] * 2) + (data["words"] // 10) + (data["reputation"] * 5) + (data["sentiment"] * 10)

# .report command to generate a report for a user
@bot.command(name="report", help="Generate a report on a user's activity.")
async def report(ctx, member: discord.Member):
    user = member.id
    data = user_data[user]
    messages = data["messages"]
    words = data["words"]
    reputation = data["reputation"]
    activity_score = data["activity_score"]
    sentiment = data["sentiment"] / messages if messages else 0
    avg_words = words / messages if messages else 0

    # Engagement & Behavior Analysis
    engagement = "High" if messages > 500 else "Medium" if messages > 200 else "Low"
    tone = "Positive" if sentiment > 0.3 else "Neutral" if sentiment > -0.3 else "Negative"
    rating = min(10, (messages // 50) + (reputation // 3) + (activity_score // 100))  # Rating out of 10
    decision = "Deserves Promotion" if rating >= 5 else "Needs Improvement / Demotion"

    embed = discord.Embed(title=f'User Report: {member.name}', color=discord.Color.blue())
    embed.add_field(name='Total Messages', value=str(messages), inline=True)
    embed.add_field(name='Average Words per Message', value=f'{avg_words:.2f}', inline=True)
    embed.add_field(name='Engagement Level', value=engagement, inline=True)
    embed.add_field(name='Message Tone', value=tone, inline=True)
    embed.add_field(name='Reputation Points', value=str(reputation), inline=True)
    embed.add_field(name='Activity Score', value=str(activity_score), inline=True)
    embed.add_field(name='Overall Rating', value=f'{rating}/10', inline=True)
    embed.add_field(name='Decision', value=decision, inline=False)

    await ctx.send(embed=embed)

# .addrep command to add reputation points to a user (admin only)
@bot.command(name="addrep", help="Add reputation points to a user.")
async def addrep(ctx, member: discord.Member, points: int):
    if ctx.author.guild_permissions.administrator:
        user_data[member.id]["reputation"] += points
        await ctx.send(f'Added {points} reputation points to {member.mention}!')
    else:
        await ctx.send("You don't have permission to add reputation points!")

# .topactive command to show the top 10 most active users
@bot.command(name="topactive", help="Show the top 10 most active users.")
async def topactive(ctx):
    sorted_users = sorted(user_data.items(), key=lambda x: x[1]["activity_score"], reverse=True)[:10]
    leaderboard = '\n'.join([f'<@{user}> - {data["activity_score"]} activity score' for user, data in sorted_users])
    embed = discord.Embed(title='Top Active Users', description=leaderboard, color=discord.Color.gold())
    await ctx.send(embed=embed)

# .toppositive command to show the top 10 users with the highest reputation
@bot.command(name="toppositive", help="Show the top 10 users with the highest reputation.")
async def toppositive(ctx):
    sorted_users = sorted(user_data.items(), key=lambda x: x[1]["reputation"], reverse=True)[:10]
    leaderboard = '\n'.join([f'<@{user}> - {data["reputation"]} reputation points' for user, data in sorted_users])
    embed = discord.Embed(title='Top Positive Users', description=leaderboard, color=discord.Color.green())
    await ctx.send(embed=embed)

# Run the bot with the token
bot.run("MTM1MzA0MjQ0MTM0Njg3NTYyMw.G8f9aU.XntXkKf8Nk1qhxvHBV_G-niIiz19tUlC9f-A2s")  # Replace with your actual bot token
