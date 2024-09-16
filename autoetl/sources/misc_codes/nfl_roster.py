#!/usr/bin/env python3
"""

nfl.import_depth_charts([2023])
import_pbp_data() - import play-by-play data
import_weekly_data() - import weekly player stats
import_seasonal_data() - import seasonal player stats
import_snap_counts() - import weekly snap count stats
import_ngs_data() - import NGS advanced analytics
import_qbr() - import QBR for NFL or college
import_seasonal_pfr() - import advanced stats from PFR on a seasonal basis
import_weekly_pfr() - import advanced stats from PFR on a weekly basis
import_officials() - import details on game officials
import_schedules() - import weekly teams schedules
import_seasonal_rosters() - import yearly team rosters
import_weekly_rosters() - import team rosters by week, including in-season updates
import_players() - import descriptive data for all players
import_depth_charts() - import team depth charts
import_injuries() - import team injury reports
import_ids() - import mapping of player ids for more major sites
import_contracts() - import contract data
import_win_totals() - import win total lines for teams
import_sc_lines() - import weekly betting lines for teams
import_draft_picks() - import draft pick history
import_draft_values() - import draft value models by pick
import_combine_data() - import combine stats
import_ftn_data() - import FTN charting data
see_pbp_cols() - return list of play-by-play columns
see_weekly_cols() - return list of weekly stat columns
import_team_desc() - import descriptive data for team viz
cache_pbp() - save pbp files locally to allow for faster loading
clean_nfl_data() - clean df by aligning common name diffs
"""

import hashlib
import os
import re
import tempfile
from datetime import datetime

import nfl_data_py as nfl
import numpy as np
import pandas as pd
from prefect import flow, task
from pydantic import BaseModel, Field


def remove_parens(text):
    return " ".join(re.sub(r"\([^)]*\)", "", text).split())


def clean_player_names(name):
    bad_last_name = [
        "S",
        "FS",
        "ll",
        "SS",
        "CB",
        "lll",
        "OLB",
        "ILB",
        "Jr",
        "Jr.",
        "Sr",
        "Sr.",
        "II",
        "III",
        "IV",
    ]

    replace_pairs = [
        ["D. Parham", "Donald Parham"],
        ["Jr", ""],
        ["III", ""],
        ["II", ""],
        ["Travis Ettienne", "Travis Etienne"],
        ["Josh Dobbs", "Joshua Dobbs"],
        ["Joshua Palmer", "Josh Palmer"],
        ["Gabe Davis", "Gabriel Davis"],
        ["Pat Surtain", "Patrick Surtain"],
        ["Foye Oluokun", "Foyesade Oluokun"],
        [".", ""],
        ["Philip Walker", "PJ Walker"],
        ["Phillip Walker", "PJ Walker"],
        ["’", ""],
        ["'", ""],
        ["Mitchell Trubisky", "Mitch Trubisky"],
        ["Jeffery Wilson", "Jeff Wilson"],
        ["Dwayne Eskridge", "Dee Eskridge"],
        ["Rod Williams", "Rodney Williams"],
        ["Chris Brooks", "Christopher Brooks"],
        ["Nathaniel Dell", "Tank Dell"],
        ["Adam Theilen", "Adam Thielen"],
        ["Amon Ra Stbrown", "Amon-Ra St Brown"],
        ["Andrei Ios As", "Andrei Iosivas"],
        ["Andrei Ios Ias", "Andrei Iosivas"],
        ["Andrei Iosas", "Andrei Iosivas"],
        ["Andrei Iosias", "Andrei Iosivas"],
        ["Andrei Iosivas", "Andrei Iosivas"],
        ["Drew Ogletree", "Andrew Ogletree"],
        ["Brandon Mcmanu", "Brandon Mcmanus"],
        ["Chandon Sull An", "Chandon Sullivan"],
        ["Chandon Sullan", "Chandon Sullivan"],
        ["Chig Okonkwo", "Chigoziem Okonkwo"],
        ["Dine Deablo", "Divine Deablo"],
        ["Di ne Deablo", "Divine Deablo"],
        ["Deonte Harris", "Deonte Harty"],
        ["D Moore", "dj Moore"],
        ["Christopher Brooks", "chris brooks"],
        ["Ed Oler", "Ed Oliver"],
        ["Isiah Hodgins", "Isaiah Hodgins"],
        ["Isaiah Oler", "Isaiah Oliver"],
        ["Jahmyr Giabbs", "Jahmyr Gibbs"],
        ["Josh Oler", "Josh Oliver"],
        ["Josh Ol Er", "Josh Oliver"],
        ["Justin Hebert", "Justin Herbert"],
        ["Keontay Ingram", "Keaontay Ingram"],
        ["Kevin Gens", "Kevin Givens"],
        ["Kevin G Ens", "Keving Givens"],
        ["Kyle Philips", "Kyle Phillips"],
        ["M Jones", "Marvin Jones"],
        ["Paris Campbell", "Parris Campbell"],
        ["Rer Cracraft", "River Cracraft"],
        ["R Er Cracraft", "River Cracraft"],
        ["R Robertson Harris", "Roy Robertson-Harris"],
        ["Roy Robertson Harris", "Roy Robertson-Harris"],
        ["Russsell Wilson", "Russell Wilson"],
        ["Scott Miller", "Scotty Miller"],
        ["Stephen Sullan", "Stephen Sullivan"],
        ["Stephen Sull An", "Stephen Sullivan"],
        ["Trevon Moehrig Woodard", "Trevon Moehrig"],
        ["Wilie Snead", "Willie Snead"],
        ["Shaquil Barrett", "Shaq Barrett"],
        ["Daxton Hill", "Dax Hill"],
        ["anandrew ogletree", "andrew ogletree"],
        ["timarvin jones", "tim jones"],
        ["chosen anderson", "robbie chosen"],
        ["Nathaniel Tank Dell", "tank dell"],
        ["Brandon McManuss", "brandon mcmanus"],
        ["Eli Mitchell", "elijah mitchell"],
        ["eli mitchell", "elijah mitchell"],
    ]

    replace_pairs += [[n[0].lower(), n[1].lower()] for n in replace_pairs]
    replace_pairs += [["oler", "oliver"], ["ol er", "oliver"]]

    for pair in replace_pairs:
        name = name.replace(pair[0], pair[1])
    name = remove_parens(name)

    name_split = name.split(" ")
    if name_split[-1] in bad_last_name:
        name_split = name_split[:-1]

    name = " ".join(name_split).strip().lower()
    name = " ".join(name.split(",")[::-1]).strip()
    return name


team_abbr_to_mascot_map = {
    "ari": "cardinals",
    "atl": "falcons",
    "bal": "ravens",
    "buf": "bills",
    "car": "panthers",
    "chi": "bears",
    "cin": "bengals",
    "cle": "browns",
    "dal": "cowboys",
    "den": "broncos",
    "det": "lions",
    "gb": "packers",
    "gbp": "packers",
    "hou": "texans",
    "ind": "colts",
    "jax": "jaguars",
    "jac": "jaguars",
    "kc": "chiefs",
    "kcc": "chiefs",
    "la": "rams",
    "lar": "rams",
    "lac": "chargers",
    "lv": "raiders",
    "lvr": "raiders",
    "mia": "dolphins",
    "min": "vikings",
    "ne": "patriots",
    "nep": "patriots",
    "no": "saints",
    "nos": "saints",
    "nyg": "giants",
    "nyj": "jets",
    "phi": "eagles",
    "pit": "steelers",
    "sea": "seahawks",
    "sf": "49ers",
    "sfo": "49ers",
    "tb": "buccaneers",
    "tbb": "buccaneers",
    "ten": "titans",
    "was": "commanders",
    "wsh": "commanders",
    "hst": "texans",
    "arz": "cardinals",
    "blt": "ravens",
    "clv": "browns",
    "ari": "cardinals",
    "atl": "falcons",
    "bal": "ravens",
    "buf": "bills",
    "car": "panthers",
    "chi": "bears",
    "cin": "bengals",
    "cle": "browns",
    "dal": "cowboys",
    "den": "broncos",
    "det": "lions",
    "gb": "packers",
    "hou": "texans",
    "ind": "colts",
    "jax": "jaguars",
    "jac": "jaguars",
    "kc": "chiefs",
    "la": "rams",
    "lar": "rams",
    "lac": "chargers",
    "lv": "raiders",
    "mia": "dolphins",
    "min": "vikings",
    "ne": "patriots",
    "no": "saints",
    "nyg": "giants",
    "nyj": "jets",
    "phi": "eagles",
    "pit": "steelers",
    "sea": "seahawks",
    "sd": "chargers",
    "sl": "rams",
    "sf": "49ers",
    "tb": "buccaneers",
    "ten": "titans",
    "was": "commanders",
    "hst": "texans",
    "arz": "cardinals",
    "blt": "ravens",
    "clv": "browns",
    "oak": "raiders",
    "sdc": "chargers",
    "stl": "rams",
    "uns": np.nan,
}


class PlayerData(BaseModel):
    season: int
    team: str
    position: str
    depth_chart_position: str
    jersey_number: int | None
    status: str
    player_name: str
    first_name: str
    last_name: str
    birth_date: datetime | None = Field(None, example="1982-05-05")
    height: int | None
    weight: int | None
    college: str | None
    player_id: str | int | None
    espn_id: int | None
    sportradar_id: str | None
    yahoo_id: str | None
    rotowire_id: str | None
    pff_id: str | None
    pfr_id: str | None
    fantasy_data_id: str | None
    sleeper_id: str | None
    years_exp: int
    headshot_url: str | None
    ngs_position: str | None
    week: int
    game_type: str
    status_description_abbr: str
    football_name: str
    esb_id: str | None
    gsis_it_id: str | None
    smart_id: str | None
    entry_year: int | None
    rookie_year: int | None
    draft_club: str | None
    draft_number: float | None
    age: float | None

    class Config:
        use_enum_values = True
        from_attributes = True
        json_schema_extra = {
            "example": {
                "season": 2023,
                "team": "PHI",
                "position": "OL",
                "depth_chart_position": "T",
                "jersey_number": 74.0,
                "status": "CUT",
                "player_name": "Bernard Williams",
                "first_name": "Bernard",
                "last_name": "Williams",
                "birth_date": None,
                "height": 80.0,
                "weight": 286,
                "college": None,
                "player_id": "00-0017724",
                "espn_id": None,
                "sportradar_id": None,
                "yahoo_id": None,
                "rotowire_id": None,
                "pff_id": None,
                "pfr_id": None,
                "fantasy_data_id": None,
                "sleeper_id": None,
                "years_exp": 29,
                "headshot_url": None,
                "ngs_position": None,
                "week": 11,
                "game_type": "REG",
                "status_description_abbr": "W03",
                "football_name": "Bernard",
                "esb_id": "WIL148626",
                "gsis_it_id": "17623",
                "smart_id": "32005749-4c14-8626-f883-08eba7248da6",
                "entry_year": 1994,
                "rookie_year": 1994.0,
                "draft_club": "PHI",
                "draft_number": 14.0,
                "age": None,
            }
        }


@task
def get_data(years: list):
    years = years or [2023]
    return nfl.import_weekly_rosters(years)


@task
def hash_and_compare(df, directory: str = None, prefix: str = None, suffix: str = None):
    # Convert DataFrame to a consistent string format for hashing
    if isinstance(df, pd.DataFrame):
        current_hash = pd.util.hash_pandas_object(
            pd.util.hash_pandas_object(df).to_frame().T
        )
        current_hash = str(current_hash.sum())
    elif isinstance(df, pd.Series):
        current_hash = pd.util.hash_pandas_object(df.to_frame().T)
        current_hash = str(current_hash.sum())
    else:
        df_string = df.to_string()
        current_hash = hashlib.sha256(df_string.encode()).hexdigest()

    # Load the previous hash
    directory = directory or tempfile.gettempdir()
    hash_file = f"{directory}/{prefix}_data_hash_{suffix}.txt"
    if os.path.exists(hash_file):
        with open(hash_file) as f:
            previous_hash = f.read()
    else:
        previous_hash = None

    # Store the current hash for next time
    with open(hash_file, "w") as f:
        f.write(current_hash)

    return current_hash != previous_hash


@task
def difference_rows(df, previous_df):
    return df.compare(previous_df) if previous_df is not None else df


@task
def dataframe_to_pydantic(df):
    # Build this function to convert the DataFrame to Pydantic models
    for m in df.to_dict(orient="records"):
        m = {k: v if pd.notnull(v) else None for k, v in m.items()}
        yield PlayerData(**m)


@task
def db_linking(df):
    # Link to the database
    return df


@task
def entity_linking(models, schema: dict):
    # Logic to determine which tables to update and whether to insert or update records
    pass


@task
def upsert_to_db(entities):
    # Logic to insert or update records in the database
    pass


def get_field_level_metadata(df):
    return pd.DataFrame(
        [
            pd.Series(df.nunique().to_dict(), name="unique"),
            pd.Series(df.isnull().sum(axis=0).to_dict(), name="nulls"),
            pd.Series(df.dtypes.to_dict(), name="dtype"),
        ]
    )


@flow(name="NFL Data ETL")
def main_flow():
    df = get_data(years=[2023])

    # Load the previous hash
    directory = tempfile.gettempdir()
    prefix = "nfl_roster"
    suffix = "task"

    hash_and_compare(df, directory, prefix, suffix)
    # if not has_changed:
    #     return

    last_file = f"{directory}/{prefix}_data_hash_{suffix}.parquet"
    previous_df = pd.read_parquet(last_file) if os.path.exists(last_file) else None
    changes = difference_rows(df, previous_df)
    models = list(dataframe_to_pydantic(changes))

    with open("nfl_roster.jsonl", "w") as f:
        for m in models:
            f.write(m.model_dump_json(exclude_none=True) + "\n")

    schema_match = db_linking(models)
    entities = entity_linking(models, schema=schema_match)
    upsert_to_db(entities)

    # weekly_roster = nfl.import_weekly_rosters([2023])
    # weekly_roster["player_name"] = weekly_roster["player_name"].map(clean_player_names)
    # weekly_roster["team"] = weekly_roster.map(team_abbr_to_mascot_map)


def get_property_distributions(models: list[PlayerData]):
    for key, value in PlayerData.model_json_schema()["properties"].items():
        # uniques, data_type, is_optional, nulls
        # Determine the min, max, median, and mean for numeric columns and the value counts for categorical columns
        values = [getattr(m, key) for m in models]
        not_null_values = np.array([v for v in values if v is not None])
        uniques = set(values)
        # TODO confirm if floats can be integers
        # TODO confirm if is_optional is correct
        meta = {
            "count": len(values),
            "uniques": len(uniques),
            "data_type": {str(t.get("type")) for t in value["anyOf"]},
            "is_optional": value.get("nullable", False),
            "nulls": len(values) - len(not_null_values),
            "examples": pd.Series(not_null_values)
            .value_counts()
            .head(10)
            .index.tolist(),
        }
        values["distribution"] = {
            "value_counts": pd.Series(values).value_counts(),
            "mean": np.mean(not_null_values),
            "median": np.median(not_null_values),
            "max": max(not_null_values),
            "min": min(not_null_values),
        }

        for m in models:
            getattr(m, key)
        if isinstance(PlayerData.schema.properties[key], BaseModel):
            yield key, pd.Series([getattr(m, key) for m in models])
        else:
            yield key, pd.Series([getattr(m, key) for m in models]).value_counts()
    models


if __name__ == "__main__":
    # Execute the flow
    main_flow()
