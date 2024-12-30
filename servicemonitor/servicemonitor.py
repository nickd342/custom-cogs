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
            
            # Update embed color based on overall status
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
                            # Message was deleted, send a new one
                            message = await channel.send(embed=embed)
                            await self.config.message_id.set(message.id)
                    else:
                        # First time sending status message
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
        """Configure service monitoring"""
        pass

    @monitor.command(name="add")
    async def add_service(self, ctx, name: str, url: str):
        """Add a service to monitor"""
        async with self.config.services() as services:
            services[name] = url
        await ctx.send(f"Added service: {name}", delete_after=10)
        await self.start_monitoring()

    @monitor.command(name="remove")
    async def remove_service(self, ctx, name: str):
        """Remove a service from monitoring"""
        async with self.config.services() as services:
            if name in services:
                del services[name]
                await ctx.send(f"Removed service: {name}", delete_after=10)
            else:
                await ctx.send("Service not found", delete_after=10)
        await self.start_monitoring()

    @monitor.command(name="list")
    async def list_services(self, ctx):
        """List monitored services"""
        services = await self.config.services()
        if not services:
            await ctx.send("No services configured")
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
        await self.config.message_id.set(None)  # Reset message ID for new channel
        await ctx.send(f"Status channel set to: {channel_id}", delete_after=10)
        await self.start_monitoring()

    @monitor.command()
    async def interval(self, ctx, seconds: int):
        """Set check interval in seconds (minimum 60)"""
        if seconds < 60:
            await ctx.send("Interval must be at least 60 seconds", delete_after=10)
            return
        await self.config.check_interval.set(seconds)
        await ctx.send(f"Check interval set to: {seconds} seconds", delete_after=10)
        await self.start_monitoring()