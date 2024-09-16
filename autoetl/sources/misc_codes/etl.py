"""
This file manages the ETL process for the OddsAPI

The ETL process is as follows:
1. Download Query the OddsAPI and get all active games
2. Pipe the results directly into Flatfile or Google PubSub into Storage
3. Resolve the data from the API responses with known entities in the database
4. Upsert the data into the database and send updates to Google PubSub

"""

import asyncio
import json
from datetime import datetime
from logging import getLogger

from dotenv import load_dotenv

from thecrowdsline_data.prisma.fe_client import Prisma as FEPrisma
from thecrowdsline_data.sources.oddsapi.etl_downloader import get_oddsdata
from thecrowdsline_data.sources.oddsapi.etl_resolver import resolve_bets
from thecrowdsline_data.sources.oddsapi.helpers import DateTimeEncoder

load_dotenv()

logger = getLogger(__name__)


async def oddsapi_main(sport: str = "americanfootball_nfl", regions: str = "us"):
    odds = await get_oddsdata(sport=sport, regions=regions)
    fname_with_timestamp = f"/usr/local/data/thecrowdsline/odds/odds_{sport}_{datetime.now().isoformat().split('.')[0]}.json"
    with open(fname_with_timestamp, "w") as fh:
        json.dump(
            [x.model_dump(exclude_none=True) for x in odds], fh, cls=DateTimeEncoder
        )

    db = FEPrisma()
    await db.connect()
    await resolve_bets(odds, db=db)
    await db.disconnect()


if __name__ == "__main__":
    # americanfootball_ncaaf
    # americanfootball_ncaaf_championship_winner

    # americanfootball_nfl
    # americanfootball_nfl_super_bowl_winner

    # icehockey_nhl
    # icehockey_nhl_championship_winner

    # basketball_nba
    # basketball_nba_championship_winner

    # basketball_ncaab
    # basketball_ncaab_championship_winner

    asyncio.run(oddsapi_main(sport="basketball_nba", regions="us"))
