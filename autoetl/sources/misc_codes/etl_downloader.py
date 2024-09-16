import asyncio
from logging import getLogger

from thecrowdsline_data.sources.oddsapi.api import ResponseGetOdds, TheOddsAPI
from thecrowdsline_data.sources.oddsapi.helpers import (
    collect_coroutines,
    object_to_coroutine,
)

logger = getLogger(__name__)


async def get_sports_game_odds(
    sport: str,
    game_id: str | None = None,
    regions: str = "us",
    markets: str | None = None,
):
    api = TheOddsAPI()
    if "nfl" in sport:
        default_markets = api.nfl_markets()
    elif "nba" in sport:
        default_markets = api.nba_markets()
    else:
        raise ValueError(f"Sport {sport} not supported")
    markets = [markets] if isinstance(markets, str) else markets or default_markets
    market = ",".join(markets)

    yield api.get_odds(sport, eventIds=game_id, regions=regions, markets=market)


async def get_sports_main_odds_markets(
    sport: str, regions: str = "us", markets: str | None = None
):
    api = TheOddsAPI()
    markets = markets or api.markets
    all_odds = []
    for market in markets:
        all_odds.extend(await api.get_odds(sport, regions=regions, markets=market))

    for odds in all_odds:
        yield asyncio.create_task(object_to_coroutine(ResponseGetOdds(**odds)))

    for game in all_odds:
        async for task in get_sports_game_odds(
            sport, game["id"], regions=regions, markets=api.nfl_markets()
        ):
            yield asyncio.create_task(task)


async def get_oddsdata(sport="americanfootball_nfl", regions="us"):
    api = TheOddsAPI()

    if sport is None:
        sports = await api.get_sports()
    elif isinstance(sport, str):
        sports = [sport]

    results = []
    for s in sports:
        coroutines = await collect_coroutines(
            get_sports_main_odds_markets(s, regions=regions, markets=api.markets)
        )
        initial_results = await asyncio.gather(*coroutines)
        additional_coroutines = []
        for result in initial_results:
            if "'coroutine'" in str(type(result)):
                additional_coroutines.append(result)
            else:
                results.append(result)
        results.extend(
            [
                ResponseGetOdds(**odds)
                for odds in await asyncio.gather(*additional_coroutines)
            ]
        )
    return [
        r if isinstance(r, ResponseGetOdds) else ResponseGetOdds(**r) for r in results
    ]
