import asyncio
import json
from datetime import datetime, timezone
from logging import getLogger
import random

from dotenv import load_dotenv

# from taskforce_api.services.ee.chattcl_models import upsert_oddsapi_odds

from thecrowdsline_data.prisma.fe_client import Prisma as FEPrisma
from thecrowdsline_data.sources.oddsapi.api import TheOddsAPI

load_dotenv()

logger = getLogger(__name__)

null = None


async def process_odds(odds, client: FEPrisma):
    for game in odds:
        # Get the game id or create it if it doesn't exist
        print(game["home_team"], game["away_team"])
        for bookmaker in game["bookmakers"]:
            # get the bookmaker id or create it if it doesn't exist
            print(bookmaker["title"])
            for market in bookmaker["markets"]:
                # get the propbet id or create it if it doesn't exist
                print(market["key"])
                for outcome in market["outcomes"]:
                    # get prop-bet value and save it if its changed
                    # Send a message to the user if it has changed
                    print(outcome["name"], outcome["price"])


async def get_sports_game_odds(
    sport: str,
    game_id: str | None = None,
    regions: str = "us",
    markets: str | None = None,
):
    api = TheOddsAPI()
    assert "nfl" in sport, "Only NFL is supported"
    t = datetime.now(timezone.utc).isoformat().split(".")[0].replace(":", "")
    asyncio.sleep(random.random())
    return await api.get_odds(
        sport, eventIds=game_id, regions=regions, markets=markets or api.nfl_markets()
    )


async def get_sports_main_odds_markets(
    sport: str, regions: str = "us", markets: str | None = None
):
    api = TheOddsAPI()
    t = datetime.now(timezone.utc).isoformat().split(".")[0].replace(":", "")
    odds = await api.get_odds(sport, regions=regions, markets=markets or api.markets)

    # await upsert_oddsapi_odds(odds)

    with open(
        f"/home/sean/repos/closedloop/taskforce/taskforce-api/taskforce_api/services/ee/chattcl_feeds/data/oddsapi-requests/odds-{sport}-{regions}-{t}.json",
        "w",
    ) as f:
        json.dump(odds, f)

    tasks = [
        get_sports_game_odds(sport, game["id"], regions=regions, markets=market)
        for game in odds
        for market in api.nfl_markets()
    ]
    game_odds = await asyncio.gather(*tasks)

    await upsert_oddsapi_odds(game_odds)

    # # Get the game id or create it if it doesn't exist
    # print(game["home_team"], game["away_team"])
    # for bookmaker in game["bookmakers"]:
    #     # get the bookmaker id or create it if it doesn't exist
    #     print(bookmaker["title"])
    #     for market in bookmaker["markets"]:
    #         # get the propbet id or create it if it doesn't exist
    #         print(market["key"])
    #         for outcome in market["outcomes"]:
    #             # get prop-bet value and save it if its changed
    #             # Send a message to the user if it has changed
    #             print(outcome["name"], outcome["price"])
    return odds + game_odds


async def main(sport="americanfootball_nfl", regions="us"):
    api = TheOddsAPI()
    # Gets active sports
    if sport is None:
        sports = await api.get_sports()
    elif isinstance(sport, str):
        sports = [sport]

    r = [get_sports_main_odds_markets(s, regions=regions, markets=None) for s in sports]
    await asyncio.gather(*r)


if __name__ == "__main__":
    # repeat every 5 minutes

    asyncio.run(main())
    # api = TheOddsAPI()
    # sports = api.get_sports()
    # odds = api.get_odds("americanfootball_nfl", regions="us", markets=api.markets)
    # pprint(odds)

    # from taskforce_api.prisma.fe_client import Prisma as FEPrisma

    # conn = PrismaClient.connect()
    # # odds is a list of games
    # # each game has a list of bookmakers
    # # each bookmaker has a list of markets
    # # each market has a list of outcomes
    # # each outcome has a name and a price
    # for game in odds:
    #     # Get the game id or create it if it doesn't exist
    #     print(game["home_team"], game["away_team"])
    #     for bookmaker in game["bookmakers"]:
    #         # get the bookmaker id or create it if it doesn't exist
    #         print(bookmaker["title"])
    #         for market in bookmaker["markets"]:
    #             # get the propbet id or create it if it doesn't exist
    #             print(market["key"])
    #             for outcome in market["outcomes"]:
    #                 # get prop-bet value and save it if its changed
    #                 # Send a message to the user if it has changed
    #                 print(outcome["name"], outcome["price"])

    # # Repeat for each game and ask detailed requests for each prop bet
    # # Count responses.  Repeat every minute or so
    # for game in odds:
    #     odds2 = api.get_game_odds("americanfootball_nfl", game_id=None, regions="us", markets=api.nfl_markets)
    #     pprint(odds2)
