import random
import time
from pprint import pformat

from collections import defaultdict
from datetime import datetime
from typing import Any

import goto_conversion
import tqdm
from cuid2 import cuid_wrapper

from thecrowdsline_data.prisma.fe_client import Prisma
from thecrowdsline_data.prisma.fe_client import Prisma as FEPrisma
from thecrowdsline_data.sources.oddsapi.api import ResponseGetOdds
from thecrowdsline_data.sources.oddsapi.ee_toolshed import (
    get_best_match,
    jarowinkler_similarity_case_insensitive,
)
from thecrowdsline_data.sources.oddsapi.helpers import hash_dictionary
from thecrowdsline_data.sources.oddsapi.models import Bookmaker, Market, Outcome

import requests
import json

cuid_generator = cuid_wrapper()

data_to_property_map = {
    "sport_key": ("League", "name"),
    "sport_title": ("League", "name"),
    "home_team": ("Team", "name"),
    "away_team": ("Team", "name"),
    "id": ("Game", "game_id", "exact"),
    "commence_time": ("Game", "startTime", "difference"),
}

data_to_er_map = {
    "nodes": [
        (0, "League", ["sport_key", "sport_title"]),
        (1, "Team", ["home_team"]),
        (2, "Team", ["away_team"]),
        (3, "Game", ["id", "commence_time"]),
    ],
    "edges": [
        (1, 0, {"fk": "leagueId"}),
        (2, 0, {"fk": "leagueId"}),
        (3, 1, {"fk": "homeTeamId"}),
        (3, 2, {"fk": "awayTeamId"}),
    ],
}

data_to_property_map2 = {
    "game_id": ("Game", "game_id", "exact"),
    "market": ("PropBetType", "id"),
    "sportsbook": ("Sportsbook", "name"),
    "last_update": ("PropBetOdds", "updatedAt", "difference"),
    "outcome": ("Team", "name"),
    "price": [
        ("PropBetOdds", "over_decimal_odds", "difference"),
        ("PropBetOdds", "under_decimal_odds", "difference"),
        ("PropBetOdds", "under_american_odds", "difference"),
        ("PropBetOdds", "over_american_odds", "difference"),
        ("PropBetOdds", "over_fractional_odds", "difference"),
        ("PropBetOdds", "under_fractional_odds", "difference"),
    ],
    "point": ("PropBetOdds", "line", "difference"),
}
data_to_er_map2 = {
    "nodes": [
        (0, "Sportsbook", ["name"]),
        (1, "Game", ["game_id"]),
        (2, "PropBetType", ["market"]),
        (3, "PropBetOdds", ["last_update", "price", "point"]),
        (4, "PropBet", []),
    ],
    "edges": [
        (3, 0, {"fk": "sportsbookId"}),
        (3, 4, {"fk": "propBetId"}),
        (4, 2, {"fk": "betTypeId"}),
        (4, 1, {"fk": "gameId"}),
        (4, 1, {"fk": "teamId"}),
    ],
}


async def resolve_outcome(outcome: Outcome, entities: dict = None, db: Prisma = None):
    new_ents = defaultdict(list)
    for entity_type in ["team", "player"]:
        include = {"PlayerTeamMap": True} if entity_type == "player" else None
        if outcome.name and outcome.name not in ["Over", "Under", "Yes"]:
            if entity := await entity_match_attempt(
                "name",
                outcome.name,
                table=entity_type,
                fuzzy_fields=["id"],
                db=db,
                include=include,
            ):
                new_ents[entity_type].append(entity)
        if outcome.description:
            if entity := await entity_match_attempt(
                "name",
                outcome.description,
                table=entity_type,
                fuzzy_fields=["id"],
                db=db,
                include=include,
            ):
                new_ents[entity_type].append(entity)

    if (
        len(new_ents["team"]) == 0
        and len(new_ents["player"]) == 0
        and outcome.name
        in {
            "Over",
            "Under",
            "Yes",
        }
    ) and outcome.description:
        player = await db.player.create(
            {"name": outcome.description, "id": outcome.description.lower()}
        )
        CACHE.register_insert("player", player)
        new_ents["player"].append(player)

    # assert new_ents.get("team", []) or new_ents.get(
    #     "player", []
    # ), f"Team or player not found for outcome {outcome}"
    return {
        "teams": new_ents.get("team"),
        "players": new_ents.get("player"),
        "propbetodds": {
            "name": outcome.name,
            "decimal_odds": outcome.price,
            "line": outcome.point,
        },
    }


async def entity_match_attempt(
    key="name",
    value=None,
    table="team",
    fuzzy_fields: [str] = None,
    db: Prisma = None,
    include: dict = None,
    scorer=jarowinkler_similarity_case_insensitive,
    score_cutoff=0.9,
):
    where = {key: value}
    fuzzy_fields = fuzzy_fields or []
    entity = await cached_find_first(
        table, where=where, db=db, raise_on_missing=False, include=include
    )
    if entity is None:
        entities = await cached_find_many(
            table, db=db, raise_on_missing=False, include=include
        )
        candidates = {}
        for t in entities:
            if hasattr(t, key):
                candidates[getattr(t, key)] = t.id
            for field in fuzzy_fields:
                if hasattr(t, field):
                    candidates[getattr(t, field)] = t.id
            if hasattr(t, "id"):
                candidates[t.id] = t.id
            if hasattr(t, "aliases"):
                for aliases in t.aliases:
                    candidates[aliases] = t.id
        if entity_id := get_best_match(
            value,
            candidates,
            scorer=scorer,
            score_cutoff=score_cutoff,
        ):
            entity = await cached_find_first(
                table,
                where={"id": entity_id},
                db=db,
                raise_on_missing=True,
                include=include,
            )
            # TODO better caching
            req_hash = hash_dictionary({**where, **(include or {})}, kind="first")
            CACHE[(table, req_hash)] = entity
            if entity.name.lower() != value.lower():
                CACHE.register_warnings(
                    f"Fuzzy match {table}.{key}: {value} -> {entity.name}"
                )

    return entity


async def resolve_propbet(
    prop_type: str,
    game_id: str,
    updatedAt: datetime,
    prop_details: [dict[str, Any]],
    entities: dict = None,
    db: Prisma = None,
):
    global CACHE
    assert prop_type in {"team", "player"}, "Invalid propbet type"
    assert db is not None, "Database not found"

    teams = {p.id: p for prop in prop_details for p in prop.get("teams", []) or []}
    players = {p.id: p for prop in prop_details for p in prop.get("players", []) or []}

    propbet_data = {
        "betTypeId": entities["propbettype"].id,
        "gameId": game_id,
        "playerId": list(players.keys())[0] if len(players) == 1 else None,
        "teamId": list(teams.keys())[0] if len(teams) == 1 else None,
    }
    propbets = await cached_find_many(
        "propbet",
        where={k: v for k, v in propbet_data.items() if v is not None},
        db=db,
        raise_on_missing=False,
    )
    if len(propbets) == 0:
        propbet_data["id"] = cuid_generator()
        propbet = await db.propbet.create(
            {k: v for k, v in propbet_data.items() if v is not None}
        )
        CACHE.register_insert("propbet", propbet)
    elif len(propbets) > 1:
        CACHE.register_warnings(
            "Multiple propbets found {} {}".format(
                [p.id for p in propbets], propbet_data
            )
        )
        propbets.sort(key=lambda x: x.id)
        propbet = propbets[0]
    else:
        propbet = propbets[0]

    if prop_type == "player":
        assert len(players) == 1, "Invalid number of players"
        over_line = None
        under_line = None
        over_odds = None
        under_odds = None
        for outcome in prop_details:
            if outcome["propbetodds"]["name"] == "Over":
                over_odds = outcome["propbetodds"]["decimal_odds"]
                over_line = outcome["propbetodds"]["line"]
            elif outcome["propbetodds"]["name"] == "Under":
                under_odds = outcome["propbetodds"]["decimal_odds"]
                under_line = outcome["propbetodds"]["line"]
            elif outcome["propbetodds"]["name"] == "Yes":
                over_odds = outcome["propbetodds"]["decimal_odds"]
                over_line = outcome["propbetodds"]["line"]
                under_line = over_line
            else:
                raise ValueError(
                    "Invalid outcome name {}".format(outcome["propbetodds"]["name"])
                )
        # assert over_line is not None and under_line is not None, "Over/under not found"
        assert over_line == under_line, "Over/under lines do not match"

        if under_odds is None:
            novig_odds = 1 / over_odds
        else:
            novig_odds = goto_conversion.goto_conversion([over_odds, under_odds])[0]

        new_propbetodd = {
            "id": cuid_generator(),
            "updatedAt": updatedAt,
            "propBetId": propbet.id,
            "sportsbookId": entities["sportsbook"].id,
            "line": over_line,
            "condition": None,
            "over_decimal_odds": over_odds,
            "under_decimal_odds": under_odds,
            "over_american_odds": None,
            "under_american_odds": None,
            "over_fractional_odds": None,
            "under_fractional_odds": None,
            "novig_implied_pct": novig_odds,
        }

    if prop_type == "team":
        # Create over/under, home team is over
        over_line = None
        under_line = None
        over_odds = None
        under_odds = None
        over_team = None
        under_team = None

        for outcome in prop_details:
            team_ids = [team.id for team in outcome.get("teams", []) or []] or [
                entities["game"].homeTeamId,
                entities["game"].awayTeamId,
            ]
            for team_id in team_ids:
                if team_id == entities["game"].homeTeamId:
                    over_team = team_id
                    over_odds = outcome["propbetodds"]["decimal_odds"]
                    over_line = outcome["propbetodds"]["line"]
                elif team_id == entities["game"].awayTeamId:
                    under_team = team_id
                    under_odds = outcome["propbetodds"]["decimal_odds"]
                    under_line = outcome["propbetodds"]["line"]
                else:
                    raise ValueError("Invalid team")
        assert over_team is not None and under_team is not None, "Over/under not found"
        # Confirm the lines are the same
        assert (over_line is None and under_line is None) or (
            over_line in [under_line, -1 * under_line]
        ), "Over/under lines do not match"

        novig_odds = goto_conversion.goto_conversion([over_odds, under_odds])
        new_propbetodd = {
            "id": cuid_generator(),
            "updatedAt": updatedAt,
            "propBetId": propbet.id,
            "sportsbookId": entities["sportsbook"].id,
            "line": over_line,
            "condition": None,
            "over_decimal_odds": over_odds,
            "under_decimal_odds": under_odds,
            "over_american_odds": None,
            "under_american_odds": None,
            "over_fractional_odds": None,
            "under_fractional_odds": None,
            "novig_implied_pct": novig_odds[0],
        }

    def odds_close(a, b):
        return False if a is None or b is None else abs(float(a) - float(b)) < 1e-6

    # Merge outcomes into propbetodds
    propbetodds = await cached_find_many(
        "propbetodds",
        where={"propBetId": propbet.id, "sportsbookId": entities["sportsbook"].id},
        db=db,
        raise_on_missing=False,
    )
    if len(propbetodds):
        matches = [
            b
            for b in propbetodds
            if (new_propbetodd["updatedAt"] >= b.updatedAt)
            and (
                (new_propbetodd["line"] is None and b.line is None)
                or (odds_close(new_propbetodd["line"], b.line))
            )
            and odds_close(new_propbetodd["under_decimal_odds"], b.under_decimal_odds)
            and odds_close(new_propbetodd["over_decimal_odds"], b.over_decimal_odds)
        ]
        if len(matches):
            return

    propbetodd = await db.propbetodds.create(new_propbetodd)
    CACHE.register_insert("propbetodds", propbetodd)
    return propbetodd


async def resolve_market(market: Market, entities: dict = None, db: Prisma = None):
    global CACHE
    propbettype = await entity_match_attempt(
        "name", market.key, table="propbettype", fuzzy_fields=["id"], db=db
    )
    if propbettype is None:
        propbettype = await db.propbettype.create(
            {"name": market.key.replace("_", " "), "id": market.key, "aliases": []}
        )
        CACHE.register_insert("propbettype", propbettype)
    assert propbettype is not None, "Propbettype not found"

    entities["propbettype"] = propbettype
    outcomes = []
    for outcome in market.outcomes:
        outcomes.append(await resolve_outcome(outcome, entities=entities, db=db))

    # Check if outcomes are consistent
    teams = {}
    players = {}
    for outcome in outcomes:
        for t in outcome.get("teams", []) or []:
            teams[t.id] = t
            assert t.id in {
                entities["game"].homeTeamId,
                entities["game"].awayTeamId,
            }, "Outcomes did not align with game"

        for p in outcome.get("players", []) or []:
            # Check that player is on the correct team
            players[p.id] = p

            if len(p.PlayerTeamMap or []) == 0:
                CACHE.register_warnings(f"Player {p.id} {p.name} is missing a team")
                continue
            matching_teams = [
                t.teamId
                for t in p.PlayerTeamMap or []
                if t.endedAt is None
                and t.teamId
                in {
                    entities["game"].homeTeamId,
                    entities["game"].awayTeamId,
                }
            ]
            if not matching_teams:
                CACHE.register_warnings(
                    f"Player {p.id} {p.name} is missing a team {p.PlayerTeamMap}"
                )

    props = defaultdict(list)
    for outcome in outcomes:
        outcome_teams = outcome.get("teams", []) or []
        outcome_players = outcome.get("players", []) or []
        if len(outcome_teams) == 0 and len(outcome_players):
            for player in outcome_players:
                props[("player", entities["game"].id, player.id)].append(outcome)
        elif len(outcome_teams) and len(outcome_players) == 0:
            props[("team", entities["game"].id, None)].append(outcome)
        elif (
            len(outcome_teams)
            and len(outcome_players)
            and market.key in {"h2h", "spreads", "totals"}
        ):
            # For the case of accidental player identification
            outcome["players"] = []
            props[("team", entities["game"].id, None)].append(outcome)
        elif market.key == "totals":
            # For the case of accidental team identification
            outcome["teams"] = []
            props[("team", entities["game"].id, None)].append(outcome)
        else:
            CACHE.register_warnings(f"Unknown outcome type {market.key} - {outcome}")
            # TODO Support this
            return

    entities["players"] = players
    entities["teams"] = teams
    for (prop_type, game_id, _), prop_details in props.items():
        try:
            await resolve_propbet(
                prop_type,
                game_id,
                market.last_update,
                prop_details,
                entities=entities,
                db=db,
            )
        except Exception as e:
            CACHE.register_warnings(f"Error resolving propbet {e}: {prop_details}")


async def resolve_bookmaker(
    bookmaker: Bookmaker, entities: dict = None, db: Prisma = None
):
    entities = entities or {}
    assert "game" in entities, "Game not found"
    assert db is not None, "Database not found"
    sportsbook = await entity_match_attempt(
        "name", bookmaker.title, table="sportsbook", fuzzy_fields=["id", "name"], db=db
    )
    if sportsbook is None:
        sportsbook = await entity_match_attempt(
            "name",
            bookmaker.key,
            table="sportsbook",
            fuzzy_fields=["id", "name"],
            db=db,
        )
    if sportsbook is None:
        sportsbook = await db.sportsbook.create(
            {"name": bookmaker.title, "id": bookmaker.key}
        )
        CACHE.register_insert("sportsbook", sportsbook)
    assert sportsbook is not None, "Sportsbook not found"
    entities["sportsbook"] = sportsbook
    for market in bookmaker.markets:
        await resolve_market(market, entities=entities, db=db)


class PoorMansCache:
    def __init__(self):
        self.cache = defaultdict(dict)
        self.misses = 0
        self.misstime = 0
        self.visits = 0
        self.inserts = defaultdict(list)
        self.warnings = set()

    def __getitem__(self, key):
        return self.cache[key[0]].get(key[1])

    def __setitem__(self, key, value):
        self.cache[key[0]][key[1]] = value

    def __delitem__(self, key):
        del self.cache[key]

    def register_warnings(self, msg):
        self.warnings.add(msg)
        print(msg)

    def register_insert(self, table, data):
        self.inserts[table].append(data)
        del self.cache[table]
        print(f"Created {table} {data}")

    def send_update(self, total_time=0):
        # Send to slack webhook
        msg = f"""
        OddsAPI updated: {total_time}
        **Warnings**:\n{pformat(sorted(self.warnings), width=120)}
        """[
            :4_000
        ].strip()
        rs = requests.post(
            "https://hooks.slack.com/services/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",
            data=json.dumps({"text": msg}),
        )
        for k, items in self.inserts.items():
            msg = f"""
            **Inserted {k} ({len(items)})**:\n{pformat(items, width=120)}
            """[
                :4_000
            ].strip()
            rs = requests.post(
                "https://hooks.slack.com/services/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",
                data=json.dumps({"text": msg}),
            )
            time.sleep(1)
        print(rs.status_code, rs.reason)


CACHE = PoorMansCache()


async def cached_find_first(
    table: str,
    where=None,
    db: Prisma = None,
    raise_on_missing=False,
    include: dict[str:bool] = None,
):
    global CACHE
    t = datetime.now()
    if where is None:
        where = {}
    req_hash = hash_dictionary({**where, **(include or {})}, kind="first")
    result = CACHE[(table, req_hash)]
    CACHE.visits += 1
    if result is None:
        result = await getattr(db, table).find_first(where=where, include=include)
        if result is not None:
            CACHE[(table, req_hash)] = result
        CACHE.misses += 1
        CACHE.misstime += (datetime.now() - t).total_seconds()
    if raise_on_missing and result is None:
        raise ValueError(f"Could not find {table} with {where}")
    return result


async def cached_find_many(
    table: str,
    where=None,
    db: Prisma = None,
    raise_on_missing=False,
    include: dict[str:bool] = None,
):
    global CACHE
    t = datetime.now()
    if where is None:
        where = {}
    req_hash = hash_dictionary({**where, **(include or {})}, kind="many")
    result = CACHE[(table, req_hash)]
    CACHE.visits += 1
    if result is None:
        t = datetime.now()
        result = CACHE[(table, req_hash)] = await getattr(db, table).find_many(
            where=where, include=include
        )
        CACHE.misses += 1
        CACHE.misstime += (datetime.now() - t).total_seconds()
    if raise_on_missing and result is None:
        raise ValueError(f"Could not find {table} with {where}")
    return result


async def resolve_bet(bet: ResponseGetOdds, db: Prisma = None):
    # Here we need to resolve
    must_disconnect = False
    if db is None:
        db = FEPrisma()
        await db.connect()
        must_disconnect = True

    # assert bet.sport_title == "NFL", "unknown League"
    league = await cached_find_first(
        "league", where={"name": bet.sport_title}, db=db, raise_on_missing=True
    )
    teams = await cached_find_many(
        "team", where={"leagueId": league.id}, db=db, raise_on_missing=False
    )
    home_team = await find_matching_team_from_bet(bet.home_team, db, league, teams)
    away_team = await find_matching_team_from_bet(bet.away_team, db, league, teams)

    game = await cached_find_first(
        "game", where={"game_id": bet.id}, db=db, raise_on_missing=False
    )
    if game is None:  # Check if similar game exists but with different id
        games = await cached_find_many(
            "game",
            where={"homeTeamId": home_team.id, "awayTeamId": away_team.id},
            db=db,
            raise_on_missing=False,
        )
        games.sort(key=lambda x: abs(x.startTime - bet.commence_time))
        if (
            len(games)
            and (bet.commence_time - games[0].startTime).total_seconds() < 60 * 60 * 24
        ):
            raise ValueError(
                f"Unknown game {bet.id} conflicting with {games[0].game_id}"
            )
    if game is None:
        game = await db.game.create(
            {
                "game_id": bet.id,
                "startTime": bet.commence_time,
                "season": bet.commence_time.year,
                "homeTeam": {
                    "connect": {"id": home_team.id}
                },  # Assuming home_team.id is the ID of an existing team
                "awayTeam": {
                    "connect": {"id": away_team.id}
                },  # Assuming away_team.id is the ID of an existing team
            }
        )
        CACHE.register_insert("game", game)
    assert game is not None, "Game not found"

    for bookmaker in bet.bookmakers:
        await resolve_bookmaker(bookmaker, entities={"game": game}, db=db)

    if must_disconnect:
        await db.disconnect()


async def find_matching_team_from_bet(team_name, db, league, teams, autocreate=True):
    team = await cached_find_first(
        "team",
        where={"name": team_name, "leagueId": league.id},
        db=db,
        raise_on_missing=False,
    )
    if team is None:
        team = get_best_match(
            team_name,
            {t.name: t.id for t in teams},
            scorer=jarowinkler_similarity_case_insensitive,
            score_cutoff=0.9,
        )
    if team is None:
        if autocreate is False:
            yes_or_no =  or input(f"Unknown team {team_name}, create?")
            if yes_or_no.lower() != "y":
                raise ValueError(f"Unknown team {team_name}")
        team = await db.team.create(
            {
                "name": team_name,
                "team_id": team_name.lower(),
                "leagueId": league.id,
            }
        )
        CACHE.register_insert("team", team)
    return team


async def resolve_bets(bets: list[ResponseGetOdds], db: Prisma):
    t = datetime.now()
    random.shuffle(bets)
    for bet in tqdm.tqdm(bets, desc="Bets"):
        await resolve_bet(bet, db)

    total_time = (datetime.now() - t).total_seconds()
    CACHE.send_update(total_time=total_time)
    print(f"Total time: {total_time}")
    print(f"Cache visits: {CACHE.visits}")
    print(f"Cache miss count: {CACHE.misses}")
    print(f"Cache miss %: {CACHE.misses / CACHE.visits * 100}")
    print(f"Cache miss time: {CACHE.misstime}")
    print(f"Cache miss time %: {CACHE.misstime / total_time * 100}")
