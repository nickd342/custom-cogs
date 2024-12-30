from redbot.core import commands, Config
import discord
import aiohttp
import asyncio
from datetime import datetime

class ServiceMonitor(commands.Cog):
    
    def __init__(self, bot):
        self.bot = bot
        self.config = Config.get_conf(self, identifier=852871979)
        self.check_task = None
        
        default_global = {
            "channel_id": None,
            "message_id": None,
            "check_interval": 300,
            "services": {}
        }
        self.config.register_global(**default_global)
        self.bot.loop.create_task(self.initialize())

    async def initialize(self):
        await self.bot.wait_until_ready()
        await self.start_monitoring()

    def create_status_embed(self, services_status, timestamp):
        embed = discord.Embed(
            title="Service Status Monitor",
            description=f"Last Updated: {timestamp}",
            color=discord.Color.blue()
        )
        
        for name, status in services_status.items():
            is_online = status == "🟢 Online"
            embed.add_field(
                name=name,
                value=status,
                inline=True
            )
            
            if not is_online and embed.color == discord.Color.blue():
                embed.color = discord.Color.red()

        return embed

    async def check_services(self):
        while True:
            channel_id = await self.config.channel_id()
            message_id = await self.config.message_id()
            interval = await self.config.check_interval()
            services = await self.config.services()
            
            if not channel_id or not services:
                await asyncio.sleep(60)
                continue
            
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            services_status = {}
            
            async with aiohttp.ClientSession() as session:
                for name, url in services.items():
                    try:
                        async with session.get(url) as response:
                            services_status[name] = "🟢 Online" if response.status == 200 else "🔴 Offline"
                    except:
                        services_status[name] = "🔴 Offline"
            
            embed = self.create_status_embed(services_status, timestamp)
            channel = self.bot.get_channel(channel_id)
            
            if channel:
                try:
                    if message_id:
                        try:
                            message = await channel.fetch_message(message_id)
                            await message.edit(embed=embed)
                        except discord.NotFound:
                            message = await channel.send(embed=embed)
                            await self.config.message_id.set(message.id)
                    else:
                        message = await channel.send(embed=embed)
                        await self.config.message_id.set(message.id)
                except discord.Forbidden:
                    await channel.send("Error: Bot lacks permissions to manage messages")
            
            await asyncio.sleep(interval)

    async def start_monitoring(self):
        if self.check_task:
            self.check_task.cancel()
        self.check_task = self.bot.loop.create_task(self.check_services())

    def cog_unload(self):
        if self.check_task:
            self.check_task.cancel()

    @commands.group()
    @commands.admin_or_permissions(administrator=True)
    async def monitor(self, ctx):
        pass

    @monitor.command(name="add")
    async def add_service(self, ctx, name: str, url: str):
        async with self.config.services() as services:
            services[name] = url
        embed = discord.Embed(description=f"Added service: {name}", color=discord.Color.green())
        await ctx.send(embed=embed, delete_after=10)
        await self.start_monitoring()

    @monitor.command(name="remove")
    async def remove_service(self, ctx, name: str):
        async with self.config.services() as services:
            if name in services:
                del services[name]
                embed = discord.Embed(description=f"Removed service: {name}", color=discord.Color.green())
                await ctx.send(embed=embed, delete_after=10)
            else:
                embed = discord.Embed(description="Service not found", color=discord.Color.red())
                await ctx.send(embed=embed, delete_after=10)
        await self.start_monitoring()

    @monitor.command(name="list")
    async def list_services(self, ctx):
        services = await self.config.services()
        if not services:
            embed = discord.Embed(
                title="Monitored Services",
                description="No services configured",
                color=discord.Color.blue()
            )
            await ctx.send(embed=embed)
            return
        
        embed = discord.Embed(
            title="Monitored Services",
            color=discord.Color.blue()
        )
        for name, url in services.items():
            embed.add_field(name=name, value=url, inline=False)
        await ctx.send(embed=embed)

    @monitor.command()
    async def channel(self, ctx, channel_id: int):
        """Set status update channel"""
        await self.config.channel_id.set(channel_id)
        await self.config.message_id.set(None)
        embed = discord.Embed(description=f"Status channel set to: {channel_id}", color=discord.Color.green())
        await ctx.send(embed=embed, delete_after=10)
        await self.start_monitoring()

    @monitor.command()
    async def interval(self, ctx, seconds: int):
        if seconds < 60:
            embed = discord.Embed(description="Interval must be at least 60 seconds", color=discord.Color.red())
            await ctx.send(embed=embed, delete_after=10)
            return
        await self.config.check_interval.set(seconds)
        embed = discord.Embed(description=f"Check interval set to: {seconds} seconds", color=discord.Color.green())
        await ctx.send(embed=embed, delete_after=10)
        await self.start_monitoring()
