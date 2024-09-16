import asyncio
import contextlib
import hashlib
import json
from collections import defaultdict
from collections.abc import Callable
from datetime import datetime, timezone
from typing import Any

import matplotlib.colors as mcolors
import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
import pandas as pd
import xgboost as xgb
from cuid2 import cuid_wrapper
from jarowinkler import jarowinkler_similarity
from networkx.drawing.nx_agraph import graphviz_layout
from pydantic import BaseModel
from rapidfuzz import fuzz, process
from tqdm import tqdm

from thecrowdsline_data.prisma.fe_client import Prisma

# Pygraphviz is required for graphviz_layout
# sudo apt-get install graphviz graphviz-dev

# Migrate code from thecrowdsline_data/sources/odds_api_process.py


# Database connection URL
DATABASE_URL = "postgres://chattcl_webapp:61Y1bYvz8IqB8V0@localhost:5433/chattcl_webapp?sslmode=disable"


cuid_generator: Callable[[], str] = cuid_wrapper()


def format_odds(data):
    for game in data:
        game_id = game["id"]
        for book in game["bookmakers"]:
            bookmaker = book["title"]
            last_update = book["last_update"]
            for market in book["markets"]:
                key = market["key"]
                last_update = market["last_update"]
                for outcome in market["outcomes"]:
                    name, price, point = (
                        outcome.get("name"),
                        outcome.get("price"),
                        outcome.get("point"),
                    )
                    yield game_id, key, bookmaker, last_update, name, price, point


def get_best_match(
    s: str,
    candidates: list[str] | dict[str, str],
    scorer=jarowinkler_similarity,
    score_cutoff=0.5,
):
    if isinstance(candidates, dict):
        choices = list(candidates.keys())
    else:
        choices = list(candidates)
    matches = process.extractOne(s, choices, scorer=scorer, score_cutoff=score_cutoff)
    if matches is None or len(matches) == 0:
        return None
    return candidates[matches[0]] if isinstance(candidates, dict) else matches[0]


def get_top_matches(
    s: str,
    candidates: list[str] | dict[str, str],
    scorer=jarowinkler_similarity,
    score_cutoff=0.0,
    k=10,
):
    if isinstance(candidates, dict):
        choices = list(candidates.keys())
    else:
        choices = list(candidates)
    matches = process.extract(
        s, choices, scorer=scorer, score_cutoff=score_cutoff, limit=k
    )
    if matches is None or len(matches) == 0:
        return None
    if isinstance(candidates, dict):
        return [(candidates[m[0]], *m[1:]) for m in matches]
    return matches


def get_max_elements_by_group(data):
    # Create a dictionary to store the max score for each group
    max_elements = defaultdict(lambda: None)

    for element in data:
        key = element[0]
        score = element[1]

        # Update the dictionary if this is the first occurrence of the key
        # or if the current score is higher than the stored one
        if max_elements[key] is None or score > max_elements[key][1]:
            max_elements[key] = element

    # Return the values of the dictionary as a list
    data = list(max_elements.values())
    return sorted(data, key=lambda x: x[1], reverse=True)


def scorer_exact(s1, s2, **kwargs):
    return float(s1 == s2)


def scorer_difference(s1, s2, **kwargs):
    if isinstance(s1, str) or isinstance(s2, str):
        s1 = pd.to_datetime(s1).replace(tzinfo=timezone.utc)
        s2 = pd.to_datetime(s2).replace(tzinfo=timezone.utc)

    if isinstance(s1, pd.Timestamp):
        s1 = s1.replace(tzinfo=timezone.utc)
    if isinstance(s2, pd.Timestamp):
        s2 = s2.replace(tzinfo=timezone.utc)
    try:
        return float(np.abs(s1 - s2)) * -1
    except (AttributeError, TypeError):
        return float(np.abs((s1 - s2).total_seconds())) * -1


def jarowinkler_similarity_case_insensitive(s1, s2, *args, **kwargs):
    s1 = s1.lower()
    s2 = s2.lower()
    return jarowinkler_similarity(s1, s2, *args, **kwargs)


class DateTimeEncoder(json.JSONEncoder):
    def default(self, obj):
        return obj.isoformat() if isinstance(obj, datetime) else super().default(obj)


def hash_dictionary(d, kind="dict"):
    """
    Hashes an object using json.dumps and SHA256.

    Args:
        d: The dictionary or list to be hashed.
        kind (str, optional): The kind of object being hashed. Defaults to "dict".

    Returns:
        str: The hexadecimal representation of the hash.

    Examples:
        >>> hash_dictionary({"a": 1, "b": 2})
        '1bc9dd4d2f6a2bbc59cdd9cb17e4c518b9049ce4e46d3abb3338332706f2487e'
    """
    serialized_dict = f"{kind}({json.dumps(d, sort_keys=True, cls=DateTimeEncoder)})"
    hash_object = hashlib.sha256()
    hash_object.update(serialized_dict.encode())
    return hash_object.hexdigest()


def _process_object(obj: Any) -> tuple[int, dict, set]:
    """
    Processes the object and returns its hash, simple data, and complex type keys.

    :param obj: The object to process.
    :return: A tuple of (hash of the object, simple data dictionary, set of complex type keys).
    """
    if isinstance(obj, dict):
        items = list(obj.items())
    elif isinstance(obj, BaseModel):
        items = [(k, getattr(obj, k)) for k in obj.__annotations__.keys()]
    else:
        raise TypeError(f"_process_object: Unsupported object type: {type(obj)}: {obj}")

    complex_types = {
        k
        for k, v in items
        if isinstance(v, (dict, BaseModel))
        or (
            isinstance(v, list)
            and len(v) > 0
            and isinstance(v[0], (dict, list, BaseModel))
        )
    }
    data = {k: v for k, v in items if k not in complex_types}
    node_id = hash_dictionary(data, kind=obj.__class__.__name__)
    print(items, data, complex_types, obj.__class__.__name__, obj)
    return node_id, data, complex_types


def object_to_dag(
    obj: Any, graph: nx.DiGraph = None, parent_id=None, parent_edge=None
) -> nx.DiGraph:
    """
    Converts a given object (list, dict, or BaseModel instance) into a directed acyclic graph.

    :param obj: The object to be converted into a DAG.
    :param graph: An existing networkx DiGraph to which the obj will be added. If None, a new graph is created.
    :param parent_id: The ID of the parent node in the graph.
    :param parent_edge: The edge label between the parent and the current node.
    :return: A networkx DiGraph representing the object structure.
    """
    if graph is None:
        graph = nx.DiGraph()

    if obj is None:
        return graph

    if not isinstance(obj, (list, dict, BaseModel)):
        raise TypeError(f"Unsupported object type: {type(obj)}: {obj}")

    if isinstance(obj, list):
        for item in obj:
            object_to_dag(item, graph, parent_id=parent_id, parent_edge=parent_edge)
        return graph

    node_id, data, complex_types = _process_object(obj)
    graph.add_node(node_id, kind=obj.__class__.__name__, data=data)

    if parent_id is not None:
        graph.add_edge(parent_id, node_id, label=parent_edge)

    for key in complex_types:
        object_to_dag(
            obj[key] if isinstance(obj, dict) else getattr(obj, key),
            graph,
            parent_id=node_id,
            parent_edge=key,
        )
    return graph


def draw_schema(g: nx.DiGraph, layout="dot"):
    """
    Draws a graph using matplotlib.

    :param g: The graph to be drawn.
    """
    assert layout in ["dot", "spring"]
    if layout == "dot":
        pos = graphviz_layout(g, prog="dot")  # positions for all nodes using Graphviz
        pos = {k: (-v[1], -v[0]) for k, v in pos.items()}
    else:
        pos = nx.spring_layout(g)

    # nodes
    kinds = list({g.nodes[n]["kind"] for n in g.nodes()})
    cmap = plt.cm.Spectral  # divergent colormap
    norm = mcolors.Normalize(vmin=0, vmax=len(kinds) - 1)  # normalizer for the colormap
    color_map = {
        kind: cmap(norm(i)) for i, kind in enumerate(kinds)
    }  # map kinds to colors
    node_colors = [color_map[g.nodes[n]["kind"]] for n in g.nodes()]
    nx.draw_networkx_nodes(g, pos, node_color=node_colors, node_size=700)

    # edges
    edgelist = g.edges()
    nx.draw_networkx_edges(g, pos, edgelist=edgelist, width=3)

    # labels
    edge_labels = {
        (u, v): ",".join(sorted(data.get("labels", [])))
        for u, v, data in g.edges(data=True)
    }
    nx.draw_networkx_edge_labels(
        g,
        pos,
        edge_labels=edge_labels,
        font_size=8,
        font_family="sans-serif",
        font_color="red",
    )

    node_labels = {
        n: n.split(".")[-1] for n, d in g.nodes(data=True)
    }  # replace with your custom labels
    nx.draw_networkx_labels(
        g, pos, labels=node_labels, font_size=10, font_family="sans-serif"
    )

    plt.axis("off")
    plt.show()


def dag_to_schema(g: nx.DiGraph) -> nx.DiGraph:
    """
    Converts a DAG into a schema graph.

    :param g: The DAG to be converted.
    :return: A schema graph.
    """
    schema = nx.DiGraph()
    for n, node_data in g.nodes(data=True):
        # Match the
        kind = g.nodes[n].get("kind")
        if kind not in schema:
            schema.add_node(
                kind, kind="entity", data_values=set(), data_types=set(), data_count=0
            )

        for field in list(node_data["data"].keys()):
            field_name = f"{kind}.{field}"
            if field_name not in schema:
                schema.add_node(
                    field_name,
                    kind="property",
                    data_values=set(),
                    data_types=set(),
                    data_count=0,
                )
            schema.add_edge(kind, field_name, labels={field})
            with contextlib.suppress(TypeError):  # Ignore unhashable types
                schema.nodes[field_name]["data_values"].add(node_data["data"][field])
            schema.nodes[field_name]["data_types"].add(type(node_data["data"][field]))
            schema.nodes[field_name]["data_count"] += 1

        in_edges = defaultdict(set)
        for src, _, d in g.in_edges(n, data=True):
            in_edges[g.nodes[src]["kind"]].add(d.get("label"))
        out_edges = defaultdict(set)
        for _, dest, d in g.out_edges(n, data=True):
            out_edges[g.nodes[dest]["kind"]].add(d.get("label"))

        for n, labels in in_edges.items():
            if n not in schema:
                schema.add_node(
                    n, kind="entity", data_values=set(), data_types=set(), data_count=0
                )
            schema.add_edge(n, kind, labels=labels)

        for n, labels in out_edges.items():
            if n not in schema:
                schema.add_node(
                    n, kind="entity", data_values=set(), data_types=set(), data_count=0
                )
            schema.add_edge(kind, n, labels=labels)
    return schema


def schema_to_map(g: nx.DiGraph):
    return pd.DataFrame(
        [
            [
                n[0],
                list(n[1].get("data_values")),
                list(n[1].get("data_types")),
                n[1].get("data_count"),
            ]
            for n in g.nodes(data=True)
            if n[1].get("kind") == "property"
        ],
        columns=["property", "values", "types", "count"],
    )


def db_schema_to_map(g: nx.DiGraph):
    return (
        pd.DataFrame(
            [
                {"property": k, "types": v["types"]}
                for k, v in g.nodes(data=True)
                if v.get("kind") == "column"
            ]
        )
        .sort_values("property")
        .reset_index(drop=True)
    )


async def db_to_schema(db: Prisma, include_indexes=False):
    # Step 1: Connect to the database
    await db.connect()
    # Step 2: Query the database schema
    tables = await db.query_raw(
        """SELECT table_name
FROM information_schema.tables
WHERE table_schema = 'public';"""
    )  # Replace with your query to get table info
    columns = await db.query_raw(
        """SELECT table_name, column_name, data_type
FROM information_schema.columns
WHERE table_schema = 'public';
"""
    )  # Replace with your query to get column info
    fks = await db.query_raw(
        """SELECT
    tc.table_name,
    kcu.column_name,
    ccu.table_name AS foreign_table_name,
    ccu.column_name AS foreign_column_name
FROM
    information_schema.table_constraints AS tc
    JOIN information_schema.key_column_usage AS kcu
      ON tc.constraint_name = kcu.constraint_name
      AND tc.table_schema = kcu.table_schema
    JOIN information_schema.constraint_column_usage AS ccu
      ON ccu.constraint_name = tc.constraint_name
      AND ccu.table_schema = tc.table_schema
WHERE tc.constraint_type = 'FOREIGN KEY' AND tc.table_schema = 'public';
"""
    )  # Replace with your query to get FK info
    indexes = []
    if include_indexes:
        indexes = await db.query_raw(
            """SELECT
        t.relname AS table_name,
        i.relname AS index_name,
        a.attname AS column_name
    FROM
        pg_class t,
        pg_class i,
        pg_index ix,
        pg_attribute a
    WHERE
        t.oid = ix.indrelid
        AND i.oid = ix.indexrelid
        AND a.attrelid = t.oid
        AND a.attnum = ANY(ix.indkey)
        AND t.relkind = 'r'
        AND t.relname NOT LIKE 'pg_%';
    """
        )  # Replace with your query to get index info

    # Step 3: Process the query results (simplified example)
    g = nx.DiGraph()

    def invalid_table(table_name):
        return table_name.startswith("pg_") or table_name.startswith("_")

    # Add tables as nodes
    for table in tables:
        if invalid_table(table["table_name"]):
            continue
        g.add_node(table["table_name"], kind="table")

    # Add columns as nodes and create edges from tables to columns
    for column in columns:
        if invalid_table(column["table_name"]):
            continue
        name = f"{column['table_name']}.{column['column_name']}"
        g.add_node(name, kind="column", types=[column["data_type"]])
        g.add_edge(column["table_name"], name)

    # Add foreign key relationships
    for fk in fks:
        if invalid_table(fk["table_name"]) or invalid_table(fk["foreign_table_name"]):
            continue
        src_name = f"{fk['table_name']}.{fk['column_name']}"
        dest_name = f"{fk['foreign_table_name']}.{fk['foreign_column_name']}"
        g.add_edge(src_name, dest_name, kind="foreign_key")

    # Add indexes as nodes and create edges
    for index in indexes:
        if invalid_table(index["table_name"]):
            continue
        name = f"{index['table_name']}.{index['column_name']}"
        g.add_node(index["index_name"], kind="index")
        g.add_edge(name, index["index_name"])

    # Disconnect from the database
    await db.disconnect()
    return g


def empirical_cdf(data):
    """
    Create an empirical CDF function for the given data.

    :param data: Array-like, input data for which the empirical CDF is calculated.
    :return: A function that takes a value and returns its empirical CDF value.
    """
    # Sort data
    sorted_data = np.sort(data)
    # Calculate CDF values
    cdf_values = np.arange(1, len(sorted_data) + 1) / len(sorted_data)

    def cdf_func(x):
        # Return CDF value for x
        return np.interp(x, sorted_data, cdf_values, left=0, right=1)

    return cdf_func


async def sample_db_random_data(table: str, column: str, db: Prisma, n=1000):
    table = table.replace('"', "").replace(";", "")
    column = column.replace('"', "").replace(";", "")

    return await db.query_raw(
        f'SELECT "{column}" FROM "{table}" ORDER BY RANDOM() LIMIT {int(n)};'
    )


async def sample_db(table_columns: list[tuple[str, str]], db: Prisma, n=1000):
    # Step 1: Connect to the database
    await db.connect()

    # TODO Run data sampling in parallel for each table-column pair
    # sample_tasks = [
    #     sample_db_random_data(t, c, db, n=n) for t, c in table_columns
    # ]
    # results = await asyncio.gather(*sample_tasks)

    samples = []
    for t, c in tqdm(table_columns, desc="Sampling db tables"):
        d = await sample_db_random_data(t, c, db, n=n)
        samples.append(pd.DataFrame(d).rename(columns={c: f"{t}.{c}"}))
    samples = pd.concat(samples, axis=1)

    # Creating DataFrames for each result and concatenating them
    # samples = pd.concat(
    #     [pd.DataFrame(result, columns=[f"{t}.{c}"]) for result, (t, c) in zip(results, table_columns)],
    #     axis=1,
    # )

    await db.disconnect()
    return samples


def schemas_distances_by_names(
    obj_schema: nx.DiGraph, db_schema: nx.DiGraph
) -> pd.DataFrame:
    db_columns = [
        n2 for n2, v in db_schema.nodes(data=True) if v.get("kind") == "column"
    ]
    properties = [
        n for n, v in obj_schema.nodes(data=True) if v.get("kind") == "property"
    ]

    distance_metrics = [
        ("jarowinkler_similarity", jarowinkler_similarity),
        (
            "jarowinkler_similarity_case_insensitive",
            jarowinkler_similarity_case_insensitive,
        ),
        ("fuzz.WRatio", fuzz.WRatio),
        ("fuzz.token_set_ratio", fuzz.token_set_ratio),
        ("fuzz.token_sort_ratio", fuzz.token_sort_ratio),
        ("fuzz.partial_ratio", fuzz.partial_ratio),
        ("fuzz.partial_token_set_ratio", fuzz.partial_token_set_ratio),
        ("fuzz.partial_token_sort_ratio", fuzz.partial_token_sort_ratio),
    ]
    metrics = [
        ("NodeNames", None),
        ("TableNames", lambda x: x.split(".")[0]),
        ("FieldVsColumnNames", lambda x: x.split(".")[1]),
    ]

    # TODO compare datatypes with a manual mapping
    results = []
    for name, processor in tqdm(metrics):
        for metric_name, scorer in distance_metrics:
            df = pd.DataFrame(
                process.cdist(
                    db_columns,
                    properties,
                    scorer=scorer,
                    workers=-1,
                    processor=processor,
                ),
                index=pd.Index(db_columns, name="column"),
                columns=pd.Index(properties, name="property"),
            )

            cdf_func = empirical_cdf(df.values.flatten())
            df = df.map(cdf_func).stack()
            df.name = (name, metric_name)
            results.append(df)

    results = pd.concat(results, axis=1)
    results.index = results.index.swaplevel("property", "column")
    return results


def schemas_distances_by_dtypes(obj_schema: nx.DiGraph, db_schema: nx.DiGraph):
    raise NotImplementedError()


async def schemas_distances_by_values(
    obj_schema: nx.DiGraph, db_schema: nx.DiGraph, db: Prisma
):
    """
    # Get schema values
    # Get database values
    # Use jacard similarity to get the distance between the two
    # Also use isin metric
    # Also get maximum fuzzy match
    # Load in sample data
    # merge all results into an n*m x k dataframe where n is the number of properties, m is the number of columns, and k is the number of metrics
    """
    db_columns = [
        n2 for n2, v in db_schema.nodes(data=True) if v.get("kind") == "column"
    ]
    properties = [
        n for n, v in obj_schema.nodes(data=True) if v.get("kind") == "property"
    ]

    table_columns = [(n.split(".")[0], n.split(".")[1]) for n in db_columns]
    db_data = await sample_db(table_columns, db, n=1000)
    if len(db_data) == 0:
        return None

    results = {}
    for p in tqdm(properties, desc="Comparing property values"):
        obj_values = obj_schema.nodes[p].get("data_values")
        if len(obj_values) == 0:
            continue
        for c in db_data.columns:
            db_values = db_data.loc[:, c].dropna()
            if len(db_values) == 0:
                continue
            if isinstance(db_values.iloc[0], list):
                db_values = db_values.explode()
            results[(p, c, "jaccard")] = len(
                set(db_values).intersection(obj_values)
            ) / len(set(db_values).union(obj_values))
            results[(p, c, "isin")] = db_values.isin(obj_values).any() * 1
            results[(p, c, "fuzzy")] = process.cdist(
                db_values.astype(str),
                pd.Series(list(obj_values)).astype(str),
                workers=-1,
                score_multiplier=0.01,
            ).max()

            with contextlib.suppress(ValueError):
                obs = pd.Series(list(obj_values)).copy()
                if ("date" in str(obs.dtype)) or ("time" in str(obs.dtype)):
                    obs = (obs.astype("int64") // 10**9).astype(float)
                else:
                    obs = obs.astype(float)

                vals = db_values.copy()
                if ("date" in str(obs.dtype)) or ("time" in str(obs.dtype)):
                    vals = (vals.astype("int64") // 10**9).astype(float)
                else:
                    vals = vals.astype(float)

                def abs_diff(x, y, **kwargs):
                    return -1 * np.abs(x - y)

                diffs = process.cdist(
                    obs,
                    vals,
                    scorer=abs_diff,
                    workers=-1,
                )
                norm_factor = 1 / (
                    1 / max(1e-6, np.var(vals)) + 1 / max(1e-6, np.var(obs))
                )
                norm_factor = max(
                    1e-12, norm_factor if np.isfinite(norm_factor) else 1.0
                )
                results[(p, c, "numerical")] = (
                    np.clip(100 * diffs.max() / norm_factor + 100, 0, 100) / 100.0
                )

    results = pd.Series(results).unstack().astype(float)
    results.index.names = ["property", "column"]
    results.columns = pd.MultiIndex.from_product(
        [["DataValues"], list(results.columns)]
    )
    return results


async def schemas_distances(
    obj_schema: nx.DiGraph, db_schema: nx.DiGraph, db: Prisma = None
) -> [pd.DataFrame, pd.DataFrame]:
    """Measures the distances between propery nodes in the object schema and columns in the database schema
    across several metrics

    Returns a dictionary of distance matrices (rows are object properties, columns are database columns)
    """
    nx.Graph()

    d1 = schemas_distances_by_names(obj_schema, db_schema)
    # d2 = schemas_distances_by_dtypes(obj_schema, db_schema)
    d3 = await schemas_distances_by_values(obj_schema, db_schema, db=db)

    scores = d3.join(d1, how="outer")
    scores.sort_index(inplace=True)

    # Find Greedy matching starting with the highest scores on 'DataValues'
    perfect_matches = scores.index[scores["DataValues"].median(axis=1) > 0.99]
    # Positive examples
    y = pd.Series(1, index=perfect_matches)

    matched_properties = perfect_matches.get_level_values("property").unique()
    matched_edges = set(perfect_matches.to_list())
    # Negative examples
    perfect_negative_matches = pd.MultiIndex.from_frame(
        pd.DataFrame(
            [
                (p, c)
                for p, c in scores.index.to_list()
                if p in matched_properties and (p, c) not in matched_edges
            ],
            columns=["property", "column"],
        )
    )

    y = pd.concat(
        [
            pd.Series(1, index=perfect_matches, name="y"),
            pd.Series(0, index=perfect_negative_matches, name="y"),
        ],
        axis=0,
    )
    x = scores.reindex(y.index).fillna(0).copy(deep=True)

    # TODO perhaps Kill the best feature(s)?
    # In the future, remove the best feature or all of x['DataValues']
    #  and see if the model still works

    # Convert the DataFrame and Series into DMatrix, which is an internal data structure that XGBoost uses
    dtrain = xgb.DMatrix(x, label=y)
    # d_os = xgb.DMatrix(x_os)
    d_all = xgb.DMatrix(scores.fillna(0))

    # Set up parameters for XGBoost
    params = {
        "objective": "binary:logistic",  # binary classification
        "max_depth": 3,  # can be tuned
        "learning_rate": 0.1,  # can be tuned
        "n_estimators": 100,  # can be tuned
    }

    # Train the model
    bst = xgb.train(params, dtrain, num_boost_round=10)  # num_boost_round can be tuned
    y_fcast = pd.Series(bst.predict(d_all), name="y_fcast", index=scores.index)
    # Combine forecasts with positive labels
    fcasts = y_fcast.to_frame().join(y, how="outer").fillna(0).max(axis=1)

    xgb.plot_importance(bst)
    plt.show()
    return fcasts, scores


def connect_schemas(
    obj_schema: nx.DiGraph,
    db_schema: nx.DiGraph,
    scorer=jarowinkler_similarity_case_insensitive,
    score_cutoff=0.0,
    k=10,
):
    """Generate cannidate connections just based on
    names
    the goal here is high recall, not high precision
    """
    G = nx.Graph()

    candidates = [
        n2 for n2, v in db_schema.nodes(data=True) if v.get("kind") == "column"
    ]
    for n, v in obj_schema.nodes(data=True):
        if v.get("kind") != "property":
            continue
        matches = get_top_matches(
            n, candidates, scorer=scorer, score_cutoff=score_cutoff, k=k
        )
        for m in matches:
            G.add_edge(("obj", n), ("db", m[0]), score=m[1])
    return G


if __name__ == "__main__":
    # Run the async main function
    asyncio.run(db_to_schema())
