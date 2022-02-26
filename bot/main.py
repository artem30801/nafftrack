import logging
import os

import dis_snek
from stats import stats_client


logging.basicConfig(level=logging.INFO)

debug = bool(int(os.environ.get("DEBUG", "0").strip()))
debug_scope = os.environ.get("DEBUG_SCOPE", dis_snek.MISSING)
debug_scope = debug_scope.strip() if debug_scope else debug_scope

client = stats_client.StatsSnake(
    asyncio_debug=debug,
    sync_interactions=True,
    debug_scope=debug_scope,
)

client.grow_scale("dis_snek.ext.debug_scale")
client.grow_scale("stats.stats_scale")

client.start(os.environ["DISCORD_TOKEN"].strip())
