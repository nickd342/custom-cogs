import json
from pathlib import Path
from redbot.core.bot import Red
from .servicemonitor import ServiceMonitor
from .utils import out_of_date_check

with open(Path(__file__).parent / "info.json") as fp:
    __red_end_user_data_statement__ = json.load(fp)["end_user_data_statement"]

async def setup(bot: Red) -> None:
    cog = ServiceMonitor(bot)
    await out_of_date_check("servicemonitor", cog.__version__)
    await bot.add_cog(cog)
