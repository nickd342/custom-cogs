from .servicemonitor import ServiceMonitor

async def setup(bot):
    await bot.add_cog(ServiceMonitor(bot))