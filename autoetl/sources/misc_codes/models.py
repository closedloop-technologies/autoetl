from datetime import datetime

from pydantic import BaseModel, Field


class Outcome(BaseModel):
    name: str
    price: float


class Market(BaseModel):
    key: str
    last_update: datetime
    outcomes: list[Outcome]


class Bookmaker(BaseModel):
    key: str
    title: str
    last_update: datetime
    markets: list[Market]


class Event(BaseModel):
    id: str = Field(..., alias="id")
    sport_key: str = Field(..., alias="sport_key")
    sport_title: str = Field(..., alias="sport_title")
    commence_time: datetime = Field(..., alias="commence_time")
    home_team: str = Field(..., alias="home_team")
    away_team: str = Field(..., alias="away_team")
    bookmakers: list[Bookmaker] = Field(..., alias="bookmakers")


class Sport(BaseModel):
    active: bool  # ': True,
    description: str  # ': 'US Football',
    group: str  # ': 'American Football',
    has_outrights: bool  # ': False,
    key: str  # ': 'americanfootball_nfl',
    title: str  # ': 'NFL'
