from typing import Any

import naff
from naff import InteractionContext, SlashCommand
from nafftrack.stats import (
    interactions_registered,
    interactions_sync,
    slash_commands_perf,
    slash_commands_running,
)


class StatsClient(naff.Client):
    async def synchronise_interactions(self) -> None:
        with interactions_sync.time():
            await super().synchronise_interactions()

        amount = len(self.application_commands)
        interactions_registered.set(amount)

    async def _run_slash_command(self, command: SlashCommand, ctx: InteractionContext) -> Any:
        labels = dict(
            base_name=command.name.default,
            group_name=command.group_name.default,
            command_name=command.sub_cmd_name.default,
            command_id=command.cmd_id,
        )

        if guild := ctx.guild:
            guild_labels = dict(guild_id=guild.id, guild_name=guild.name, dm=0)
        else:
            guild_labels = dict(guild_id=None, guild_name=None, dm=1)

        labels.update(guild_labels)

        perf = slash_commands_perf.labels(**labels)
        running = slash_commands_running.labels(**labels)
        with perf.time(), running.track_inprogress():
            return await super()._run_slash_command(command, ctx)
