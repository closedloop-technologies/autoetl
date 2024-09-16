from datetime import datetime

from pydantic import BaseModel, Field

from thecrowdsline_data.sources.base_api import BaseAPI
from thecrowdsline_data.sources.oddsapi.models import Sport


class Outcome(BaseModel):
    name: str = Field(..., alias="name")
    description: str | None = None
    price: float = Field(..., alias="price")
    point: float | None = None


class Markets(BaseModel):
    key: str = Field(..., alias="key")
    last_update: datetime = Field(..., alias="last_update")
    outcomes: list[Outcome] = Field(..., alias="outcomes")


class BookMaker(BaseModel):
    key: str = Field(..., alias="key")
    title: str = Field(..., alias="title")
    markets: list[Markets] = Field(..., alias="markets")


class ResponseGetOdds(BaseModel):
    id: str = Field(..., alias="id")
    sport_key: str = Field(..., alias="sport_key")
    sport_title: str = Field(..., alias="sport_title")
    commence_time: datetime
    home_team: str = Field(..., alias="home_team")
    away_team: str = Field(..., alias="away_team")
    bookmakers: list[BookMaker] = Field(..., alias="bookmakers")


class TheOddsAPI(BaseAPI):
    def __init__(self, api_key: str = None):
        super().__init__(
            api_key=api_key,
            api_env="ODDSAPI_API_KEY",
            base_url="https://api.the-odds-api.com/v4/",
        )

    async def get_sports(self, all: bool = False) -> list[Sport]:
        return [
            Sport(**s) for s in await self._get("sports", {"all": str(all).lower()})
        ]

    @property
    def regions(self):
        return ["us", "us2", "uk", "eu", "au"]

    @property
    def markets(self):
        """General markets for all sports
        excludes: "outrights", "h2h_lay", "outrights_lay"
        """
        return ["h2h", "spreads", "totals"]

    def nfl_markets(self):
        return [
            "player_pass_tds",  # Pass Touchdowns (Over/Under)
            "player_pass_yds",  # Pass Yards (Over/Under)
            "player_pass_completions",  # Pass Completions (Over/Under)
            "player_pass_attempts",  # Pass Attempts (Over/Under)
            "player_pass_interceptions",  # Pass Intercepts (Over/Under)
            "player_pass_longest_completion",  # Pass Longest Completion (Over/Under)
            "player_rush_yds",  # Rush Yards (Over/Under)
            "player_rush_attempts",  # Rush Attempts (Over/Under)
            "player_rush_longest",  # Longest Rush (Over/Under)
            "player_receptions",  # Receptions (Over/Under)
            "player_reception_yds",  # Reception Yards (Over/Under)
            "player_reception_longest",  # Longest Reception (Over/Under)
            "player_kicking_points",  # Kicking Points (Over/Under)
            "player_field_goals",  # Field Goals (Over/Under)
            "player_tackles_assists",  # Tackles + Assists (Over/Under)
            "player_1st_td",  # 1st Touchdown Scorer (Yes/No)
            "player_last_td",  # Last Touchdown Scorer (Yes/No)
            "player_anytime_td",  # Anytime Touchdown Scorer (Yes/No)
        ]

    def nba_markets(self):
        return [
            "player_points",  # Points (Over/Under)
            "player_rebounds",  # Rebounds (Over/Under)
            "player_assists",  # Assists (Over/Under)
            "player_threes",  # Threes (Over/Under)
            "player_blocks",  # Blocks (Over/Under)
            "player_steals",  # Steals (Over/Under)
            "player_blocks_steals",  # Blocks + Steals (Over/Under)
            "player_turnovers",  # Turnovers (Over/Under)
            "player_points_rebounds_assists",  # Points + Rebounds + Assists (Over/Under)
            "player_points_rebounds",  # Points + Rebounds (Over/Under)
            "player_points_assists",  # Points + Assists (Over/Under)
            "player_rebounds_assists",  # Rebounds + Assists (Over/Under)
            "player_first_basket",  # First Basket Scorer (Yes/No)
            "player_double_double",  # Double Double (Yes/No)
            "player_triple_double",  # Triple Double (Yes/No)
        ] + [
            "player_points_alternate",  # Alternate Points (Over/Under)
            "player_rebounds_alternate",  # Alternate Rebounds (Over/Under)
            "player_assists_alternate",  # Alternate Assists (Over/Under)
            "player_blocks_alternate",  # Alternate Blocks (Over/Under)
            "player_steals_alternate",  # Alternate Steals (Over/Under)
            "player_threes_alternate",  # Alternate Threes (Over/Under)
            "player_points_assists_alternate",  # Alternate Points + Assists (Over/Under)
            "player_points_rebounds_alternate",  # Alternate Points + Rebounds (Over/Under)
            "player_rebounds_assists_alternate",  # Alternate Rebounds + Assists (Over/Under)
            "player_points_rebounds_assists_alternate",  # Alternate Points + Rebounds + Assists (Over/Under)
        ]

    # Implement this # GET /v4/sports/{sport}/odds/?apiKey={apiKey}&regions={regions}&markets={markets}
    async def get_odds(
        self,
        sport: str,
        regions: str | None = None,
        markets: str | None = None,
        dateFormat: str | None = None,
        oddsFormat: str | None = None,
        eventIds: str | None = None,
        bookmakers: str | None = None,
        commenceTimeFrom: str | None = None,
        commenceTimeTo: str | None = None,
    ) -> list[ResponseGetOdds]:
        assert regions in self.regions, f"regions must be one of {self.regions}"

        params = {
            "regions": regions or ",".join(self.regions),
            "markets": markets or "h2h",
            "dateFormat": dateFormat or "iso",
            "oddsFormat": oddsFormat or "decimal",
        }

        if bookmakers is not None:
            params["bookmakers"] = bookmakers
        if commenceTimeFrom is not None:
            params["commenceTimeFrom"] = commenceTimeFrom
        if commenceTimeTo is not None:
            params["commenceTimeTo"] = commenceTimeTo

        if eventIds is None:
            return await self._get(f"sports/{sport}/odds", params)
        else:
            return await self._get(f"sports/{sport}/events/{eventIds}/odds", params)
