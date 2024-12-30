from redbot.core import commands, Config
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
            "check_interval": 300,
            "services": {}
        }
        self.config.register_global(**default_global)
        self.bot.loop.create_task(self.initialize())
    
    async def initialize(self):
        await self.bot.wait_until_ready()
        await self.start_monitoring()
    
    async def check_services(self):
        while True:
            channel_id = await self.config.channel_id()
            interval = await self.config.check_interval()
            services = await self.config.services()
            
            if not channel_id or not services:
                await asyncio.sleep(60)
                continue
            
            status_message = []
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            status_message.append(f"Service Status Update ({timestamp})")
            
            async with aiohttp.ClientSession() as session:
                for name, url in services.items():
                    try:
                        async with session.get(url) as response:
                            status = "🟢 Online" if response.status == 200 else "🔴 Offline"
                    except:
                        status = "🔴 Offline"
                    status_message.append(f"{name}: {status}")
            
            channel = self.bot.get_channel(channel_id)
            if channel:
                await channel.send("\n".join(status_message))
            
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
        await ctx.send(f"Added service: {name}")
        await self.start_monitoring()

    @monitor.command(name="remove")
    async def remove_service(self, ctx, name: str):
        """Remove a service from monitoring"""
        async with self.config.services() as services:
            if name in services:
                del services[name]
                await ctx.send(f"Removed service: {name}")
            else:
                await ctx.send("Service not found")
        await self.start_monitoring()

    @monitor.command(name="list")
    async def list_services(self, ctx):
        """List monitored services"""
        services = await self.config.services()
        if not services:
            await ctx.send("No services configured")
            return
        
        message = ["Monitored Services:"]
        for name, url in services.items():
            message.append(f"{name}: {url}")
        await ctx.send("\n".join(message))

    @monitor.command()
    async def channel(self, ctx, channel_id: int):
        """Set status update channel"""
        await self.config.channel_id.set(channel_id)
        await ctx.send(f"Status channel set to: {channel_id}")
        await self.start_monitoring()

    @monitor.command()
    async def interval(self, ctx, seconds: int):
        """Set check interval in seconds (minimum 60)"""
        if seconds < 60:
            await ctx.send("Interval must be at least 60 seconds")
            return
        await self.config.check_interval.set(seconds)
        await ctx.send(f"Check interval set to: {seconds} seconds")
        await self.start_monitoring()