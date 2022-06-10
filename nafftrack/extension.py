import asyncio
import logging

import prometheus_client
import uvicorn
import naff
from nafftrack.stats import (
    bot_info,
    guilds_gauge,
    latency_gauge,
    messages_counter,
    snek_info,
)


class Stats(naff.Extension):
    host = "0.0.0.0"
    port = 8877
    interval = 5

    @naff.listen()
    async def on_startup(self) -> None:
        logging.info("Starting metrics endpoint!")
        app = prometheus_client.make_asgi_app()
        config = uvicorn.Config(app=app, host=self.host, port=self.port, access_log=False)
        server = uvicorn.Server(config)
        loop = asyncio.get_running_loop()
        loop.create_task(server.serve())

        snek_info.info(
            {
                "version": naff.const.__version__,
            }
        )

        guilds_gauge.set(len(self.bot.user._guild_ids))

        stats_task = naff.Task(
            self.collect_stats, naff.triggers.IntervalTrigger(seconds=self.interval)
        )
        stats_task.start()

    @naff.listen()
    async def on_ready(self) -> None:
        bot_info.info(
            {
                "username": self.bot.user.username,
                "discriminator": self.bot.user.discriminator,
                "tag": str(self.bot.user.tag),
            }
        )

    @naff.listen()
    async def on_message_create(self, event: naff.events.MessageCreate):
        if guild := event.message.guild:
            counter = messages_counter.labels(guild_id=guild.id, guild_name=guild.name, dm=0)
        else:
            counter = messages_counter.labels(guild_id=None, guild_name=None, dm=1)

        counter.inc()

    # @tasks.Task.create(tasks.triggers.IntervalTrigger(seconds=interval))  # TODO wait for polls implementing it
    async def collect_stats(self):
        # Latency stats
        if latency := self.bot.ws.latency:
            latency_gauge.set(latency[-1])

    @naff.listen()
    async def on_guild_join(self, event):
        # ignore guild_join events during bot initialization
        if not self.bot.is_ready:
            return

        guilds_gauge.set(len(self.bot.user._guild_ids))

    @naff.listen()
    async def on_guild_left(self, event):
        guilds_gauge.set(len(self.bot.user._guild_ids))

    # @naff.listen()
    # async def on_guild_unavailable(self, event):
    #     guilds_gauge.set(len(self.bot.user._guild_ids))


def setup(client):
    Stats(client)
